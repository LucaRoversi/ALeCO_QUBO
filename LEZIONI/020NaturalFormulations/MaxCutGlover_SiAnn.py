####################################################################
# Implementiamo la soluzione al problema MaxCut relativa al grafo:
# 
#              1-----2
#              |     |
#              3-----4
#               \   /
#                 5
#
# illustrata in:
# "Quantum Bridge Analytics I: A Tutorial on Formulating and Using QUBO Models".


from pyqubo import Binary, Constraint, Placeholder
x1, x2, x3, x4, x5 = Binary('x1'), Binary('x2'), Binary('x3'), Binary('x4'), Binary('x5')

# Hamiltoniano completo nella rappresentazione funzionale ovvia.
ham  = -( 2*x1 + 2*x2 + 3*x3 + 3*x4 + 2*x5
         -2*x1*x2 -2*x1*x3 -2*x2*x4 
         -2*x3*x4 -2*x3*x5 -2*x4*x5        )

# Rappresentazione interna (D-Wave) dell'hamiltoniano.
# Servirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
ham_internal = ham.compile()

print("-----------------------------")
# BQM estratto dalla rappresentazione interna dell'Hamiltoniano ham.
bqm = ham_internal.to_bqm()

####################################################################
# Campionamento con Simulated Annealing
####################################################################
from neal import SimulatedAnnealingSampler

# Istanza del campionatore scelto
SA = SimulatedAnnealingSampler()

print("-----------------------------")
# Campionatura sul BQM.

n_reads  = 10
n_sweeps = 1
sampleset_SA = SA.sample(bqm, num_reads=n_reads, num_sweeps=n_sweeps)
print("Sampleset:\n",sampleset_SA)

# Le risposte sono il seguente grafo e quello che si ottiene
# per riflessione rispetto all'asse di simmetria verticale:
#
#              X    Y
#              1----2
#               \  /
#                \/
#                /\
#               /  \
#              4----3
#              |   /
#              |  /
#              | /
#              |/
#              5
#
# Il numero di archi a "cavallo del taglio" corrisponde 
# all'energia calcolata.