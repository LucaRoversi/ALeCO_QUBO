################################################################################
# NumberPartitioning_ExSol.py
#
# Classroom companion for the two examples in SiSi2Qubo.tex.
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
#   identical sum. Therefore, zero-energy states are precisely the answers of
#   the Subsets with Identical Sum / Number Partitioning instance.
#
# Software roles:
#   pyqubo is used as a modelling layer: it lets us write the Hamiltonian almost
#   exactly as a symbolic mathematical expression in binary variables. In this
#   file it is the bridge from the formula in the notes to an Ocean-compatible
#   BQM, but it is not the D-Wave QPU interface.
#
#   dimod is the D-Wave/Ocean-specific component used directly here. It provides
#   the Binary Quadratic Model (BQM) data structure and the standard SampleSet
#   returned by Ocean samplers.
#
#   dimod.ExactSolver is also part of Ocean. It is not a quantum sampler and it
#   does not use a D-Wave QPU. It enumerates all binary assignments, so it is a
#   transparent reference sampler for small examples and for checking the QUBO
#   construction before using heuristic samplers or hardware samplers.
################################################################################

from dimod import ExactSolver
from pyqubo import Binary


print('## "Number Partitioning" / "Subsets with Identical Sum"')
print('## Exact exhaustive sampling through dimod.ExactSolver\n')


################################################################################
# Variables shared by both examples.
#
# Binary('x1'), ..., Binary('x5') are pyqubo symbolic binary variables. They are
# not numerical values yet. They are placeholders used to build the polynomial
# expression for H. The later call to compile() translates this symbolic
# expression into a form from which a dimod BQM can be obtained.
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
# Helper functions.
################################################################################
def build_hamiltonian(variables, values):
    """Return the pyqubo expression for the Number Partitioning Hamiltonian.

    variables = (x1, x2, x3, x4, x5) as above.
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
    print(bqm.linear)
    print('\n -- bqm.quadratic, off-diagonal QUBO coefficients Q_ij:')
    print(bqm.quadratic)
    print('\n -- bqm.offset, constant term V^2:')
    print(bqm.offset)


def print_sampleset(sampleset):
    """Print the raw Ocean SampleSet returned by a sampler.

    A SampleSet is the standard Ocean container for sampler output. It stores the
    sampled binary assignments, their energies, and how many times each sample
    was observed. ExactSolver returns every possible assignment once.
    """

    print('Sampleset returned by dimod.ExactSolver:')
    print(sampleset)


def print_decoded_samples(compiled_hamiltonian, sampleset):
    """Decode Ocean samples back through the pyqubo model.

    The sampler works on the dimod BQM. pyqubo.decode_sampleset translates the
    SampleSet back into pyqubo's decoded representation, so that one can inspect
    samples using the original variable names and, in more elaborate models,
    constraint labels and sub-Hamiltonians.
    """

    decoded_sampleset = compiled_hamiltonian.decode_sampleset(sampleset)

    print('Decoded samples, sorted as returned by the decoded SampleSet:')
    for decoded_sample in decoded_sampleset:
        sample = decoded_sample.sample
        energy = decoded_sample.energy
        ordered_bits = tuple(sample[name] for name in variable_names)
        print(f'  x = {ordered_bits}, energy = {energy}, sample = {sample}')


def print_ground_states(sampleset):
    """Print the minimum-energy states.

    In these examples, a ground state with energy 0 is a genuine partition into
    two identical sums. If the minimum energy is positive, the instance has no
    exact answer.
    """

    ground_sampleset = sampleset.lowest()
    minimum_energy = ground_sampleset.first.energy

    print('\nMinimum energy found by exhaustive sampling:')
    print(minimum_energy)
    print('Ground states:')
    for row in ground_sampleset.data(['sample', 'energy']):
        sample = row.sample
        ordered_bits = tuple(sample[name] for name in variable_names)
        print(f'  x = {ordered_bits}, energy = {row.energy}')

    if minimum_energy == 0:
        print('Interpretation: the instance has at least one exact partition.')
    else:
        print('Interpretation: no binary assignment makes H equal to 0.')


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
    # A BQM is the representation expected by Ocean samplers, including the
    # exact sampler used here, simulated annealers, and D-Wave hardware-oriented
    # workflows after the additional embedding steps required by QPU samplers.
    ###########################################################################
    bqm = compiled_hamiltonian.to_bqm()
    print('\n--- Binary Quadratic Model exported to Ocean/dimod ---')
    print_bqm_components(bqm)

    ###########################################################################
    # Step 4. Sample the BQM with dimod.ExactSolver.
    #
    # ExactSolver performs a brute-force enumeration of all 2^5 assignments. It
    # is used here because the examples are intentionally small and because it
    # makes the relationship between the QUBO and its solutions completely
    # explicit. This sampler is deterministic and local: it does not require a
    # D-Wave API token, Leap access, or QPU time.
    ###########################################################################
    sampler = ExactSolver()
    print('\n--- Ocean sampler information ---')
    print('Sampler class: dimod.ExactSolver')
    print('Sampler parameters:')
    print(sampler.parameters)

    sampleset = sampler.sample(bqm)
    print('\n--- Raw Ocean SampleSet ---')
    print_sampleset(sampleset)

    ###########################################################################
    # Step 5. Decode and interpret the sampled states.
    #
    # The raw SampleSet is already enough to see energies. Decoding through
    # pyqubo is useful pedagogically because it brings the result back to the
    # variable names used when the Hamiltonian was written.
    ###########################################################################
    print('\n--- Decoded samples ---')
    print_decoded_samples(compiled_hamiltonian, sampleset)

    print('\n--- Ground-state interpretation ---')
    print_ground_states(sampleset)


################################################################################
# First instance from SiSi2Qubo.tex.
#
# S = (1, 3, 4, 2, 6), total V = 16.
# A zero-energy solution is x = (0, 0, 0, 1, 1), which chooses positions 4 and 5:
#   2 + 6 = 8.
# The complementary zero-energy solution is x = (1, 1, 1, 0, 0):
#   1 + 3 + 4 = 8.
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
################################################################################
run_instance(
    title='Second instance: no zero-energy answer',
    values=(1, 1, 1, 1, 1),
)
