################################################################################
# sisi_solver.py
#
# Simulated-annealing search for SiSi instances.
#
# The solver uses neal.SimulatedAnnealingSampler on the BQM built in sisi_qubo.py.
# The annealing parameters are supplied by sisi_tuning.py and therefore depend
# only on n = len(S).  The solver then runs the requested reads in batches and
# stops early if a zero-energy partition has already been found.
################################################################################

from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Optional, Sequence

from neal import SimulatedAnnealingSampler

from sisi_qubo import SiSiModel, build_bqm, partition_from_sample
from sisi_tuning import AnnealingParameters, tune_annealing_parameters


@dataclass(frozen=True)
class SiSiAnswer:
    """Decoded form of the best state found by the annealer.

    sample:
        Dictionary assigning 0 or 1 to each variable x1, ..., xn.

    energy:
        Energy reported by the sampler for this assignment.

    num_occurrences:
        Number of times the assignment was observed in the SampleSet row.

    selected_values and complement_values:
        The two parts T and S \\ T induced by the binary assignment.

    selected_sum, complement_sum, and gap:
        Integer quantities used for the final mathematical interpretation.
        The gap is zero exactly when an identical-sum partition has been found.
    """

    sample: dict[str, int]
    energy: float
    num_occurrences: int
    selected_values: tuple[int, ...]
    complement_values: tuple[int, ...]
    selected_sum: int
    complement_sum: int
    gap: int

    @property
    def exact_partition_found(self) -> bool:
        """Return True exactly when the decoded sample solves the SiSi instance.

        The Hamiltonian is the square of the difference between the two sums.
        Therefore gap == 0 is the most transparent mathematical test for an
        exact partition; it avoids relying only on floating-point energy output.
        """

        return self.gap == 0


@dataclass(frozen=True)
class SiSiRunResult:
    """Complete result returned by the application core.

    The entry point prints this object, but does not solve the problem itself.
    Keeping the result in a dataclass separates computation from presentation
    and makes the solver reusable in notebooks or tests.
    """

    model: SiSiModel
    parameters: AnnealingParameters
    best_answer: Optional[SiSiAnswer]
    reads_used: int
    batches_used: int
    proven_impossible_by_parity: bool

    @property
    def annealing_work_used(self) -> int:
        """Return the actual read-sweep work spent by this run.

        This may be smaller than parameters.annealing_work because the batched
        solver stops early once a zero-energy partition has been found.
        """

        return self.reads_used * self.parameters.num_sweeps

    @property
    def variable_updates_used(self) -> int:
        """Return an approximate count of variable-update opportunities.

        Each sweep visits the variables of the BQM.  Multiplying the read-sweep
        work by n gives a simple size-aware cost indicator for printed output.
        """

        return self.model.n * self.annealing_work_used


def _decode_best_answer(model: SiSiModel, sampleset) -> SiSiAnswer:
    """Decode the lowest-energy row of an Ocean SampleSet.

    neal returns a SampleSet, which is an Ocean container.  The application needs
    a problem-level answer.  This helper extracts the best row, translates the
    assignment to the two parts T and S \\ T, and stores both the sampler energy
    and the integer gap between the two sums.
    """

    best_row = sampleset.lowest().first
    sample = dict(best_row.sample)
    selected, complement, selected_sum, complement_sum, gap = partition_from_sample(
        model.values,
        model.variable_names,
        sample,
    )

    # For this Hamiltonian the energy should equal gap ** 2.  The value returned
    # by the sampler is a float, so the gap computed from integers is the safest
    # quantity for the final mathematical interpretation.
    return SiSiAnswer(
        sample=sample,
        energy=float(best_row.energy),
        num_occurrences=int(best_row.num_occurrences),
        selected_values=selected,
        complement_values=complement,
        selected_sum=selected_sum,
        complement_sum=complement_sum,
        gap=gap,
    )


def _better_answer(candidate: SiSiAnswer, current: Optional[SiSiAnswer]) -> SiSiAnswer:
    """Return the better of two decoded answers.

    Lower energy is preferred.  If two answers have numerically equal energy, the
    one observed more often is kept because repeated occurrence is a useful
    heuristic signal in a stochastic sampler.
    """

    if current is None:
        return candidate

    if candidate.energy < current.energy:
        return candidate

    if isclose(candidate.energy, current.energy) and candidate.num_occurrences > current.num_occurrences:
        return candidate

    return current


def solve_sisi_instance(
    values: Sequence[int],
    profile: str = 'balanced',
    seed: Optional[int] = None,
    use_parity_filter: bool = True,
) -> SiSiRunResult:
    """Solve one SiSi instance by size-tuned simulated annealing.

    The function is the application core:

      1. build the BQM for S;
      2. choose num_reads and num_sweeps from n only;
      3. optionally stop immediately if sum(S) is odd;
      4. run neal in batches;
      5. stop early if a zero-energy partition is found;
      6. return a decoded result.

    The optional parity filter is not a tuning rule.  It is a mathematical
    shortcut: if sum(S) is odd, no integer partition can split S into two equal
    sums, so the application can stop before sampling.
    """

    model = build_bqm(values)
    parameters = tune_annealing_parameters(model.n, profile=profile)

    if use_parity_filter and model.total % 2 != 0:
        return SiSiRunResult(
            model=model,
            parameters=parameters,
            best_answer=None,
            reads_used=0,
            batches_used=0,
            proven_impossible_by_parity=True,
        )

    sampler = SimulatedAnnealingSampler()
    best_answer: Optional[SiSiAnswer] = None
    reads_used = 0
    batches_used = 0

    while reads_used < parameters.num_reads:
        remaining_reads = parameters.num_reads - reads_used
        batch_reads = min(parameters.reads_per_batch, remaining_reads)

        sample_kwargs = {
            'num_reads': batch_reads,
            'num_sweeps': parameters.num_sweeps,
        }
        if seed is not None:
            # Use a deterministic but different seed per batch.  This avoids
            # repeating the same pseudo-random batch while keeping the whole run
            # reproducible from one user-provided seed.
            sample_kwargs['seed'] = seed + batches_used

        sampleset = sampler.sample(model.bqm, **sample_kwargs)
        candidate = _decode_best_answer(model, sampleset)
        best_answer = _better_answer(candidate, best_answer)

        reads_used += batch_reads
        batches_used += 1

        # Energy 0 is an actual solution of the decision problem, so spending
        # the remaining reads would only look for additional equivalent answers.
        if best_answer.exact_partition_found:
            break

    return SiSiRunResult(
        model=model,
        parameters=parameters,
        best_answer=best_answer,
        reads_used=reads_used,
        batches_used=batches_used,
        proven_impossible_by_parity=False,
    )
