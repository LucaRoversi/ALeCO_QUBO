################################################################################
# NumberPartitioning_SiAnn.py
#
# Classroom companion for the two Number Partitioning examples in SiSi2Qubo.tex.
#
# This script has the same modelling purpose as NumberPartitioning_ExSol.py, but
# it replaces exhaustive enumeration with simulated annealing.
#
# Mathematical problem:
#   Given an indexed collection S = (v_1, ..., v_n) of natural numbers, decide
#   whether some set of positions I has the same total weight as its complement.
#
# Binary encoding:
#   x_i = 1  means that position i is chosen;
#   x_i = 0  means that position i is left in the complement.
#
# QUBO objective / Hamiltonian:
#   H(x_1, ..., x_n) = (sum_i v_i - 2 sum_i x_i v_i)^2.
#
# Interpretation:
#   H = 0 exactly when the chosen positions and the complementary positions have
#   identical sum. Therefore, zero-energy states are precisely the solutions of
#   the Subsets with Identical Sum / Number Partitioning instance.
#
# Software roles:
#   pyqubo is used as a modelling layer. It lets us write the Hamiltonian almost
#   exactly as a symbolic mathematical expression in binary variables. The call
#   to compile() prepares that expression for export to an Ocean-compatible BQM.
#
#   dimod is the D-Wave Ocean component that provides the Binary Quadratic Model
#   (BQM) and the SampleSet interface used by Ocean samplers.
#
#   neal.SimulatedAnnealingSampler is a classical simulated-annealing sampler
#   distributed in the D-Wave Ocean ecosystem. It is not a quantum sampler and it
#   does not submit the problem to a D-Wave QPU. It is useful here because it has
#   the same BQM input style as Ocean samplers and because it introduces the
#   practical idea of tuning sampling parameters.
#
# Main pedagogical point of this file:
#   Unlike ExactSolver, simulated annealing is heuristic. It does not enumerate
#   all states. It performs several stochastic annealing attempts and returns the
#   states it has found. For this reason the parameters passed to sample(), in
#   particular num_reads and num_sweeps, are part of the modelling experiment.
#
#   num_reads = n_reads
#       Number of independent annealing attempts. More reads give more chances to
#       start from different random configurations and to observe a low-energy
#       state. They improve exploration and empirical confidence.
#
#   num_sweeps = 10
#       Number of sweeps performed inside each annealing attempt. More sweeps give
#       each read more time to relax along the annealing schedule. They improve
#       the quality of each individual attempt, but they also consume more work.
#
#   Balance:
#       With a fixed computational budget, the relevant cost is roughly related
#       to num_reads * num_sweeps. Many short reads explore broadly but may stop
#       before relaxation; a few long reads relax more carefully but may explore
#       fewer independent starts. The useful balance is instance-dependent.
#
#       This is also the right conceptual preparation for quantum and hybrid
#       annealing workflows: one must tune the number of reads together with the
#       annealing effort per read in order to exploit the available computational
#       resource. Increasing both blindly is not the same as taking advantage of
#       the potentially greater computational power of the quantum model.
################################################################################

from neal import SimulatedAnnealingSampler
from pyqubo import Binary


print('## "Number Partitioning" / "Subsets with Identical Sum"')
print('## Heuristic sampling through neal.SimulatedAnnealingSampler\n')


################################################################################
# Variables shared by both examples.
#
# Binary('x1'), ..., Binary('x5') are pyqubo symbolic binary variables. They are
# used to build the polynomial expression for H. They become numerical only when
# a sampler assigns 0 or 1 to them.
################################################################################
x1, x2, x3, x4, x5 = (
    Binary('x1'),
    Binary('x2'),
    Binary('x3'),
    Binary('x4'),
    Binary('x5'),
)
variables = (x1, x2, x3, x4, x5)
variable_names = ('x1', 'x2', 'x3', 'x4', 'x5')


################################################################################
# Global simulated-annealing parameters.
#
# n_reads is passed to sample() as num_reads=n_reads.
# It controls how many independent stochastic annealing runs are performed.
#
# sweeps_per_read is passed to sample() as num_sweeps=sweeps_per_read.
# It controls how much annealing work is spent inside each run.
#
# For the tiny examples below, n_reads = 10 and sweeps_per_read = 10 are enough
# to keep the output short and readable. For larger QUBO instances these values
# should be varied experimentally: the aim is to allocate the available budget
# between more independent attempts and more careful relaxation per attempt.
################################################################################
n_reads = 10
sweeps_per_read = 10


################################################################################
# Helper functions.
################################################################################
def build_hamiltonian(variables, values):
    """Return the pyqubo expression for the Number Partitioning Hamiltonian.

    values = (v_1, ..., v_5) is the indexed collection used in the examples.
    The expression mirrors the formula in SiSi2Qubo.tex:

        H = (V - 2 * selected_sum)^2,
        V = sum_i v_i,
        selected_sum = sum_i x_i v_i.

    In pyqubo, arithmetic operations between Binary variables and integers build
    a symbolic pseudo-Boolean polynomial. At this point we have described the
    optimization problem, but we have not sampled it yet.
    """

    total = sum(values)
    selected_sum = sum(x * v for x, v in zip(variables, values))
    return (total - 2 * selected_sum) ** 2


def sorted_linear_terms(bqm):
    """Return bqm.linear sorted by variable name for stable classroom output."""

    return dict(sorted(bqm.linear.items(), key=lambda item: item[0]))


def sorted_quadratic_terms(bqm):
    """Return bqm.quadratic sorted lexicographically by variable-pair names."""

    return dict(
        sorted(
            bqm.quadratic.items(),
            key=lambda item: (item[0][0], item[0][1]),
        )
    )


def print_bqm_components(bqm):
    """Print the parts of the dimod BinaryQuadraticModel.

    In Ocean, a Binary Quadratic Model stores an objective of the form

        energy(x) = offset
                    + sum_i linear[i] * x_i
                    + sum_{i<j} quadratic[i,j] * x_i * x_j.

    For the upper-triangular QUBO matrix Q used in the notes:
      - bqm.linear contains the diagonal coefficients Q_ii;
      - bqm.quadratic contains the off-diagonal coefficients Q_ij;
      - bqm.offset contains the constant term V^2.
    """

    print('bqm:')
    print(bqm)
    print('\n -- bqm.linear, diagonal QUBO coefficients Q_ii:')
    print(sorted_linear_terms(bqm))
    print('\n -- bqm.quadratic, off-diagonal QUBO coefficients Q_ij:')
    print(sorted_quadratic_terms(bqm))
    print('\n -- bqm.offset, constant term V^2:')
    print(bqm.offset)


def print_annealing_parameters():
    """Print and explain the parameters used by the simulated annealer."""

    print('Sampler class: neal.SimulatedAnnealingSampler')
    print('Sampling parameters used in this run:')
    print(f'  num_reads  = {n_reads}')
    print(f'  num_sweeps = {sweeps_per_read}')
    print()
    print('Meaning:')
    print('  num_reads counts independent stochastic annealing attempts.')
    print('  num_sweeps counts the annealing sweeps performed in each attempt.')
    print('  The product num_reads * num_sweeps is a first approximation of the')
    print('  classical effort spent by this simulated annealing experiment.')
    print()
    print('Tuning principle:')
    print('  more reads = broader exploration; more sweeps = deeper relaxation.')
    print('  The useful balance must be found experimentally for each instance.')


def sample_with_simulated_annealing(bqm):
    """Sample the BQM using neal.SimulatedAnnealingSampler.

    The sampler receives the Ocean BQM and returns an Ocean SampleSet. Because
    this is a heuristic sampler, the lowest-energy state returned is the best
    state found in the selected stochastic experiment, not a proof of optimality.

    The two parameters below are intentionally written explicitly:

        num_reads=n_reads
        num_sweeps=sweeps_per_read

    num_reads asks for several independent attempts. num_sweeps controls the
    length of each attempt. In a larger experiment one should compare several
    pairs, for example:

        many short reads:  num_reads large, num_sweeps small;
        fewer long reads: num_reads small, num_sweeps large.

    The same conceptual trade-off is important when moving to quantum or hybrid
    annealing resources: the number of reads and the annealing effort per read
    must be balanced, rather than increased mechanically.
    """

    sampler = SimulatedAnnealingSampler()
    print_annealing_parameters()

    return sampler.sample(
        bqm,
        num_reads=n_reads,
        num_sweeps=sweeps_per_read,
    )


def print_sampleset(sampleset):
    """Print the raw Ocean SampleSet returned by simulated annealing.

    A SampleSet stores the sampled binary assignments, their energies, and how
    many times each assignment was observed. Repeated observations are important
    in heuristic sampling: frequent low-energy samples suggest that the chosen
    parameters are reasonable, while missing known ground states may suggest that
    more reads, more sweeps, or a different balance is needed.
    """

    print('Raw SampleSet returned by neal.SimulatedAnnealingSampler:')
    print(sampleset)


def print_decoded_samples(compiled_hamiltonian, sampleset):
    """Decode Ocean samples back through the pyqubo model.

    The sampler works on the dimod BQM. pyqubo.decode_sampleset translates the
    SampleSet back into pyqubo's decoded representation, using the original
    symbolic variable names x1, ..., x5.
    """

    decoded_sampleset = compiled_hamiltonian.decode_sampleset(sampleset)

    print('Decoded samples, ordered by increasing energy when displayed:')
    for decoded_sample in decoded_sampleset:
        sample = decoded_sample.sample
        energy = decoded_sample.energy
        ordered_bits = tuple(sample[name] for name in variable_names)
        print(f'  x = {ordered_bits}, energy = {energy}, sample = {sample}')


def print_best_states(sampleset):
    """Print the best states found by simulated annealing.

    For these examples the theoretical meaning is the same as before:
      - best energy 0 means that a partition was found;
      - best energy > 0 is consistent with no exact partition.

    However, because simulated annealing is heuristic, a positive best energy is
    not by itself a mathematical proof that no zero-energy state exists. In the
    first instance, if the sampler does not find energy 0, the parameter balance
    should be reconsidered. In the second instance, the mathematical reason for
    the absence of energy 0 is the odd total sum, not the heuristic output alone.
    """

    best_sampleset = sampleset.lowest()
    best_energy = best_sampleset.first.energy

    print('\nBest energy found in this simulated-annealing run:')
    print(best_energy)
    print('Best states found:')
    for row in best_sampleset.data(['sample', 'energy', 'num_occurrences']):
        sample = row.sample
        ordered_bits = tuple(sample[name] for name in variable_names)
        print(
            f'  x = {ordered_bits}, energy = {row.energy}, '
            f'num_occurrences = {row.num_occurrences}'
        )

    if best_energy == 0:
        print('Interpretation: this run found an exact partition.')
    else:
        print('Interpretation: this run did not find a zero-energy state.')
        print('For heuristic sampling this is not, by itself, a proof of absence.')


def run_instance(title, values):
    """Build, compile, sample, and decode one Number Partitioning instance."""

    print('\n' + '=' * 78)
    print(title)
    print('=' * 78)
    print(f'Indexed collection S = {values}')
    print(f'Total weight V = {sum(values)}')

    ###########################################################################
    # Step 1. Build the Hamiltonian in pyqubo.
    #
    # This is the modelling step. We are still at the level of the mathematical
    # objective H, represented symbolically by pyqubo.
    ###########################################################################
    hamiltonian = build_hamiltonian(variables, values)

    ###########################################################################
    # Step 2. Compile the pyqubo expression.
    #
    # compile() creates pyqubo's internal model. This object knows how to export
    # the problem to Ocean's dimod BQM format and how to decode samples later.
    ###########################################################################
    compiled_hamiltonian = hamiltonian.compile()

    ###########################################################################
    # Step 3. Export the compiled model as a dimod BQM.
    #
    # This is the point where the symbolic Hamiltonian becomes an Ocean object.
    # A BQM is the representation expected by Ocean samplers, including neal's
    # classical simulated annealer and, after the additional steps required for
    # hardware use, D-Wave QPU-oriented workflows.
    ###########################################################################
    bqm = compiled_hamiltonian.to_bqm()
    print('\n--- Binary Quadratic Model exported to Ocean/dimod ---')
    print_bqm_components(bqm)

    ###########################################################################
    # Step 4. Sample the BQM with simulated annealing.
    #
    # ExactSolver would enumerate all 2^5 states. Here we deliberately use a
    # heuristic sampler, so the result depends on the stochastic experiment and
    # on the chosen values of num_reads and num_sweeps.
    ###########################################################################
    print('\n--- Ocean-compatible simulated annealing sampler ---')
    sampleset = sample_with_simulated_annealing(bqm)

    print('\n--- Raw Ocean SampleSet ---')
    print_sampleset(sampleset)

    ###########################################################################
    # Step 5. Decode and interpret the sampled states.
    ###########################################################################
    print('\n--- Decoded samples ---')
    print_decoded_samples(compiled_hamiltonian, sampleset)

    print('\n--- Best-state interpretation ---')
    print_best_states(sampleset)


################################################################################
# First instance from SiSi2Qubo.tex.
#
# S = (1, 3, 4, 2, 6), total V = 16.
# A zero-energy solution is x = (0, 0, 0, 1, 1), which chooses positions 4 and 5:
#   2 + 6 = 8.
# The complementary zero-energy solution is x = (1, 1, 1, 0, 0):
#   1 + 3 + 4 = 8.
#
# Since simulated annealing is heuristic, the script asks whether the selected
# pair (num_reads, num_sweeps) is sufficient to find these zero-energy states in
# this run. If it is not, one should increase or rebalance the two parameters.
################################################################################
run_instance(
    title='First instance: two zero-energy answers',
    values=(1, 3, 4, 2, 6),
)


################################################################################
# Second instance from SiSi2Qubo.tex.
#
# S = (1, 1, 1, 1, 1), total V = 5.
# Since V is odd, no subset can have the same sum as its complement. Therefore
# the Hamiltonian cannot reach energy 0; the minimum energy is 1.
#
# In this case, simulated annealing should find states of energy 1 if the chosen
# parameters are adequate. The absence of energy 0 is explained mathematically by
# the odd total sum, not merely by the heuristic sampler.
################################################################################
run_instance(
    title='Second instance: no zero-energy answer',
    values=(1, 1, 1, 1, 1),
)
