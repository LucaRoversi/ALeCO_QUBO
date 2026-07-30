################################################################################
# NumberPartitioning_DWaveSam.py
#
# Classroom companion for the first Number Partitioning example in SiSi2Qubo.tex.
#
# This script has the same modelling purpose as NumberPartitioning_ExSol.py and
# NumberPartitioning_SiAnn.py, but it submits the resulting BQM to a D-Wave
# quantum annealer through DWaveSampler wrapped by EmbeddingComposite.
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
#   dimod is not imported explicitly here, but it is the Ocean layer behind the
#   Binary Quadratic Model and the SampleSet returned by the sampler.
#
#   dwave.system.samplers.DWaveSampler is the Ocean sampler that connects to an
#   available D-Wave QPU. Running this script requires a configured D-Wave Leap
#   account, a valid API token, internet access, and QPU time.
#
#   dwave.system.composites.EmbeddingComposite is the automatic minor-embedding
#   layer. The logical graph of the BQM is not usually identical to the physical
#   graph of the QPU. EmbeddingComposite maps each logical variable to one or
#   more physical qubits, called a chain.
#
# Main pedagogical point of this file:
#   The BQM construction is the same as in the exact and simulated-annealing
#   examples. What changes is the sampling layer. A QPU sampler introduces
#   hardware-specific notions:
#
#   num_reads = n_reads
#       Number of independent samples requested from the QPU.
#
#   annealing_time = anneal_time
#       Physical annealing time of each read on the QPU. This is not the same as
#       num_sweeps in simulated annealing. num_sweeps counts classical update
#       sweeps; annealing_time controls the duration of the hardware anneal.
#
#   chain_strength = chain_strength
#       Coupling strength used to keep all physical qubits in a chain aligned,
#       so that the chain behaves as one logical variable. Too small a value may
#       create broken chains; too large a value can dominate the problem biases.
#       The simple rule used below is useful for a classroom example, not a
#       universal tuning rule.
#
#   Because QPU sampling is stochastic and hardware-dependent, a returned
#   positive best energy is not by itself a proof that no zero-energy state
#   exists. It only describes the best state found in this sampling experiment.
################################################################################

from dwave.system.composites import EmbeddingComposite
from dwave.system.samplers import DWaveSampler
from pyqubo import Binary

import dwave.inspector


print('## "Number Partitioning" / "Subsets with Identical Sum"')
print('## QPU-oriented sampling through DWaveSampler + EmbeddingComposite\n')


################################################################################
# Global D-Wave sampling parameters.
#
# n_reads is passed to sample() as num_reads=n_reads.
# It controls how many samples are requested from the QPU.
#
# anneal_time is passed to sample() as annealing_time=anneal_time.
# It controls the physical annealing duration used for each read. It should not
# be identified with simulated annealing's num_sweeps: the former is a hardware
# timing parameter, while the latter is a count of classical sweeps.
#
# open_inspector controls whether the script opens D-Wave Inspector after the
# sampling call. Inspector is very useful in class because it shows the embedding,
# chains, chain breaks, and QPU sampling details. Set it to False when running in
# an environment where a browser window should not be opened.
################################################################################
n_reads = 10
anneal_time = 20
open_inspector = True


################################################################################
# Helper functions: modelling layer.
################################################################################
def make_binary_variables(number_of_values):
    """Create one pyqubo binary variable for each indexed value of S.

    The variables are named x1, x2, ..., xn to match the notation in the notes.
    They are symbolic variables: before sampling they are not equal to 0 or 1;
    they are placeholders used to build the polynomial Hamiltonian.
    """

    names = tuple(f'x{i}' for i in range(1, number_of_values + 1))
    variables = tuple(Binary(name) for name in names)
    return variables, names


def build_hamiltonian(variables, values):
    """Return the pyqubo expression for the Number Partitioning Hamiltonian.

    values = (v_1, ..., v_n) is the indexed collection used in the example.
    The expression mirrors the formula in SiSi2Qubo.tex:

        H = (V - 2 * selected_sum)^2,
        V = sum_i v_i,
        selected_sum = sum_i x_i v_i.

    In pyqubo, arithmetic operations between Binary variables and integers build
    a symbolic pseudo-Boolean polynomial. At this point we have described the
    optimization problem, but we have not submitted it to the QPU yet.
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
    """Print the parts of the Ocean BinaryQuadraticModel.

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


################################################################################
# Helper functions: QPU sampling layer.
################################################################################
def default_chain_strength(bqm):
    """Return a simple classroom chain-strength value for this BQM.

    A logical variable may be represented by a chain of physical qubits. The
    chain_strength parameter penalizes disagreements inside such chains.

    The rule used here follows the original script:

        chain_strength = max absolute quadratic bias + 1.

    This is intentionally simple and easy to explain. In real experiments,
    chain_strength should be tuned together with the problem scale, the selected
    QPU, the embedding, and the observed chain-break statistics.
    """

    largest_quadratic_bias = max(
        (abs(bias) for bias in bqm.quadratic.values()),
        default=1,
    )
    return largest_quadratic_bias + 1


def print_qpu_parameters(chain_strength):
    """Print and explain the parameters used in the QPU sampling call."""

    print('Sampler class: dwave.system.samplers.DWaveSampler')
    print('Composite:     dwave.system.composites.EmbeddingComposite')
    print('Sampling parameters used in this run:')
    print(f'  num_reads      = {n_reads}')
    print(f'  annealing_time = {anneal_time}')
    print(f'  chain_strength = {chain_strength}')
    print()
    print('Meaning:')
    print('  num_reads asks the QPU for several samples of the embedded BQM.')
    print('  annealing_time is the physical anneal duration per read.')
    print('  chain_strength penalizes disagreement inside chains of physical qubits.')
    print()
    print('Tuning principle:')
    print('  num_reads controls empirical sampling statistics; annealing_time controls')
    print('  the hardware anneal duration; chain_strength controls how strongly the')
    print('  embedding enforces each logical variable.')


def sample_with_dwave_qpu(bqm):
    """Sample the BQM using a D-Wave QPU through EmbeddingComposite.

    DWaveSampler sends the problem to a D-Wave quantum processing unit. Since the
    logical BQM graph may not be directly available on the hardware graph,
    EmbeddingComposite first performs minor embedding automatically.

    The returned object is an Ocean SampleSet. It contains sampled assignments,
    energies, occurrence counts, and usually additional embedding diagnostics
    such as chain-break information.
    """

    chain_strength = default_chain_strength(bqm)
    print_qpu_parameters(chain_strength)

    sampler = EmbeddingComposite(DWaveSampler())

    try:
        return sampler.sample(
            bqm,
            chain_strength=chain_strength,
            num_reads=n_reads,
            annealing_time=anneal_time,
        )
    except Exception as error:
        print('\nD-Wave QPU sampling did not complete.')
        print('Check your Leap credentials, selected solver, internet connection,')
        print('available QPU time, and whether annealing_time is supported.')
        raise error


def print_sampleset(sampleset):
    """Print the raw Ocean SampleSet returned by the QPU sampler.

    A SampleSet stores the sampled binary assignments, their energies, and how
    many times each assignment was observed. For embedded QPU sampling, the
    SampleSet may also contain chain-break information. This information is part
    of the experiment: frequent chain breaks suggest that the embedding or the
    chain strength should be reconsidered.
    """

    print('Raw SampleSet returned by DWaveSampler + EmbeddingComposite:')
    print(sampleset)


def print_embedding_diagnostics(sampleset):
    """Print embedding metadata when Ocean provides it in sampleset.info."""

    print('Embedding and QPU metadata available in sampleset.info:')
    if not sampleset.info:
        print('  No metadata available in sampleset.info.')
        return

    for key, value in sampleset.info.items():
        print(f'  {key}: {value}')


def print_decoded_samples(compiled_hamiltonian, sampleset, variable_names):
    """Decode Ocean samples back through the pyqubo model.

    The sampler works on the dimod BQM. pyqubo.decode_sampleset translates the
    SampleSet back into pyqubo's decoded representation, using the original
    symbolic variable names x1, ..., xn.
    """

    decoded_sampleset = compiled_hamiltonian.decode_sampleset(sampleset)

    print('Decoded samples, ordered as returned by the decoded SampleSet:')
    for decoded_sample in decoded_sampleset:
        sample = decoded_sample.sample
        energy = decoded_sample.energy
        ordered_bits = tuple(sample[name] for name in variable_names)
        print(f'  x = {ordered_bits}, energy = {energy}, sample = {sample}')


def print_best_states(sampleset, variable_names):
    """Print the best states found by the QPU sampling experiment.

    For this instance, energy 0 means that the run found an exact partition.
    Since QPU sampling is stochastic, failure to observe energy 0 in one run
    would not be a mathematical proof that no partition exists. It would instead
    motivate a new experiment: more reads, different annealing time, different
    chain strength, or a different embedding/solver.
    """

    best_sampleset = sampleset.lowest()
    best_energy = best_sampleset.first.energy

    print('\nBest energy found in this QPU run:')
    print(best_energy)
    print('Best states found:')

    data_fields = ['sample', 'energy', 'num_occurrences']
    if 'chain_break_fraction' in best_sampleset.record.dtype.names:
        data_fields.append('chain_break_fraction')

    for row in best_sampleset.data(data_fields):
        sample = row.sample
        ordered_bits = tuple(sample[name] for name in variable_names)
        line = (
            f'  x = {ordered_bits}, energy = {row.energy}, '
            f'num_occurrences = {row.num_occurrences}'
        )
        if hasattr(row, 'chain_break_fraction'):
            line += f', chain_break_fraction = {row.chain_break_fraction}'
        print(line)

    if best_energy == 0:
        print('Interpretation: this run found an exact partition.')
    else:
        print('Interpretation: this run did not find a zero-energy state.')
        print('For QPU sampling this is not, by itself, a proof of absence.')


def maybe_open_dwave_inspector(sampleset):
    """Open D-Wave Inspector when requested by open_inspector.

    Inspector gives a visual explanation of the hardware experiment: the selected
    QPU, the minor embedding, chains, chain breaks, and samples. It is therefore
    useful for a lecture, but it may be inconvenient in automated runs.
    """

    if open_inspector:
        print('\n--- Opening D-Wave Inspector ---')
        dwave.inspector.show(sampleset)
    else:
        print('\n--- D-Wave Inspector disabled ---')
        print('Set open_inspector = True to visualize the embedding and samples.')


################################################################################
# Main experiment.
################################################################################
def run_instance(title, values):
    """Build, compile, submit, decode, and interpret one QPU experiment."""

    variables, variable_names = make_binary_variables(len(values))

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
    # The same BQM could be passed to ExactSolver, to neal's simulated annealer,
    # to a hybrid sampler, or, as here, to a QPU-oriented sampler after minor
    # embedding.
    ###########################################################################
    bqm = compiled_hamiltonian.to_bqm()
    print('\n--- Binary Quadratic Model exported to Ocean/dimod ---')
    print_bqm_components(bqm)

    ###########################################################################
    # Step 4. Submit the BQM to the D-Wave QPU.
    #
    # EmbeddingComposite searches for a minor embedding of the logical BQM into
    # the QPU topology. The QPU then samples the embedded problem. This is the
    # first script in the sequence where the computation is neither exhaustive
    # nor purely local/classical.
    ###########################################################################
    print('\n--- D-Wave QPU sampler ---')
    sampleset = sample_with_dwave_qpu(bqm)

    print('\n--- Raw Ocean SampleSet ---')
    print_sampleset(sampleset)

    print('\n--- Embedding diagnostics ---')
    print_embedding_diagnostics(sampleset)

    ###########################################################################
    # Step 5. Decode and interpret the sampled states.
    ###########################################################################
    print('\n--- Decoded samples ---')
    print_decoded_samples(compiled_hamiltonian, sampleset, variable_names)

    print('\n--- Best-state interpretation ---')
    print_best_states(sampleset, variable_names)

    ###########################################################################
    # Step 6. Visualize the hardware run, if requested.
    ###########################################################################
    maybe_open_dwave_inspector(sampleset)


if __name__ == '__main__':
    ############################################################################
    # First instance from SiSi2Qubo.tex.
    #
    # S = (1, 3, 4, 2, 6), total V = 16.
    # A zero-energy solution is x = (0, 0, 0, 1, 1), which chooses positions 4
    # and 5:
    #   2 + 6 = 8.
    # The complementary zero-energy solution is x = (1, 1, 1, 0, 0):
    #   1 + 3 + 4 = 8.
    #
    # Since QPU sampling is stochastic and embedding-dependent, the script asks
    # whether the selected hardware experiment observes one of these states.
    ############################################################################
    run_instance(
        title='First instance: two zero-energy answers',
        values=(1, 3, 4, 2, 6),
    )
