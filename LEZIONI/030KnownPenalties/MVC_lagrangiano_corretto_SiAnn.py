################################################################################
# Risolviamo correttamente un'istanza del problema Minimun Vertex Cover 
# relativa al grafo:
# 
#              v2--v3
#               |   | \
#               |   |  v5
#               |   | /
#              v1--v4
#
# usando un campionatore Simulated Annealing.
# L'esempio è tratto da:
# "Quantum Bridge Analytics I: A Tutorial on Formulating and Using QUBO Models".
################################################################################
from pyqubo import Binary, Constraint, Placeholder

v1, v2, v3, v4, v5 = Binary('v1'), Binary('v2'), Binary('v3'), Binary('v4'), Binary('v5')

# Hamiltoniano espresso nella forma naturale di un polinomio.
ham_obiettivo  = v1 + v2 + v3 + v4 + v5

# Elenco dei polinomi penalità con cui estenderemo l'Hamiltoniano.
ham_penalita   = Constraint(1 - v1 - v2 + v1*v2, label="constr0")
ham_penalita  += Constraint(1 - v2 - v3 + v2*v3, label="constr1") 
ham_penalita  += Constraint(1 - v3 - v4 + v3*v4, label="constr2") 
ham_penalita  += Constraint(1 - v4 - v1 + v4*v1, label="constr3") 
ham_penalita  += Constraint(1 - v3 - v5 + v3*v5, label="constr4") 
ham_penalita  += Constraint(1 - v4 - v5 + v4*v5, label="constr5") 

# Una possibile istanza corretta del Lagrangiano.
L = 2

# Hamiltoniano completo nella rappresentazione funzionale ovvia,
# con lagrangiano e penalità.
ham = ham_obiettivo + L * ham_penalita 

# Rappresentazione interna (D-Wave) dell'Hamiltoniano.
# Servirà per poter decodificare la struttura restituita dal campionatore
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
print(" -- bqm (componenti lineari):\n", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche):\n", bqm.quadratic)    # quadratiche
print(" -- bqm (offset):\n", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento con Simulated Annealing
####################################################################
from neal import SimulatedAnnealingSampler

# Istanza del campionatore scelto
SA = SimulatedAnnealingSampler()

print("-----------------------------")
# Campionatura sul BQM.
sampleset = SA.sample(bqm, num_reads=4, num_sweeps=20)
print("Sampleset:\n",sampleset)
