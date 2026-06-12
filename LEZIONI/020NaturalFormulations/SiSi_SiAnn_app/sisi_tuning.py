################################################################################
# sisi_tuning.py
#
# Size-based tuning rules for the SiSi_SiAnn application.
#
# The original classroom script NumberPartitioning_SiAnn.py used fixed values
#
#     num_reads  = 10
#     num_sweeps = 10
#
# because the two examples had only five binary variables.  An application that
# accepts an arbitrary sequence S = (v_1, ..., v_n) must choose these parameters
# from n.  This module keeps that choice explicit and reproducible.
#
# Important limitation:
#   No formula depending only on n can be optimal for every Number Partitioning
#   instance.  The actual difficulty also depends on the values in S.  Therefore
#   the rules below are not a proof of optimality.  They are cost profiles:
#   deterministic policies that allocate a bounded annealing budget as n grows.
################################################################################

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, log2, sqrt


@dataclass(frozen=True)
class AnnealingParameters:
    """Parameters passed to neal.SimulatedAnnealingSampler.sample().

    num_reads:
        Total number of independent annealing attempts allowed by the selected
        profile.  Increasing it broadens the search because the sampler starts
        from more independent configurations.

    num_sweeps:
        Number of sweeps in each attempt.  Increasing it deepens each attempt
        because the sampler has more time to relax along its annealing schedule.

    reads_per_batch:
        The application runs the reads in batches.  After each batch it checks
        whether a zero-energy partition has already been found.  This can save
        work on satisfiable instances without changing the n-based parameter
        rule.

    profile:
        Name of the selected cost profile.
    """

    num_reads: int
    num_sweeps: int
    reads_per_batch: int
    profile: str

    @property
    def max_batches(self) -> int:
        """Return the maximum number of batches used by the solver.

        This is a reporting quantity.  The solver may use fewer batches if it
        finds a zero-energy state before spending the full n-based budget.
        """

        return ceil(self.num_reads / self.reads_per_batch)

    @property
    def annealing_work(self) -> int:
        """Return num_reads * num_sweeps.

        This is the first-order cost indicator explained in the classroom
        script.  A more faithful implementation-level estimate multiplies this
        quantity by n, because a sweep visits the variables of the BQM.
        """

        return self.num_reads * self.num_sweeps


def _round_up(value: float, step: int) -> int:
    """Round value up to the next positive multiple of step.

    The tuning formulas produce real numbers.  The sampler expects integer
    counts.  Rounding to multiples such as 5, 10, or 20 keeps the printed
    parameters easy to read in classroom transcripts.
    """

    return max(step, int(ceil(value / step) * step))


def tune_annealing_parameters(n: int, profile: str = 'balanced') -> AnnealingParameters:
    """Return simulated-annealing parameters determined only by n.

    The profiles express three different teaching/application choices:

      - classroom: small output and low cost;
      - balanced: default compromise between exploration and relaxation;
      - aggressive: higher cost, useful when one wants a stronger heuristic run.

    The same n always gives the same parameters.  No value from S is inspected in
    this function.  This is intentional: the module demonstrates what a pure
    size-based tuning rule can and cannot do.
    """

    if n < 0:
        raise ValueError('n must be non-negative')

    # Empty instances are not meaningful for the classroom problem, but using an
    # effective size of one keeps the formulas well-defined if such an instance
    # is passed programmatically.
    effective_n = max(1, n)
    log_factor = max(1.0, log2(effective_n + 1))

    if profile == 'classroom':
        # Keep the transcript short.  This is enough for tiny examples, but it
        # is not meant as a serious search policy for larger instances.
        num_reads = _round_up(2 * sqrt(effective_n) + 8, 5)
        num_sweeps = _round_up(8 * effective_n * log_factor + 20, 10)
        reads_per_batch = min(num_reads, 10)

    elif profile == 'balanced':
        # Default policy.  Reads grow roughly linearly in n, while sweeps grow as
        # n log n.  The product gives a modest polynomial budget.
        num_reads = _round_up(6 * effective_n + 20, 10)
        num_sweeps = _round_up(20 * effective_n * log_factor + 50, 10)
        reads_per_batch = min(num_reads, max(10, _round_up(num_reads / 5, 10)))

    elif profile == 'aggressive':
        # Spend more work in both directions while keeping the rule n-based.
        # This is useful for demonstrations in which one wants a stronger
        # heuristic attempt without manually tuning low-level sampler options.
        num_reads = _round_up(16 * effective_n + 50, 10)
        num_sweeps = _round_up(50 * effective_n * log_factor + 100, 10)
        reads_per_batch = min(num_reads, max(20, _round_up(num_reads / 8, 10)))

    else:
        raise ValueError(
            "unknown profile: expected 'classroom', 'balanced', or 'aggressive'"
        )

    return AnnealingParameters(
        num_reads=num_reads,
        num_sweeps=num_sweeps,
        reads_per_batch=reads_per_batch,
        profile=profile,
    )
