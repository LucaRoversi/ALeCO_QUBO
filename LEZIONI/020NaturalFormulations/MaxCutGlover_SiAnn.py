################################################################################
# MaxCutGlover_SiAnn.py
#
# Simulated-annealing implementation of the five-vertex MaxCut example adapted
# from "Quantum Bridge Analytics I: A Tutorial on Formulating and Using QUBO
# Models". The graph is defined by
#
#   E = {{x1,x2}, {x1,x3}, {x2,x4},
#        {x3,x4}, {x3,x5}, {x4,x5}}
#
# which is:
# 
#              1-----2
#              |     |
#              3-----4
#               \   /
#                 5
#
# Binary encoding:
#   x_v = 1  means that vertex v belongs to X;
#   x_v = 0  means that vertex v belongs to Y.
#
# For every edge {u,v}, the XOR polynomial
#
#   x_u + x_v - 2*x_u*x_v
#
# is 1 exactly when the edge crosses the cut. The minimization Hamiltonian is
#
#   H(x) = - sum_{ {u,v} in E } XOR(x_u, x_v).
#
# Thus the sampled energy is the negative of the cut value. In particular,
# energy -5 means that five edges cross the cut; the energy itself is not the
# positive number of crossing edges.
#
# The Hamiltonian is constructed from the edge list instead of manually copied
# coefficients. This makes the code auditable: linear[v] is generated as
# -degree(v), and every graph edge receives quadratic bias +2.
################################################################################


from neal import SimulatedAnnealingSampler
from pyqubo import Base, Binary


VERTICES = ('x1', 'x2', 'x3', 'x4', 'x5')
EDGES = (
    ('x1', 'x2'),
    ('x1', 'x3'),
    ('x2', 'x4'),
    ('x3', 'x4'),
    ('x3', 'x5'),
    ('x4', 'x5'),
)

N_READS = 50
SWEEPS_PER_READ = 100
RANDOM_SEED = 7


def build_binary_variables(vertices):
    """Return a dictionary of pyqubo Binary variables indexed by vertex name."""

    return {vertex: Binary(vertex) for vertex in vertices}


def build_cut_value(binary_variables, edges) -> Base:
    """Return the symbolic number of graph edges crossing the cut."""

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
    """Return the minimization Hamiltonian H = -(cut value)."""

    return -build_cut_value(binary_variables, edges)


def degree(vertex):
    """Return the degree of vertex in the graph defined by EDGES."""

    return sum(vertex in edge for edge in EDGES)


def expected_linear_biases():
    """Return the theoretical BQM linear biases -degree(v)."""

    return {vertex: -degree(vertex) for vertex in VERTICES}


def expected_quadratic_biases():
    """Return the theoretical quadratic bias +2 for every graph edge."""

    return {tuple(sorted(edge)): 2 for edge in EDGES}


def sorted_linear_terms(bqm):
    """Return the BQM linear biases sorted for stable classroom output."""

    return dict(sorted(bqm.linear.items(), key=lambda item: item[0]))


def sorted_quadratic_terms(bqm):
    """Return the BQM quadratic biases with canonical sorted endpoint pairs."""

    return dict(
        sorted(
            (
                (tuple(sorted(edge)), bias)
                for edge, bias in bqm.quadratic.items()
            ),
            key=lambda item: item[0],
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


def verify_bqm_coefficients(bqm):
    """Assert that pyqubo produced the coefficients derived from the graph.

    These assertions connect the abstract edge sum to the concrete BQM:

      linear[v]       = -degree(v),
      quadratic[u, v] = 2 for each edge,
      offset           = 0.
    """

    assert sorted_linear_terms(bqm) == expected_linear_biases()
    assert sorted_quadratic_terms(bqm) == expected_quadratic_biases()
    assert bqm.offset == 0


def print_bqm_components(bqm):
    """Print the BQM components and compare them with graph-derived values."""

    print('bqm:')
    print(bqm)
    print('\n -- bqm.linear = -degree(v):')
    print(sorted_linear_terms(bqm))
    print('    expected:')
    print(expected_linear_biases())
    print('\n -- bqm.quadratic = 2 on every graph edge:')
    print(sorted_quadratic_terms(bqm))
    print('\n -- bqm.offset:')
    print(bqm.offset)


def print_annealing_parameters():
    """Print the parameters controlling the simulated-annealing experiment."""

    print('Sampler class: neal.SimulatedAnnealingSampler')
    print('Sampling parameters:')
    print(f'  num_reads  = {N_READS}')
    print(f'  num_sweeps = {SWEEPS_PER_READ}')
    print(f'  seed       = {RANDOM_SEED}')
    print()
    print('More reads broaden the search over independent initial states.')
    print('More sweeps increase the relaxation effort within each read.')
    print('The useful balance must be measured for the instance under study.')


def sample_with_simulated_annealing(bqm):
    """Return a reproducible heuristic SampleSet for the Glover instance."""

    sampler = SimulatedAnnealingSampler()
    print_annealing_parameters()
    return sampler.sample(
        bqm,
        num_reads=N_READS,
        num_sweeps=SWEEPS_PER_READ,
        seed=RANDOM_SEED,
    )


def print_distinct_samples(sampleset):
    """Print each distinct sampled cut and its number of observations."""

    aggregated = sampleset.aggregate()

    print('Distinct sampled cuts:')
    for row in aggregated.data(
        ['sample', 'energy', 'num_occurrences'],
        sorted_by='energy',
    ):
        sample = row.sample
        side_x, side_y = partition_from_sample(sample)
        cut_edges = crossing_edges(sample)

        assert row.energy == -len(cut_edges)

        print(
            f'  X = {side_x}, Y = {side_y}, cut value = {len(cut_edges)}, '
            f'energy = {row.energy}, occurrences = {row.num_occurrences}'
        )


def print_best_states(sampleset):
    """Print and explain the best states found by simulated annealing.

    The instance has four binary ground states. Two pairs are complements. The
    additional degeneracy comes from x5: once x3 and x4 are separated, placing
    x5 on either side cuts exactly one of {x3,x5} and {x4,x5}.
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
            f'  X = {side_x}, Y = {side_y}, '
            f'crossing edges = {cut_edges}, '
            f'energy = {row.energy}, occurrences = {row.num_occurrences}'
        )

    print(
        'Heuristic warning: simulated annealing reports the best states found; '
        'it does not by itself prove that no lower-energy state exists.'
    )


def main():
    """Build, check, sample, decode, and interpret the five-vertex MaxCut QUBO."""

    print('## Five-vertex MaxCut example')
    print('## Heuristic sampling through neal.SimulatedAnnealingSampler\n')
    print(f'Vertices V = {VERTICES}')
    print(f'Edges E = {EDGES}')

    ###########################################################################
    # Step 1. Build H = -C directly from the graph edge list.
    ###########################################################################
    binary_variables = build_binary_variables(VERTICES)
    hamiltonian = build_hamiltonian(binary_variables, EDGES)

    ###########################################################################
    # Step 2. Compile the pyqubo expression and export an Ocean BQM.
    ###########################################################################
    compiled_hamiltonian = hamiltonian.compile()
    bqm = compiled_hamiltonian.to_bqm()

    ###########################################################################
    # Step 3. Verify the graph-to-BQM translation before sampling.
    ###########################################################################
    verify_bqm_coefficients(bqm)
    print('\n--- Verified Binary Quadratic Model ---')
    print_bqm_components(bqm)

    ###########################################################################
    # Step 4. Sample with classical simulated annealing.
    ###########################################################################
    print('\n--- Ocean-compatible simulated annealing ---')
    sampleset = sample_with_simulated_annealing(bqm)
    print('\n--- Raw Ocean SampleSet ---')
    print(sampleset)

    ###########################################################################
    # Step 5. Decode the sampled bits as cuts and check H = -C.
    ###########################################################################
    print('\n--- Distinct decoded cuts ---')
    print_distinct_samples(sampleset)

    print('\n--- Best-state interpretation ---')
    print_best_states(sampleset)


if __name__ == '__main__':
    main()