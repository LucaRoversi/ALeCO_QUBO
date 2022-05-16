##############################
# Minimun Vertex Cover to QUBO
# ============================
# Risolviamo un istanza di problema, usando uno dei due grafi in 
# https://en.wikipedia.org/wiki/Vertex_cover
# 
#              1-----2
#              |     |
#              3-----4
#               \   /
#                 5

from pyqubo import Binary, Constraint, Placeholder

x1, x2, x3, x4, x5 = Binary('x1'), Binary('x2'), Binary('x3'), Binary('x4'), Binary('x5')

ham  = -( 2*x1 + 2*x2 + 3*x3 + 3*x4 + 2*x5
         -2*x1*x2 -2*x1*x3 -2*x2*x4 
         -2*x3*x4 -2*x3*x5 -2*x4*x5        )

# Rappresentazione interna (D-Wave) dell'hamoltoniano.
# Sercirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
ham_internal = ham.compile()
bqm = ham_internal.to_bqm()

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
sampleset = SA.sample(bqm, num_reads=2, num_sweeps=10)
print("Sampleset:\n",sampleset)
