################################################################################
# Max2SAT_ExSolSiAnn(1).py
#
# Classroom companion for the MAX-2-SAT-to-QUBO example in the teaching notes.
#
# Mathematical problem:
#   f = [x] AND [not y] AND [z] AND [not x OR y]
#       AND [not x OR not z] AND [not y OR not z].
#
# The six clause-penalties sum to the quadratic pseudo-Boolean function
#
#   Q(x,y,z) = 2 + y - z - x*y + x*z + y*z.
#
# For every binary assignment, Q is the number of falsified clauses.  Therefore
# minimizing Q is equivalent to maximizing the number of satisfied clauses.
# The optimum is Q = 1, attained at (x,y,z) = (0,0,1), where five clauses are
# satisfied.
#
# Software roles:
#   pyqubo is the modelling layer.  Binary('x'), Binary('y'), and Binary('z')
#   are symbolic variables used to write the mathematical objective.  The call
#   to compile() prepares that objective for export to an Ocean-compatible BQM
#   and also provides the decoding mechanism.
#
#   dimod provides the Binary Quadratic Model and ExactSolver.  ExactSolver is
#   a transparent reference sampler for this small example: it enumerates all
#   2^3 binary assignments and therefore identifies the global minimum.
#
#   neal provides SimulatedAnnealingSampler.  This is a classical heuristic
#   sampler.  It searches for low-energy states, but it does not prove that the
#   best state found is globally optimal.
################################################################################

from dimod import ExactSolver
from neal import SimulatedAnnealingSampler
from pyqubo import Binary


print('## MAX-2-SAT to QUBO')
print('## Exact enumeration and simulated annealing\n')


################################################################################
# Symbolic variables.
#
# These are not numerical values yet.  They are pyqubo symbolic objects.  They
# are placeholders used to build the polynomial corresponding to the MAX-2-SAT
# instance.  A sampler will assign the numerical values 0 or 1 only later.
#
# `variables` is an ordered tuple used by functions that manipulate the model.
# `variable_names` is the corresponding tuple of strings used when a dimod
# SampleSet is decoded and printed.  Keeping the order explicit makes the
# printed tuple `(x,y,z)` agree with the mathematical notation in the notes.
################################################################################
x, y, z = Binary('x'), Binary('y'), Binary('z')
variables = (x, y, z)
variable_names = ('x', 'y', 'z')


# Parameters for the heuristic experiment.  The instance is deliberately tiny;
# these values keep the output readable while making several stochastic reads.
# `n_reads` is the number of independent annealing attempts.  `sweeps_per_read`
# is the amount of annealing work performed inside each attempt.  They are not
# QUBO variables: they control the heuristic sampler only.
n_reads = 10
sweeps_per_read = 10


################################################################################
# Mathematical model
################################################################################
def build_hamiltonian(variables):
    """Return the pyqubo expression for the MAX-2-SAT QUBO.

    Parameters
    ----------
    variables:
        An ordered tuple `(x, y, z)` of pyqubo Binary objects.  The parameter is
        deliberately passed to the function so that the mathematical expression
        is visibly built from the symbolic variables, rather than from already
        sampled numerical values.

    Returns
    -------
    A symbolic pyqubo expression.  It is not yet a dimod BQM and it has not yet
    been given a numerical assignment.

    The clauses are

        [x], [not y], [z], [not x OR y], [not x OR not z], [not y OR not z].

    Their violation penalties are respectively

        1-x, y, 1-z, x-x*y, x*z, y*z.

    The sum is

        Q = (1-x) + y + (1-z) + (x-x*y) + x*z + y*z
          = 2 + y - z - x*y + x*z + y*z.

    A binary assignment has energy equal to the number of falsified clauses.
    """

    x, y, z = variables
    return 2 + y - z - x * y + x * z + y * z


def sorted_linear_terms(bqm):
    """Return linear BQM coefficients in stable variable-name order.

    Parameters
    ----------
    bqm:
        A dimod BinaryQuadraticModel.  Its `linear` dictionary contains the
        coefficients of the one-variable terms.
    """

    return dict(sorted(bqm.linear.items(), key=lambda item: item[0]))


def sorted_quadratic_terms(bqm):
    """Return quadratic BQM coefficients in stable pair-name order.

    Parameters
    ----------
    bqm:
        A dimod BinaryQuadraticModel.  Its `quadratic` dictionary contains the
        coefficients of products such as `x*y`.
    """

    return dict(
        sorted(
            bqm.quadratic.items(),
            key=lambda item: (item[0][0], item[0][1]),
        )
    )


def print_bqm_components(bqm):
    """Print the components of the Ocean BinaryQuadraticModel.

    Parameters
    ----------
    bqm:
        The dimod BinaryQuadraticModel produced from the compiled pyqubo
        expression.  This is the object actually passed to Ocean samplers.

    Ocean stores an objective of the form

        energy = offset
               + sum_i linear[i] * x_i
               + sum_{i<j} quadratic[i,j] * x_i * x_j.

    The offset is the constant term of the polynomial.  It is important when
    interpreting absolute energies, although it does not change the minimizing
    assignment.
    """

    print('Binary Quadratic Model:')
    print(bqm)
    print('\n-- linear coefficients:')
    print(sorted_linear_terms(bqm))
    print('\n-- quadratic coefficients:')
    print(sorted_quadratic_terms(bqm))
    print('\n-- offset:')
    print(bqm.offset)


def build_compiled_problem():
    """Build, compile, and export the symbolic MAX-2-SAT objective.

    The returned compiled model is retained because it is needed later to
    decode samples using the original symbolic variable names.  The BQM is the
    sampler-facing representation; the compiled model is the pyqubo object
    needed to translate sampler results back to the original model.
    """

    hamiltonian = build_hamiltonian(variables)

    # compile() creates pyqubo's internal model.  It is not a sampler.
    compiled_hamiltonian = hamiltonian.compile()

    # to_bqm() exports the compiled expression in the format expected by
    # dimod samplers, including ExactSolver and simulated annealing.
    bqm = compiled_hamiltonian.to_bqm()
    return compiled_hamiltonian, bqm


################################################################################
# Output and interpretation helpers
################################################################################
def print_sampleset(sampleset, title):
    """Print the raw Ocean SampleSet returned by a sampler.

    Parameters
    ----------
    sampleset:
        A dimod SampleSet containing binary samples, energies, and occurrence
        counts.  ExactSolver returns every configuration; simulated annealing
        returns the configurations observed during its stochastic runs.
    title:
        A heading identifying the sampler that produced the SampleSet.
    """

    print(f'\n--- {title} ---')
    print(sampleset)


def print_decoded_samples(compiled_hamiltonian, sampleset):
    """Decode samples through pyqubo and print the original variables.

    Parameters
    ----------
    compiled_hamiltonian:
        The pyqubo model returned by `hamiltonian.compile()`.  It retains the
        information needed to interpret the sampler output.
    sampleset:
        The dimod SampleSet returned by an exact or heuristic sampler.

    The sampler works with the dimod BQM.  Decoding maps its results back to
    the symbolic model used to write the MAX-2-SAT objective.
    """

    decoded_sampleset = compiled_hamiltonian.decode_sampleset(sampleset)

    print('\n--- Decoded samples ---')
    for decoded_sample in decoded_sampleset:
        sample = decoded_sample.sample
        energy = decoded_sample.energy
        ordered_bits = tuple(sample[name] for name in variable_names)
        print(
            f'  (x,y,z) = {ordered_bits}, '
            f'energy = {energy}, sample = {sample}'
        )


def print_exact_ground_states(sampleset):
    """Interpret the globally minimal states returned by ExactSolver.

    The argument is expected to contain the complete exhaustive result.  Thus
    the first energy in `sampleset.lowest()` is a certified global minimum,
    not merely the best state found during a search.
    """

    ground_sampleset = sampleset.lowest()
    minimum_energy = ground_sampleset.first.energy

    print('\n--- Exact ground-state interpretation ---')
    print(f'Minimum energy: {minimum_energy}')
    print('Ground states:')
    for row in ground_sampleset.data(['sample', 'energy']):
        sample = row.sample
        ordered_bits = tuple(sample[name] for name in variable_names)
        print(f'  (x,y,z) = {ordered_bits}, energy = {row.energy}')

    print(
        'Interpretation: the minimum energy is the number of falsified '
        'clauses.'
    )
    print(
        f'Therefore, the maximum number of satisfied clauses is '
        f'6 - {minimum_energy} = {6 - minimum_energy}.'
    )


def print_best_annealing_states(sampleset):
    """Interpret the best states found by simulated annealing.

    Parameters
    ----------
    sampleset:
        The SampleSet returned by simulated annealing.  Its lowest row is the
        best state found in the chosen stochastic experiment.

    A zero-energy state is a certificate that five or six clauses can be
    satisfied, depending on the instance.  A positive energy returned by this
    heuristic run is not a proof that no lower-energy state exists.
    """

    best_sampleset = sampleset.lowest()
    best_energy = best_sampleset.first.energy

    print('\n--- Simulated-annealing interpretation ---')
    print(f'Best energy found in this run: {best_energy}')
    print('Best states found:')
    for row in best_sampleset.data(['sample', 'energy', 'num_occurrences']):
        sample = row.sample
        ordered_bits = tuple(sample[name] for name in variable_names)
        print(
            f'  (x,y,z) = {ordered_bits}, energy = {row.energy}, '
            f'num_occurrences = {row.num_occurrences}'
        )

    if best_energy == 1:
        print(
            'This run found the known optimum for this instance: one '
            'falsified clause and five satisfied clauses.'
        )
    elif best_energy < 1:
        print('This run found an energy below the expected optimum; inspect the model.')
    else:
        print(
            'This run did not find the known optimum.  Because simulated '
            'annealing is heuristic, this is not a proof of non-optimality.'
        )


def print_annealing_parameters():
    """Explain the global parameters used by the heuristic sampler.

    `n_reads` controls breadth of exploration, while `sweeps_per_read` controls
    the annealing effort within one attempt.  Neither parameter changes the
    QUBO objective itself.
    """

    print('\n--- Simulated-annealing parameters ---')
    print(f'num_reads  = {n_reads}')
    print(f'num_sweeps = {sweeps_per_read}')
    print(
        'More reads provide more independent attempts; more sweeps give each '
        'attempt more time to relax.'
    )


################################################################################
# Solver experiments
################################################################################
def run_exact_solver(compiled_hamiltonian, bqm):
    """Enumerate all binary assignments with dimod.ExactSolver.

    Parameters
    ----------
    compiled_hamiltonian:
        The pyqubo model used for decoding.
    bqm:
        The dimod model sampled by ExactSolver.
    """

    print('\n' + '=' * 78)
    print('Exact solution through exhaustive enumeration')
    print('=' * 78)

    sampler = ExactSolver()
    print('Sampler class: dimod.ExactSolver')
    print('This sampler enumerates all 2^3 binary assignments.')

    sampleset = sampler.sample(bqm)
    print_sampleset(sampleset, 'Raw ExactSolver SampleSet')
    print_decoded_samples(compiled_hamiltonian, sampleset)
    print_exact_ground_states(sampleset)


def run_simulated_annealing(compiled_hamiltonian, bqm):
    """Search for low-energy assignments with simulated annealing.

    Parameters
    ----------
    compiled_hamiltonian:
        The pyqubo model used to decode the returned samples.
    bqm:
        The dimod model passed to the classical heuristic sampler.

    Unlike `run_exact_solver`, this function does not certify that the best
    returned sample is globally optimal.
    """

    print('\n' + '=' * 78)
    print('Heuristic solution through simulated annealing')
    print('=' * 78)

    sampler = SimulatedAnnealingSampler()
    print('Sampler class: neal.SimulatedAnnealingSampler')
    print_annealing_parameters()

    sampleset = sampler.sample(
        bqm,
        num_reads=n_reads,
        num_sweeps=sweeps_per_read,
    )
    print_sampleset(sampleset, 'Raw simulated-annealing SampleSet')
    print_decoded_samples(compiled_hamiltonian, sampleset)
    print_best_annealing_states(sampleset)


################################################################################
# Main classroom experiment
################################################################################
def main():
    """Build the common model and run both solver types.

    The order of the calls mirrors the mathematical and computational pipeline:
    build the symbolic objective, compile it, export a BQM, sample it, decode
    the results, and interpret their energies as clause counts.
    """

    print('\n--- Symbolic MAX-2-SAT objective ---')
    print('Q(x,y,z) = 2 + y - z - x*y + x*z + y*z')
    print(
        'Energy interpretation: energy = number of falsified clauses; '
        'therefore satisfied clauses = 6 - energy.'
    )

    compiled_hamiltonian, bqm = build_compiled_problem()

    print('\n--- BQM exported to Ocean/dimod ---')
    print_bqm_components(bqm)

    run_exact_solver(compiled_hamiltonian, bqm)
    run_simulated_annealing(compiled_hamiltonian, bqm)


if __name__ == '__main__':
    main()
