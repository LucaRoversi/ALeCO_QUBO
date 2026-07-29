################################################################################
# MaxCut_SiAnn.py
#
# Simulated-annealing companion for the three-vertex path in MaxCut2Qubo.tex:
#
#                       b ----- c ----- d
#
# Binary encoding:
#   x_v = 1  means that vertex v belongs to X;
#   x_v = 0  means that vertex v belongs to Y.
#
# Cut value:
#   C(x) = sum_{ {u,v} in E } (x_u + x_v - 2*x_u*x_v).
#
# Minimization Hamiltonian:
#   H(x) = -C(x).
#
# Therefore, an energy of -k represents a cut containing k edges. The optimum
# for this path has energy -2 and is encoded by (b,c,d)=(0,1,0) or (1,0,1).
#
# neal.SimulatedAnnealingSampler is a classical heuristic sampler in the D-Wave
# Ocean ecosystem. Unlike ExactSolver, it does not enumerate all states and does
# not prove that the best state found is globally optimal.
################################################################################

from neal import SimulatedAnnealingSampler
from pyqubo import Base, Binary


VERTICES = ('b', 'c', 'd')
EDGES = (('b', 'c'), ('c', 'd'))

# The two effort parameters are explicit so that the experiment is reproducible
# and easy to tune. The seed fixes the pseudo-random trajectory of this example.
N_READS = 20
SWEEPS_PER_READ = 50
RANDOM_SEED = 7


def build_binary_variables(vertices):
    """Return a dictionary of pyqubo Binary variables indexed by vertex name."""

    return {vertex: Binary(vertex) for vertex in vertices}


def build_cut_value(binary_variables, edges) -> Base:
    """Return the symbolic MaxCut value as a sum of edge XOR polynomials."""

    edge_terms = [
        binary_variables[u]
        + binary_variables[v]
        - 2 * binary_variables[u] * binary_variables[v]
        for u, v in edges
    ]

    # Python's sum() uses the integer 0 for an empty iterable. Consequently,
    # Pylance would infer "Base | int" and later reject hamiltonian.compile().
    # A MaxCut instance must contain at least one edge, so make that requirement
    # explicit and start the accumulation from a genuine pyqubo expression.
    if not edge_terms:
        raise ValueError('A MaxCut instance must contain at least one edge.')

    cut_value: Base = edge_terms[0]
    for edge_term in edge_terms[1:]:
        cut_value = cut_value + edge_term
    return cut_value


def build_hamiltonian(binary_variables, edges) -> Base:
    """Return the QUBO minimization Hamiltonian H = -(cut value)."""

    return -build_cut_value(binary_variables, edges)


def sorted_linear_terms(bqm):
    """Return the BQM linear biases sorted for stable classroom output."""

    return dict(sorted(bqm.linear.items(), key=lambda item: item[0]))


def sorted_quadratic_terms(bqm):
    """Return the BQM quadratic biases sorted by their endpoint names."""

    return dict(
        sorted(
            bqm.quadratic.items(),
            key=lambda item: tuple(sorted(item[0])),
        )
    )


def partition_from_sample(sample):
    """Decode a binary sample into the two sides X and Y."""

    side_x = tuple(vertex for vertex in VERTICES if sample[vertex] == 1)
    side_y = tuple(vertex for vertex in VERTICES if sample[vertex] == 0)
    return side_x, side_y


def crossing_edges(sample):
    """Return the edges crossing the cut represented by sample."""

    return tuple(
        (u, v)
        for u, v in EDGES
        if sample[u] != sample[v]
    )


def print_bqm_components(bqm):
    """Print the BQM coefficients and their mathematical meaning."""

    print('bqm:')
    print(bqm)
    print('\n -- bqm.linear = -degree(v):')
    print(sorted_linear_terms(bqm))
    print('\n -- bqm.quadratic = 2 on every graph edge:')
    print(sorted_quadratic_terms(bqm))
    print('\n -- bqm.offset:')
    print(bqm.offset)


def print_annealing_parameters():
    """Print the simulated-annealing parameters and their roles."""

    print('Sampler class: neal.SimulatedAnnealingSampler')
    print('Sampling parameters:')
    print(f'  num_reads  = {N_READS}')
    print(f'  num_sweeps = {SWEEPS_PER_READ}')
    print(f'  seed       = {RANDOM_SEED}')
    print()
    print('num_reads controls the number of independent stochastic attempts.')
    print('num_sweeps controls the relaxation effort inside each attempt.')
    print('Their product is a first approximation of the classical work used.')


def sample_with_simulated_annealing(bqm):
    """Return a heuristic SampleSet produced by simulated annealing.

    Many short reads emphasize exploration; fewer long reads emphasize the
    relaxation of each initial state. The useful balance is instance-dependent.
    """

    sampler = SimulatedAnnealingSampler()
    print_annealing_parameters()
    return sampler.sample(
        bqm,
        num_reads=N_READS,
        num_sweeps=SWEEPS_PER_READ,
        seed=RANDOM_SEED,
    )


def print_decoded_samples(compiled_hamiltonian, sampleset):
    """Decode and display the distinct sampled assignments."""

    aggregated = sampleset.aggregate()
    decoded_sampleset = compiled_hamiltonian.decode_sampleset(aggregated)

    print('Distinct decoded assignments:')
    for decoded_sample in decoded_sampleset:
        sample = decoded_sample.sample
        side_x, side_y = partition_from_sample(sample)
        cut_edges = crossing_edges(sample)
        print(
            f'  X = {side_x}, Y = {side_y}, crossing edges = {cut_edges}, '
            f'cut value = {len(cut_edges)}, energy = {decoded_sample.energy}'
        )


def print_best_states(sampleset):
    """Print and verify the best states found in this stochastic run.

    The equality energy = -(cut value) is exact for every returned sample.
    Optimality, however, does not follow from simulated annealing alone.
    """

    best_sampleset = sampleset.lowest().aggregate()
    best_energy = best_sampleset.first.energy

    print(f'Best energy found: {best_energy}')
    print(f'Best cut value found: {-best_energy}')
    print('Best states found:')

    for row in best_sampleset.data(
        ['sample', 'energy', 'num_occurrences'],
        sorted_by='energy',
    ):
        sample = row.sample
        side_x, side_y = partition_from_sample(sample)
        cut_edges = crossing_edges(sample)

        assert row.energy == -len(cut_edges)

        print(
            f'  X = {side_x}, Y = {side_y}, crossing edges = {cut_edges}, '
            f'energy = {row.energy}, occurrences = {row.num_occurrences}'
        )

    print(
        'Heuristic warning: the best returned energy is evidence from this run, '
        'not a proof of global optimality.'
    )


def main():
    """Build, compile, heuristically sample, decode, and verify the MaxCut QUBO."""

    print('## MaxCut on the path b--c--d')
    print('## Heuristic sampling through neal.SimulatedAnnealingSampler\n')
    print(f'Vertices V = {VERTICES}')
    print(f'Edges E = {EDGES}')

    ###########################################################################
    # Step 1. Build the symbolic Hamiltonian H = -C with pyqubo.
    ###########################################################################
    binary_variables = build_binary_variables(VERTICES)
    hamiltonian = build_hamiltonian(binary_variables, EDGES)

    ###########################################################################
    # Step 2. Compile the symbolic expression.
    ###########################################################################
    compiled_hamiltonian = hamiltonian.compile()

    ###########################################################################
    # Step 3. Export the model as an Ocean/dimod BQM.
    ###########################################################################
    bqm = compiled_hamiltonian.to_bqm()
    print('\n--- Binary Quadratic Model exported to Ocean/dimod ---')
    print_bqm_components(bqm)

    ###########################################################################
    # Step 4. Sample the BQM with classical simulated annealing.
    ###########################################################################
    print('\n--- Ocean-compatible simulated annealing ---')
    sampleset = sample_with_simulated_annealing(bqm)
    print('\n--- Raw Ocean SampleSet ---')
    print(sampleset)

    ###########################################################################
    # Step 5. Decode and interpret the stochastic result.
    ###########################################################################
    print('\n--- Decoded samples ---')
    print_decoded_samples(compiled_hamiltonian, sampleset)

    print('\n--- Best-state interpretation ---')
    print_best_states(sampleset)


if __name__ == '__main__':
    main()
