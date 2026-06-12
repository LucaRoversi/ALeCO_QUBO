#!/usr/bin/env python3
################################################################################
# SiSi_SiAnn.py
#
# Application entry point for the problem "Subsets with Identical Sum".
#
# Interactive classroom use:
#   python SiSi_SiAnn.py
#
# The script then asks for:
#   - the integer sequence S;
#   - the tuning profile;
#   - an optional random seed;
#   - whether the BQM coefficients should be printed.
#
# Non-interactive command-line use is still available:
#   python SiSi_SiAnn.py 1 3 4 2 6
#   python SiSi_SiAnn.py 1 1 1 1 1 --profile classroom
#   python SiSi_SiAnn.py 12 -3 7 4 2 --profile aggressive --seed 123
#
# This double entry point is useful in two settings:
#   - from an IDE, Spyder, PyCharm, VS Code, or another editor that already uses
#     the correct conda interpreter, one can press "Run" and answer the prompts;
#   - from a shell, one can still pass all parameters explicitly.
#
# The application accepts an arbitrary integer sequence S. It builds the QUBO
# Hamiltonian for Number Partitioning, selects simulated-annealing parameters as
# a function of n = len(S), and searches for a partition T and S \\ T with equal
# sum.
################################################################################

from __future__ import annotations

import argparse
import re
import sys
from typing import Optional, Sequence


PROFILES = ('classroom', 'balanced', 'aggressive')


################################################################################
# Command-line parsing.
################################################################################
def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Translate shell arguments into the internal option object.

    This function is the non-interactive front end of the application.  It lets
    the same solver be used in scripts, terminal experiments, or reproducible
    examples in which the sequence and the tuning profile must be written down
    explicitly.

    The positional arguments are the integer values of S.  The optional
    arguments choose the n-based cost profile, the seed, the parity-filter
    behavior, and the amount of diagnostic output.
    """

    parser = argparse.ArgumentParser(
        prog='SiSi_SiAnn.py',
        description='Size-tuned simulated annealing for Subsets with Identical Sum.',
    )
    parser.add_argument(
        'values',
        metavar='v',
        type=int,
        nargs='*',
        help='integer values v_1 ... v_n of the sequence S',
    )
    parser.add_argument(
        '--profile',
        choices=PROFILES,
        default='balanced',
        help='n-based annealing cost profile; default: balanced',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='optional random seed for reproducible heuristic runs',
    )
    parser.add_argument(
        '--no-parity-filter',
        action='store_true',
        help='sample even when sum(S) is odd; useful only for demonstrations',
    )
    parser.add_argument(
        '--show-bqm',
        action='store_true',
        help='print the BQM components before the final interpretation',
    )
    return parser.parse_args(argv)


################################################################################
# Interactive prompting.
################################################################################
def parse_integer_sequence(text: str) -> tuple[int, ...]:
    """Parse the sequence S entered at an interactive prompt.

    The classroom entry point should not require students to remember a rigid
    command-line syntax.  For this reason the parser accepts the most common
    ways of writing a finite sequence of integers:

        1 3 4 2 6
        1, 3, 4, 2, 6
        (1, 3, 4, 2, 6)
        [1, 3, 4, 2, 6]

    The function still rejects decimal numbers and other tokens.  The QUBO used
    in these notes represents the integer version of the problem, so accepting
    floats would make the mathematical interpretation less clear.
    """

    cleaned = text.strip()
    if not cleaned:
        raise ValueError('the sequence cannot be empty')

    cleaned = cleaned.strip('()[]{}')
    tokens = [token for token in re.split(r'[\s,;]+', cleaned) if token]
    if not tokens:
        raise ValueError('the sequence cannot be empty')

    values = []
    for token in tokens:
        if not re.fullmatch(r'[+-]?\d+', token):
            raise ValueError(f'{token!r} is not an integer')
        values.append(int(token))

    return tuple(values)


def prompt_integer_sequence() -> tuple[int, ...]:
    """Ask for S and repeat the question until the input is valid.

    This function is deliberately small and pedagogical.  It separates the
    user-interface loop from parse_integer_sequence(), so that the validation
    rule can also be tested or reused without interactive input.
    """

    while True:
        text = input('Enter the sequence S of integer values: ')
        try:
            return parse_integer_sequence(text)
        except ValueError as error:
            print(f'  Invalid sequence: {error}.')
            print('  Example: 1 3 4 2 6')


def prompt_profile(default: str = 'balanced') -> str:
    """Ask which n-based tuning profile must be used.

    The profile is the classroom-visible way to choose a computational budget.
    The user chooses among names, while sisi_tuning.py translates the chosen name
    and n = len(S) into concrete values for num_reads and num_sweeps.
    """

    print('\nChoose the n-based tuning profile:')
    print('  1. classroom   low cost, compact output')
    print('  2. balanced    default compromise')
    print('  3. aggressive  higher-cost heuristic run')

    choices = {
        '1': 'classroom',
        '2': 'balanced',
        '3': 'aggressive',
        'c': 'classroom',
        'classroom': 'classroom',
        'b': 'balanced',
        'balanced': 'balanced',
        'a': 'aggressive',
        'aggressive': 'aggressive',
    }

    while True:
        text = input(f'Profile [default: {default}]: ').strip().lower()
        if not text:
            return default
        if text in choices:
            return choices[text]
        print('  Invalid profile. Use 1, 2, 3, or classroom/balanced/aggressive.')


def prompt_optional_seed() -> Optional[int]:
    """Ask for an optional random seed.

    Simulated annealing is stochastic.  A seed makes a classroom experiment
    reproducible: the same interpreter, libraries, input sequence, profile, and
    seed should reproduce the same pseudo-random choices.  Empty input keeps the
    run stochastic.
    """

    while True:
        text = input('\nRandom seed [empty: no fixed seed]: ').strip()
        if not text:
            return None
        if re.fullmatch(r'[+-]?\d+', text):
            return int(text)
        print('  Invalid seed. Enter an integer, or leave the field empty.')


def prompt_yes_no(question: str, default: bool = False) -> bool:
    """Ask a yes/no question and return a Boolean answer.

    The function is used for optional diagnostic output.  It keeps the wording
    of prompts consistent and avoids mixing input validation with the main
    control flow.
    """

    suffix = '[Y/n]' if default else '[y/N]'
    while True:
        text = input(f'{question} {suffix}: ').strip().lower()
        if not text:
            return default
        if text in ('y', 'yes'):
            return True
        if text in ('n', 'no'):
            return False
        print('  Please answer y or n.')


def interactive_args() -> argparse.Namespace:
    """Collect the same options as parse_args(), but through prompts.

    The returned object has the same attributes as argparse.Namespace produced
    by the command-line parser.  This is the small design choice that makes the
    rest of the program independent of how the input was obtained.
    """

    print('## SiSi_SiAnn interactive mode')
    print('## Subsets with Identical Sum by simulated annealing')
    print()

    values = prompt_integer_sequence()
    profile = prompt_profile(default='balanced')
    seed = prompt_optional_seed()
    show_bqm = prompt_yes_no('\nShow the BQM coefficients before the result?', default=False)

    # The parity filter is mathematically sound and avoids wasting annealing work
    # when sum(S) is odd.  We keep it enabled in the interactive classroom mode.
    return argparse.Namespace(
        values=values,
        profile=profile,
        seed=seed,
        no_parity_filter=False,
        show_bqm=show_bqm,
    )


################################################################################
# Printing.
################################################################################
def print_bqm_components(result) -> None:
    """Print the BQM coefficients used by the Ocean sampler.

    This is diagnostic output for teaching.  The diagonal coefficients are the
    linear terms of the BQM; the off-diagonal coefficients are the quadratic
    interactions; the offset is the constant V ** 2 from the expanded
    Hamiltonian.
    """

    bqm = result.model.bqm
    print('\n--- Binary Quadratic Model exported to Ocean/dimod ---')
    print('bqm:')
    print(bqm)
    print('\n -- bqm.linear, diagonal QUBO coefficients Q_ii:')
    print(dict(sorted(bqm.linear.items(), key=lambda item: item[0])))
    print('\n -- bqm.quadratic, off-diagonal QUBO coefficients Q_ij:')
    print(dict(sorted(bqm.quadratic.items(), key=lambda item: (item[0][0], item[0][1]))))
    print('\n -- bqm.offset, constant term V^2:')
    print(bqm.offset)


def print_result(result, show_bqm: bool = False) -> None:
    """Print the mathematical interpretation of one solver run.

    The solver returns Python data structures.  This function translates them
    into the language used in the notes: the sequence S, the chosen tuning
    profile, the best binary assignment, the two induced parts T and S \\ T, and
    the gap between their sums.
    """

    model = result.model
    parameters = result.parameters

    print('\n## "Number Partitioning" / "Subsets with Identical Sum"')
    print('## Size-tuned heuristic sampling through neal.SimulatedAnnealingSampler')
    print()
    print(f'Indexed collection S = {model.values}')
    print(f'n = {model.n}')
    print(f'Total weight V = {model.total}')
    print()
    print('Annealing parameters selected from n only:')
    print(f'  profile         = {parameters.profile}')
    print(f'  num_reads       = {parameters.num_reads}')
    print(f'  num_sweeps      = {parameters.num_sweeps}')
    print(f'  reads_per_batch = {parameters.reads_per_batch}')
    print(f'  max work        = {parameters.annealing_work} read-sweeps')
    print(f'  max updates     = {model.n * parameters.annealing_work} variable updates')

    if show_bqm:
        print_bqm_components(result)

    print('\n--- Best-state interpretation ---')

    if result.proven_impossible_by_parity:
        print('No simulated-annealing run was needed.')
        print('Reason: sum(S) is odd, hence two integer sums cannot be equal.')
        return

    answer = result.best_answer
    if answer is None:
        print('No sample was produced.')
        return

    print(f'Reads used       = {result.reads_used}')
    print(f'Batches used     = {result.batches_used}')
    print(f'Work used        = {result.annealing_work_used} read-sweeps')
    print(f'Variable updates = {result.variable_updates_used}')
    print()
    print(f'Best sample x    = {answer.sample}')
    print(f'Best energy H    = {answer.energy}')
    print(f'Gap              = |sum(T) - sum(S \\ T)| = {answer.gap}')
    print(f'T                = {answer.selected_values}, sum(T) = {answer.selected_sum}')
    print(
        f'S \\ T            = {answer.complement_values}, '
        f'sum(S \\ T) = {answer.complement_sum}'
    )

    if answer.exact_partition_found:
        print('Interpretation: this run found an exact partition.')
    else:
        print('Interpretation: this run did not find a zero-energy state.')
        print('Because simulated annealing is heuristic, this is not a proof of absence.')


################################################################################
# Main control.
################################################################################
def main(argv: Sequence[str]) -> int:
    """Run the application and return a shell-style exit code.

    The function first decides whether the run is command-line based or
    interactive.  It then imports the Ocean-dependent solver only after the
    prompts have completed.  This late import makes the error message clearer
    when the file is executed with an interpreter that does not contain dimod and
    neal.
    """

    if argv:
        args = parse_args(argv)
    else:
        args = interactive_args()

    try:
        # Import the Ocean-dependent solver only after the prompts have been
        # completed.  This keeps the entry point readable and gives a clearer
        # message when the file is accidentally run with the wrong interpreter.
        from sisi_solver import solve_sisi_instance

        result = solve_sisi_instance(
            args.values,
            profile=args.profile,
            seed=args.seed,
            use_parity_filter=not args.no_parity_filter,
        )
    except ModuleNotFoundError as error:
        print(f'Error: missing Python package {error.name!r}.', file=sys.stderr)
        print(
            'Run this file with the conda environment that contains dimod and neal, '
            'or select that interpreter in your IDE.',
            file=sys.stderr,
        )
        return 2
    except Exception as error:  # keep the CLI readable for classroom use
        print(f'Error: {error}', file=sys.stderr)
        return 2

    print_result(result, show_bqm=args.show_bqm)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
