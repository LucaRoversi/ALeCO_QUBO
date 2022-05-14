##############################
# Minimun Vertex Cover to QUBO
# ============================
# Risolviamo un istanza di problema, usando uno dei due grafi in 
# https://en.wikipedia.org/wiki/Vertex_cover
# 
#              c1--c3--c5
#             / |   |
#           c0  |   |
#             \ |   |
#              c2--c4
#
#

from pyqubo import Binary, Constraint, Placeholder

c0, c1, c2, c3, c4, c5 = Binary('c0'), Binary('c1'), Binary('c2'), Binary('c3'), Binary('c4'), Binary('c5')

ham_obiettivo  = c0 + c1 + c2 + c3 + c4 + c5
ham_penalita   = Constraint(1 - c0 - c1 + c0*c1, label="constr0")
ham_penalita  += Constraint(1 - c0 - c2 + c0*c2, label="constr1") 
ham_penalita  += Constraint(1 - c1 - c3 + c1*c3, label="constr2") 
ham_penalita  += Constraint(1 - c2 - c4 + c2*c4, label="constr3") 
ham_penalita  += Constraint(1 - c3 - c4 + c3*c4, label="constr4") 
ham_penalita  += Constraint(1 - c3 - c5 + c3*c5, label="constr5") 
# Istanza del Lagrangiano.
L = 2
# hamiltoniano completo nella rappresentazione funzionale ovvia.
ham = ham_obiettivo + L * ham_penalita 
# Rappresentazione interna (D-Wave) dell'hamoltoniano.
# Sercirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
ham_internal = ham.compile()

print("-----------------------------")
# BQM corrispondete all'Hamiltoniano ham.
# È nuovamente una rappresentazione interna che gioca il ruolo
# della matrice quadrata triangolare superiore, o simmetrica,
# che caratterizza una istanza QUBO.
bqm = ham_internal.to_bqm()
print("bqm: ", bqm)

# Alcuni attributi del BQM.
print(" -- bqm (componenti lineari): ", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche): ", bqm.quadratic)    # quadratiche
print(" -- bqm (offset): ", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento con ExactSolver (visita BF)
# -----------------------------------------
# Lo scopo è estrarre tutte le risposte, cioè le soluzioni che 
# soddisfano il vincolo e che hanno energia minima.
####################################################################
from neal import SimulatedAnnealingSampler

# Istanza del campionatore scelto
SA = SimulatedAnnealingSampler()

print("-----------------------------")
# Campionatura sul BQM.
sampleset = SA.sample(bqm, num_reads=10)
print("Sampleset: ",sampleset)
#       ==> [DecodedSample(decoded_subhs=[Constraint(a + b = 1,energy=1.000000)] ...
print("Lunghezza Sampleset: ", len(sampleset))

print("-----------------------------")
# Rappresentazione ad array della campionatura con attributi accessibili:
decoded_sampleset = ham_internal.decode_sampleset(sampleset)
#print("Decoded_samplset: ", decoded_sampleset)
#   - singolo campione;
#print(" -- decoded_sampleset[0]: ", decoded_sampleset[0])
#   - lista dei campioni;
#print(" -- lista dei sample estratti dal decoded_sampleset: ", [x.sample for x in decoded_sampleset])
#   - lista delle energie di ogni campione;
#print(" -- lista delle sole enerige dei sample estratti dal decoded_sampleset: ",  [x.energy for x in decoded_sampleset])
#   - lista dei vincoli di ogni campione;
#print(" -- lista dei soli constraint dei sample estratti dal decoded_sampleset: ", [x.constraints() for x in decoded_sampleset])
#   - lista dei campioni che non soddisfano il vincolo:
non_solutions = [s.sample for s in decoded_sampleset \
    if not(s.constraints().get('constr0')[0]) or \
       not(s.constraints().get('constr1')[0]) or \
       not(s.constraints().get('constr2')[0]) or \
       not(s.constraints().get('constr3')[0]) or \
       not(s.constraints().get('constr4')[0]) or \
       not(s.constraints().get('constr5')[0])]
#print(" -- lista dei sample che non soddisfano il constraint:", non_solutions)
print(" -- lunghezza della lista dei sample che non soddisfano il constraint:", len(non_solutions))

print("-----------------------------")
# Energia minima dei sample che soddisfano il constraint.
best_energy = min([s.energy for s in decoded_sampleset \
    if s.constraints().get('constr0')[0] and \
       s.constraints().get('constr1')[0] and \
       s.constraints().get('constr2')[0] and \
       s.constraints().get('constr3')[0] and \
       s.constraints().get('constr4')[0] and \
       s.constraints().get('constr5')[0]])
print("Energia minima dei sample che soddisfano il constraint: ", best_energy)

print("-----------------------------")
# Lista con tutte risposte, cioè soluzioni con energia minima che soddisfano i vincoli
answers = [s.sample for s in decoded_sampleset \
    if (s.energy == best_energy) and \
        s.constraints().get('constr0')[0] and \
        s.constraints().get('constr1')[0] and \
        s.constraints().get('constr2')[0] and \
        s.constraints().get('constr3')[0] and \
        s.constraints().get('constr4')[0] and \
        s.constraints().get('constr5')[0]]
print("Tutte e sole le risposte con energia minima {} sono {}.".format(best_energy,answers))