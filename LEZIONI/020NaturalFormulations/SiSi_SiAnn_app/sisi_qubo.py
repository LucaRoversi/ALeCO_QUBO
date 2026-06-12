################################################################################
# sisi_qubo.py
#
# Direct QUBO/BQM construction for Subsets with Identical Sum, also known here
# as Number Partitioning.
#
# Mathematical instance:
#   S = (v_1, ..., v_n), with integer values.
#
# Binary encoding:
#   x_i = 1  means that position i is put in T;
#   x_i = 0  means that position i is put in S \ T.
#
# Hamiltonian:
#   H(x_1, ..., x_n) = (V - 2 * selected_sum)^2,
#   V = sum_i v_i,
#   selected_sum = sum_i x_i v_i.
#
# Direct BQM coefficients:
#   H = V^2
#       + sum_i (4 v_i^2 - 4 V v_i) x_i
#       + sum_{i<j} 8 v_i v_j x_i x_j.
#
# The original classroom scripts used pyqubo to keep the code close to the
# symbolic Hamiltonian.  In this application the formula has already been
# derived in the notes, so the BQM is built directly with dimod.  This removes
# pyqubo as a runtime dependency while preserving exactly the same QUBO model.
################################################################################

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import dimod


@dataclass(frozen=True)
class SiSiModel:
    """Container for the Ocean representation of one SiSi instance.

    values:
        The frozen integer sequence S = (v_1, ..., v_n).

    variable_names:
        The Ocean variable labels x1, ..., xn.  The i-th name corresponds to the
        i-th position of values, not to a possibly repeated numerical value.

    bqm:
        The dimod BinaryQuadraticModel encoding the Hamiltonian
        (V - 2 * selected_sum) ** 2.
    """

    values: tuple[int, ...]
    variable_names: tuple[str, ...]
    bqm: dimod.BinaryQuadraticModel

    @property
    def n(self) -> int:
        """Return the number of binary variables of the model.

        This is len(S).  The tuning module uses this number, and only this
        number, to select the simulated-annealing budget.
        """

        return len(self.values)

    @property
    def total(self) -> int:
        """Return V, the total sum of the input sequence.

        V is needed both in the QUBO formula and in the parity shortcut: if V is
        odd, two integer parts cannot have identical sums.
        """

        return sum(self.values)


def normalize_values(values: Iterable[int]) -> tuple[int, ...]:
    """Validate and freeze the input sequence as a tuple of integers.

    The application accepts any iterable of integers at the Python level.  This
    function materializes it once, checks that every entry is an integer, and
    returns an immutable tuple so that later code cannot accidentally change the
    instance while the BQM is being interpreted.
    """

    normalized = tuple(values)

    for value in normalized:
        if not isinstance(value, int):
            raise TypeError('all elements of S must be integers')

    return normalized


def make_variable_names(n: int) -> tuple[str, ...]:
    """Return the canonical variable labels x1, ..., xn.

    The labels use 1-based numbering because the notes use positions
    1, ..., n.  The labels are strings because dimod stores variables as
    hashable Python objects and string labels make the printed SampleSet more
    readable in class.
    """

    if n < 0:
        raise ValueError('n must be non-negative')

    return tuple(f'x{i}' for i in range(1, n + 1))


def build_bqm(values: Sequence[int]) -> SiSiModel:
    """Build the BQM for one arbitrary integer sequence S.

    The function is the mathematical core of the application.  It implements the
    expanded Hamiltonian

        V^2
        + sum_i 4 v_i (v_i - V) x_i
        + sum_{i<j} 8 v_i v_j x_i x_j.

    dimod stores the constant term as bqm.offset, the diagonal QUBO coefficients
    as linear terms, and the off-diagonal QUBO coefficients as quadratic
    interactions.
    """

    frozen_values = normalize_values(values)
    total = sum(frozen_values)
    variable_names = make_variable_names(len(frozen_values))

    bqm = dimod.BinaryQuadraticModel.empty(dimod.BINARY)
    bqm.offset = total * total

    # Linear terms: Q_ii = 4 v_i (v_i - V).
    for name, value in zip(variable_names, frozen_values):
        bqm.add_variable(name, 4 * value * value - 4 * total * value)

    # Quadratic terms: Q_ij = 8 v_i v_j for i < j.
    for i, name_i in enumerate(variable_names):
        value_i = frozen_values[i]
        for j in range(i + 1, len(variable_names)):
            name_j = variable_names[j]
            value_j = frozen_values[j]
            bqm.add_interaction(name_i, name_j, 8 * value_i * value_j)

    return SiSiModel(values=frozen_values, variable_names=variable_names, bqm=bqm)


def selected_positions(sample: dict[str, int], variable_names: Sequence[str]) -> tuple[int, ...]:
    """Return the 1-based positions i such that x_i = 1.

    This helper is useful when one wants to report the answer as a subset of
    positions rather than as a tuple of selected values.  Positions are more
    precise than values when S contains repetitions.
    """

    return tuple(index + 1 for index, name in enumerate(variable_names) if sample[name] == 1)


def partition_from_sample(
    values: Sequence[int],
    variable_names: Sequence[str],
    sample: dict[str, int],
) -> tuple[tuple[int, ...], tuple[int, ...], int, int, int]:
    r"""Decode one binary sample as the two parts T and S \ T.

    The sampler returns assignments to x1, ..., xn.  This function translates
    one such assignment back to the original problem:

      - x_i = 1 puts v_i in T;
      - x_i = 0 puts v_i in S \ T.

    It returns selected_values, complement_values, selected_sum,
    complement_sum, and gap = abs(selected_sum - complement_sum).  For this
    Hamiltonian, the mathematical energy is gap ** 2.
    """

    selected = []
    complement = []

    for name, value in zip(variable_names, values):
        if sample[name] == 1:
            selected.append(value)
        else:
            complement.append(value)

    selected_sum = sum(selected)
    complement_sum = sum(complement)
    gap = abs(selected_sum - complement_sum)

    return tuple(selected), tuple(complement), selected_sum, complement_sum, gap
