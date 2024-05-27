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
#
ham  = -( 2*x1 + 2*x2 + 3*x3 + 3*x4 + 2*x5
         -2*x1*x2 -2*x1*x3 -2*x2*x4 
         -2*x3*x4 -2*x3*x5 -2*x4*x5        )

# Rappresentazione interna (D-Wave) dell'hamiltoniano.
# Servirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
#
ham_internal = ham.compile()
bqm = ham_internal.to_bqm()

##############################################
# Campionatore ibrido(?) con DWaveSampler
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
import dwave.inspector

DWHS = EmbeddingComposite(DWaveSampler())
n_reads    = 10 # Numero di campioni prodotti
c_strength = 1  # Più il valore è alto, più può essere difficile trovare la risposta (a causa della precisione dell'hardware?)
ann_time   = 20 # Potrebbe corrispondere al parametro num_sweep di SimulatedAnnealingSampler(?) 

sampleset_DWHS = DWHS.sample(bqm, chain_strength=c_strength, num_reads=n_reads, annealing_time=ann_time)
dwave.inspector.show(sampleset_DWHS)
