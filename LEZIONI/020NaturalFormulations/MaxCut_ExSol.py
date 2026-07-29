################################################################################
# MaxCut_ExSol.py
#
# Classroom companion for the three-vertex path discussed in MaxCut2Qubo.tex:
#
#                       b ----- c ----- d
#
# Mathematical problem:
#   Split the vertices into two sets X and Y so that the number of edges with
#   one endpoint in each set is as large as possible.
#
# Binary encoding:
#   x_v = 1  means that vertex v belongs to X;
#   x_v = 0  means that vertex v belongs to Y.
#
# One edge {u, v} crosses the cut exactly when x_u != x_v. For binary variables,
#
#   XOR(x_u, x_v) = x_u + x_v - 2*x_u*x_v.
#
# Hence the cut value and the minimization Hamiltonian are
#
#   C(x) = sum_{ {u,v} in E } (x_u + x_v - 2*x_u*x_v),
#   H(x) = -C(x).
#
# The sampler minimizes H, so an energy of -k represents a cut containing k
# edges. This script uses dimod.ExactSolver, which enumerates all assignments.
# It is a classical, deterministic reference calculation, not a quantum run.
#
# Software roles:
#   pyqubo translates the symbolic Hamiltonian into an Ocean-compatible Binary
#   Quadratic Model (BQM).
#
#   dimod supplies the BQM/SampleSet data structures and ExactSolver.
################################################################################

from dimod import ExactSolver
from pyqubo import Base, Binary


VERTICES = ('b', 'c', 'd')
EDGES = (('b', 'c'), ('c', 'd'))


def build_binary_variables(vertices):
    """Return a dictionary of pyqubo Binary variables indexed by vertex name."""

    return {vertex: Binary(vertex) for vertex in vertices}


def build_cut_value(binary_variables, edges) -> Base:
    """Return the symbolic number of edges crossing the cut.

    Each edge contributes the binary XOR polynomial

        x_u + x_v - 2*x_u*x_v.

    The resulting expression is a maximization objective.
    """

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
    """Decode a binary sample into the two sides X and Y of the cut."""

    side_x = tuple(vertex for vertex in VERTICES if sample[vertex] == 1)
    side_y = tuple(vertex for vertex in VERTICES if sample[vertex] == 0)
    return side_x, side_y


def crossing_edges(sample):
    """Return the graph edges whose endpoints lie on different cut sides."""

    return tuple(
        (u, v)
        for u, v in EDGES
        if sample[u] != sample[v]
    )


def print_bqm_components(bqm):
    """Print the BQM and connect each component to the QUBO formula.

    For H = -C on an unweighted graph:

      linear[v]       = -degree(v),
      quadratic[u, v] = 2 for every edge {u, v},
      offset           = 0.

    Thus the BQM for b--c--d has linear biases (-1, -2, -1) and two
    quadratic biases equal to 2.
    """

    print('bqm:')
    print(bqm)
    print('\n -- bqm.linear = diagonal QUBO coefficients:')
    print(sorted_linear_terms(bqm))
    print('\n -- bqm.quadratic = off-diagonal QUBO coefficients:')
    print(sorted_quadratic_terms(bqm))
    print('\n -- bqm.offset = constant term:')
    print(bqm.offset)


def print_decoded_samples(compiled_hamiltonian, sampleset):
    """Decode every exact sample through the original pyqubo model."""

    decoded_sampleset = compiled_hamiltonian.decode_sampleset(sampleset)

    print('Decoded assignments:')
    for decoded_sample in decoded_sampleset:
        sample = decoded_sample.sample
        side_x, side_y = partition_from_sample(sample)
        cut_edges = crossing_edges(sample)
        print(
            f'  sample = {sample}, X = {side_x}, Y = {side_y}, '
            f'crossing edges = {cut_edges}, '
            f'cut value = {len(cut_edges)}, energy = {decoded_sample.energy}'
        )


def print_ground_states(sampleset):
    """Print and verify all minimum-energy assignments.

    ExactSolver enumerates all 2^3 assignments. Consequently, sampleset.lowest()
    returns every optimum and proves optimality for this finite instance.
    """

    ground_sampleset = sampleset.lowest()
    minimum_energy = ground_sampleset.first.energy

    print(f'Minimum energy: {minimum_energy}')
    print(f'Maximum cut value: {-minimum_energy}')
    print('Ground states:')

    for row in ground_sampleset.data(['sample', 'energy']):
        sample = row.sample
        side_x, side_y = partition_from_sample(sample)
        cut_edges = crossing_edges(sample)

        # This assertion is an executable check of the bridge H = -C.
        assert row.energy == -len(cut_edges)

        print(
            f'  X = {side_x}, Y = {side_y}, '
            f'crossing edges = {cut_edges}, energy = {row.energy}'
        )

    print(
        'The two ground states are complementary encodings of the same '
        'unoriented cut: {c} | {b,d}.'
    )


def main():
    """Build, compile, exhaustively sample, decode, and verify the MaxCut QUBO."""

    print('## MaxCut on the path b--c--d')
    print('## Exact exhaustive sampling through dimod.ExactSolver\n')
    print(f'Vertices V = {VERTICES}')
    print(f'Edges E = {EDGES}')

    ###########################################################################
    # Step 1. Write the mathematical Hamiltonian symbolically with pyqubo.
    ###########################################################################
    binary_variables = build_binary_variables(VERTICES)
    hamiltonian = build_hamiltonian(binary_variables, EDGES)

    ###########################################################################
    # Step 2. Compile the symbolic expression.
    #
    # compile() creates pyqubo's internal representation. No sampling occurs in
    # this step.
    ###########################################################################
    compiled_hamiltonian = hamiltonian.compile()

    ###########################################################################
    # Step 3. Export the compiled expression as a dimod BQM.
    ###########################################################################
    bqm = compiled_hamiltonian.to_bqm()
    print('\n--- Binary Quadratic Model exported to Ocean/dimod ---')
    print_bqm_components(bqm)

    ###########################################################################
    # Step 4. Enumerate all binary assignments.
    #
    # ExactSolver is practical only for small instances because the number of
    # assignments grows as 2^|V|.
    ###########################################################################
    sampler = ExactSolver()
    print('\n--- Ocean sampler information ---')
    print('Sampler class: dimod.ExactSolver')
    print(f'Sampler parameters: {sampler.parameters}')

    sampleset = sampler.sample(bqm)
    print('\n--- Raw Ocean SampleSet ---')
    print(sampleset)

    ###########################################################################
    # Step 5. Decode the samples and verify energy = -(cut value).
    ###########################################################################
    print('\n--- Decoded samples ---')
    print_decoded_samples(compiled_hamiltonian, sampleset)

    print('\n--- Ground-state interpretation ---')
    print_ground_states(sampleset)


if __name__ == '__main__':
    main()
