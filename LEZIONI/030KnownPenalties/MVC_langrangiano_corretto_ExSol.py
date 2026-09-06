################################################################################
# MVC_langrangiano_corretto_ExSol.py
#
# Classroom example: a correct QUBO penalty for Minimum Vertex Cover (MVC).
#
# Graph:
#
#              v2--v3
#               |   | \
#               |   |  v5
#               |   | /
#              v1--v4
#
# Binary encoding:
#   v_i = 1  means that vertex i belongs to the proposed cover;
#   v_i = 0  means that vertex i is excluded.
#
# QUBO objective:
#   H_L(v) = sum_i v_i + L * sum_(i,j) in E (1-v_i)(1-v_j).
#
# The first term counts selected vertices. Each edge term is 1 exactly when the
# edge is uncovered. Any L > 1 prevents the saving obtained by removing one
# vertex from compensating for an uncovered edge. Here L = 2 is the smallest
# integer choice with that property.
#
# Software roles:
#   pyqubo is the symbolic modelling layer. Binary and Constraint express the
#   mathematical formula; compile() prepares it for conversion and decoding.
#
#   dimod supplies the Ocean BQM, SampleSet, and ExactSolver. ExactSolver is a
#   classical exhaustive reference sampler, not a quantum or hybrid solver.
################################################################################

from dimod import ExactSolver
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


def build_hamiltonian():
    """Return the symbolic pyqubo model."""

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
    """Return the graph edges not covered by the proposed solution."""

    return tuple(
        edge for edge in EDGES
        if sample[edge[0]] == 0 and sample[edge[1]] == 0
    )


def print_bqm_components(bqm):
    """Display the BQM as constant, linear, and quadratic components."""

    print('bqm:')
    print(bqm)
    print('\n -- linear coefficients:')
    print(dict(sorted(bqm.linear.items())))
    print('\n -- quadratic coefficients:')
    print(dict(sorted(bqm.quadratic.items())))
    print('\n -- constant offset:')
    print(bqm.offset)


def print_decoded_constraints(compiled_hamiltonian, sampleset):
    """Use pyqubo labels to expose which edge constraints each state violates."""

    print('Decoded states and violated Constraint labels:')
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


def print_ground_state_interpretation(sampleset):
    """Verify that every exact ground state is a minimum vertex cover."""

    ground_sampleset = sampleset.lowest()
    minimum_energy = ground_sampleset.first.energy

    print(f'Minimum energy: {minimum_energy}')
    print(f'Number of ground states: {len(ground_sampleset)}')
    print('Ground states:')

    all_feasible = True
    for row in ground_sampleset.data(['sample', 'energy']):
        missing = uncovered_edges(row.sample)
        all_feasible = all_feasible and not missing
        print(
            f'  v = {ordered_bits(row.sample)}, '
            f'selected = {selected_vertices(row.sample)}, '
            f'uncovered = {missing}'
        )

    print('\nInterpretation:')
    if all_feasible:
        print('  Every ground state is a feasible cover of size 3.')
        print('  Exact enumeration confirms four minimum vertex covers and no')
        print('  spurious ground state.')
    else:
        print('  Unexpected result: at least one ground state is infeasible.')


print('## Minimum Vertex Cover: sufficient penalty')
print('## Classical exhaustive sampling with dimod.ExactSolver\n')

# Step 1. Write the mathematical Hamiltonian symbolically with pyqubo.
hamiltonian = build_hamiltonian()

# Step 2. Compile the symbolic expression.
compiled_hamiltonian = hamiltonian.compile()

# Step 3. Export the compiled model as an Ocean BQM.
bqm = compiled_hamiltonian.to_bqm()
print('--- Binary Quadratic Model ---')
print_bqm_components(bqm)

# Step 4. Enumerate all 2^5 states with the classical exact sampler.
sampler = ExactSolver()
print('\n--- Sampler ---')
print('Class: dimod.ExactSolver')
print(f'Parameters: {sampler.parameters}')
sampleset = sampler.sample(bqm)
print(f'Number of sampled assignments: {len(sampleset)}')

# Step 5. Decode the Ocean SampleSet and interpret the exact ground states.
print('\n--- Decoding through pyqubo ---')
print_decoded_constraints(compiled_hamiltonian, sampleset)

print('\n--- Ground-state interpretation ---')
print_ground_state_interpretation(sampleset)

# ###### ORIGINALE

# ################################################################################
# # Risolviamo correttamente un'istanza del problema Minimun Vertex Cover 
# # relativa al grafo:
# # 
# #              v2--v3
# #               |   | \
# #               |   |  v5
# #               |   | /
# #              v1--v4
# #
# # usando un campionatore esaustivo.
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
# print(" -- bqm (componenti lineari): ", bqm.linear)           # lineari
# print(" -- bqm (componenti quadratiche): ", bqm.quadratic)    # quadratiche
# print(" -- bqm (--->> OFFSET): ", bqm.offset)                 # scostamento costante da 0?

# ####################################################################
# # Campionamento con ExactSolver (visita BF)
# ####################################################################
# from dimod import ExactSolver

# # Istanza del campionatore scelto
# ES = ExactSolver()

# print("\n-----------------------------")
# # Campionatura sul BQM.
# sampleset = ES.sample(bqm)
# print("Sampleset:\n",sampleset)
# #       ==> [DecodedSample(decoded_subhs=[Constraint(a + b = 1,energy=1.000000)] ...
# print("Lunghezza Sampleset: ", len(sampleset))

# print("\n-----------------------------")
# # Rappresentazione ad array della campionatura con attributi accessibili:
# decoded_sampleset = ham_internal.decode_sampleset(sampleset)
# print("Decoded_samplset:\n", decoded_sampleset)
# #   - singolo campione;
# print("\n -- decoded_sampleset[0]: singolo campione.\n", decoded_sampleset[0])
# #   - lista dei campioni;
# #print("\n -- lista dei sample estratti dal decoded_sampleset:\n", [x.sample for x in decoded_sampleset])
# #   - lista delle energie di ogni campione;
# #print("\n -- lista delle sole energie dei sample estratti dal decoded_sampleset: ",  [x.energy for x in decoded_sampleset])
# #   - lista dei vincoli di ogni campione;
# #print("\n -- lista dei soli constraint dei sample estratti dal decoded_sampleset: ", [x.constraints() for x in decoded_sampleset])
# #   - lista dei campioni che non soddisfano il vincolo:
# non_solutions = [s.sample for s in decoded_sampleset \
#     if not(s.constraints().get('constr0')[0]) or \
#        not(s.constraints().get('constr1')[0]) or \
#        not(s.constraints().get('constr2')[0]) or \
#        not(s.constraints().get('constr3')[0]) or \
#        not(s.constraints().get('constr4')[0]) or \
#        not(s.constraints().get('constr5')[0])]
# #print(" -- lista dei sample che non soddisfano il constraint:", non_solutions)
# print("\n -- lunghezza della lista dei sample che non soddisfano almeno un vincolo:\n", len(non_solutions))

# print("\n-----------------------------")
# # Energia minima dei sample che soddisfano il constraint.
# best_energy = min([s.energy for s in decoded_sampleset \
#     if s.constraints().get('constr0')[0] and \
#        s.constraints().get('constr1')[0] and \
#        s.constraints().get('constr2')[0] and \
#        s.constraints().get('constr3')[0] and \
#        s.constraints().get('constr4')[0] and \
#        s.constraints().get('constr5')[0]])
# print("Energia minima dei sample che soddisfano almeno un vincolo:\n", best_energy)

# print("\n-----------------------------")
# # Lista con tutte risposte, cioè soluzioni con energia minima che soddisfano i vincoli
# answers = [s.sample for s in decoded_sampleset \
#     if (s.energy == best_energy) and \
#         s.constraints().get('constr0')[0] and \
#         s.constraints().get('constr1')[0] and \
#         s.constraints().get('constr2')[0] and \
#         s.constraints().get('constr3')[0] and \
#         s.constraints().get('constr4')[0] and \
#         s.constraints().get('constr5')[0]]
# print("Tutte e sole le risposte con energia minima {} che soddisfano i vincoli: {}.".format(best_energy,answers))

# print("\n-----------------------------")
# # Lista con tutte le non soluzioni (sample che non soddisfano almeno un vinvolo) 
# # ma che hanno energia minima.
# answers = [s.sample for s in decoded_sampleset \
#     if (s.energy == best_energy) and \
#         (not(s.constraints().get('constr0')[0]) or \
#         not(s.constraints().get('constr1')[0]) or \
#         not(s.constraints().get('constr2')[0]) or \
#         not(s.constraints().get('constr3')[0]) or \
#         not(s.constraints().get('constr4')[0]) or \
#         not(s.constraints().get('constr5')[0]))]
# print("Tutte e sole le *non* risposte con energia minima {}: {}.".format(best_energy,answers))