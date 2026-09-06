################################################################################
# MVC_lagrangiano_corretto_SiAnn.py
#
# Classroom companion to MVC_langrangiano_corretto_ExSol.py. The symbolic MVC
# model and its penalty weight are unchanged, but exhaustive enumeration is
# replaced by classical simulated annealing.
#
# QUBO objective:
#   H_2(v) = sum_i v_i + 2 * sum_(i,j) in E (1-v_i)(1-v_j).
#
# Software roles:
#   pyqubo builds and compiles the symbolic Hamiltonian.
#   dimod provides the Ocean BQM and SampleSet abstractions used indirectly.
#   neal.SimulatedAnnealingSampler is an Ocean-compatible classical heuristic.
#   It is not a quantum sampler and does not submit work to a D-Wave QPU.
#
# Unlike ExactSolver, simulated annealing neither visits every assignment nor
# proves optimality. NUM_READS controls independent attempts; NUM_SWEEPS controls
# the work in each attempt. Their balance is part of the experiment. SEED makes
# this classroom run reproducible; remove it when independent runs are desired.
################################################################################

from neal import SimulatedAnnealingSampler
from pyqubo import Binary, Constraint


VERTEX_NAMES = ('v1', 'v2', 'v3', 'v4', 'v5')
EDGES = (
    ('v1', 'v2'),
    ('v2', 'v3'),
    ('v3', 'v4'),
    ('v4', 'v1'),
    ('v3', 'v5'),
    ('v4', 'v5'),
)
PENALTY_WEIGHT = 2

# Explicit simulated-annealing experiment parameters.
NUM_READS = 20
NUM_SWEEPS = 100
SEED = 7


def build_hamiltonian():
    """Build the symbolic MVC Hamiltonian with labelled edge penalties."""

    variables = {name: Binary(name) for name in VERTEX_NAMES}

    # Start every addition from a pyqubo expression, not from the integer 0.
    cover_size = (
        variables['v1']
        + variables['v2']
        + variables['v3']
        + variables['v4']
        + variables['v5']
    )

    edge_penalties = tuple(
        Constraint(
            (1 - variables[left]) * (1 - variables[right]),
            label=f'edge_{left}_{right}',
        )
        for left, right in EDGES
    )
    uncovered_edge_penalty = (
        edge_penalties[0]
        + edge_penalties[1]
        + edge_penalties[2]
        + edge_penalties[3]
        + edge_penalties[4]
        + edge_penalties[5]
    )

    return cover_size + PENALTY_WEIGHT * uncovered_edge_penalty


def ordered_bits(sample):
    """Return a sample in the mathematical order (v1, ..., v5)."""

    return tuple(sample[name] for name in VERTEX_NAMES)


def selected_vertices(sample):
    """Decode value 1 as membership in the proposed vertex cover."""

    return tuple(name for name in VERTEX_NAMES if sample[name] == 1)


def uncovered_edges(sample):
    """Return any graph edges missed by the proposed cover."""

    return tuple(
        edge for edge in EDGES
        if sample[edge[0]] == 0 and sample[edge[1]] == 0
    )


def print_bqm_components(bqm):
    """Display the constant, linear, and quadratic parts of the Ocean BQM."""

    print('bqm:')
    print(bqm)
    print('\n -- linear coefficients:')
    print(dict(sorted(bqm.linear.items())))
    print('\n -- quadratic coefficients:')
    print(dict(sorted(bqm.quadratic.items())))
    print('\n -- constant offset:')
    print(bqm.offset)


def print_sampling_parameters():
    """Explain the two main annealing controls used in this experiment."""

    print('Class: neal.SimulatedAnnealingSampler')
    print('Parameters used:')
    print(f'  num_reads  = {NUM_READS}')
    print(f'  num_sweeps = {NUM_SWEEPS}')
    print(f'  seed       = {SEED}')
    print('Interpretation:')
    print('  more reads broaden the search across independent attempts;')
    print('  more sweeps allow deeper relaxation within each attempt;')
    print('  their useful balance is instance-dependent.')


def print_decoded_samples(compiled_hamiltonian, sampleset):
    """Decode sampled states back through the original pyqubo model."""

    print('Decoded sampled states:')
    for decoded in compiled_hamiltonian.decode_sampleset(sampleset):
        violated = tuple(
            label
            for label, (is_satisfied, _energy) in decoded.constraints().items()
            if not is_satisfied
        )
        print(
            f'  v = {ordered_bits(decoded.sample)}, '
            f'energy = {decoded.energy}, violated = {violated}'
        )


def print_best_state_interpretation(sampleset):
    """Interpret the lowest-energy states found in this stochastic run."""

    best_sampleset = sampleset.lowest()
    best_energy = best_sampleset.first.energy

    print(f'Best energy found: {best_energy}')
    print('Best states observed:')
    for row in best_sampleset.data(['sample', 'energy', 'num_occurrences']):
        print(
            f'  v = {ordered_bits(row.sample)}, '
            f'selected = {selected_vertices(row.sample)}, '
            f'uncovered = {uncovered_edges(row.sample)}, '
            f'occurrences = {row.num_occurrences}'
        )

    print('\nInterpretation:')
    if best_energy == 3 and all(
        not uncovered_edges(row.sample)
        for row in best_sampleset.data(['sample'])
    ):
        print('  This run found one or more valid minimum covers of size 3.')
    else:
        print('  This run did not establish the known ground energy 3.')
        print('  Because the sampler is heuristic, parameters or repetitions may')
        print('  need adjustment; the run alone is not a proof of optimality.')


print('## Minimum Vertex Cover: sufficient penalty')
print('## Classical heuristic sampling with simulated annealing\n')

# Step 1. Symbolic modelling with pyqubo.
hamiltonian = build_hamiltonian()

# Step 2. Compile the symbolic expression.
compiled_hamiltonian = hamiltonian.compile()

# Step 3. Export the model to an Ocean-compatible BQM.
bqm = compiled_hamiltonian.to_bqm()
print('--- Binary Quadratic Model ---')
print_bqm_components(bqm)

# Step 4. Perform 20 independent classical annealing reads. The result is an
# Ocean SampleSet, but it need not contain every state or even a true ground state.
sampler = SimulatedAnnealingSampler()
print('\n--- Sampler ---')
print_sampling_parameters()
sampleset = sampler.sample(
    bqm,
    num_reads=NUM_READS,
    num_sweeps=NUM_SWEEPS,
    seed=SEED,
)
print('\nRaw SampleSet:')
print(sampleset)

# Step 5. Decode and interpret the best states found in this experiment.
print('\n--- Decoding through pyqubo ---')
print_decoded_samples(compiled_hamiltonian, sampleset)

print('\n--- Best-state interpretation ---')
print_best_state_interpretation(sampleset)


# ##### ORIGINALE
# # ################################################################################
# # Risolviamo correttamente un'istanza del problema Minimun Vertex Cover 
# # relativa al grafo:
# # 
# #              v2--v3
# #               |   | \
# #               |   |  v5
# #               |   | /
# #              v1--v4
# #
# # usando un campionatore Simulated Annealing.
# # L'esempio è tratto da:
# # "Quantum Bridge Analytics I: A Tutorial on Formulating and Using QUBO Models".
# ################################################################################
# from pyqubo import Binary, Constraint, Placeholder

# v1, v2, v3, v4, v5 = Binary('v1'), Binary('v2'), Binary('v3'), Binary('v4'), Binary('v5')

# # Hamiltoniano espresso nella forma naturale di un polinomio.
# ham_obiettivo  = v1 + v2 + v3 + v4 + v5

# # Elenco dei polinomi penalità con cui estenderemo l'Hamiltoniano.
# ham_penalita   = Constraint(1 - v1 - v2 + v1*v2, label="constr0")
# ham_penalita  += Constraint(1 - v2 - v3 + v2*v3, label="constr1") 
# ham_penalita  += Constraint(1 - v3 - v4 + v3*v4, label="constr2") 
# ham_penalita  += Constraint(1 - v4 - v1 + v4*v1, label="constr3") 
# ham_penalita  += Constraint(1 - v3 - v5 + v3*v5, label="constr4") 
# ham_penalita  += Constraint(1 - v4 - v5 + v4*v5, label="constr5") 

# # Una possibile istanza corretta del Lagrangiano.
# L = 2

# # Hamiltoniano completo nella rappresentazione funzionale ovvia,
# # con lagrangiano e penalità.
# ham = ham_obiettivo + L * ham_penalita 

# # Rappresentazione interna (D-Wave) dell'Hamiltoniano.
# # Servirà per poter decodificare la struttura restituita dal campionatore
# # che viene applicato ad un BQM (Binary Quadratic Model).

# ham_internal = ham.compile()

# print("-----------------------------")
# # BQM corrispondete all'Hamiltoniano ham.
# # È nuovamente una rappresentazione interna che gioca il ruolo
# # della matrice quadrata triangolare superiore, o simmetrica,
# # che caratterizza una istanza QUBO.
# bqm = ham_internal.to_bqm()
# print("bqm: ", bqm)

# # Alcuni attributi del BQM.
# print(" -- bqm (componenti lineari):\n", bqm.linear)           # lineari
# print(" -- bqm (componenti quadratiche):\n", bqm.quadratic)    # quadratiche
# print(" -- bqm (offset):\n", bqm.offset)                       # scostamento costante da 0?

# ####################################################################
# # Campionamento con Simulated Annealing
# ####################################################################
# from neal import SimulatedAnnealingSampler

# # Istanza del campionatore scelto
# SA = SimulatedAnnealingSampler()

# print("-----------------------------")
# # Campionatura sul BQM.
# sampleset = SA.sample(bqm, num_reads=4, num_sweeps=20)
# print("Sampleset:\n",sampleset)
