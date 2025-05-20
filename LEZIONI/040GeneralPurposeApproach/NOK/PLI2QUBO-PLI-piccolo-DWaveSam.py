################################################################################################
# Riduzione di un problema in PLI, con vincoli arbitrari in QUBO.
# Sviluppiamo un esempio nell stile della sezione :
# 
# "General 0/1 Programming", de:
# "Quantum Bridge Analytics I: a tutorial on formulating and using QUBO models"
# 
# Il punto fondamentale dell'esempio è trasformare disequazioni in equazioni tramite 
# l'espansione binaria di variabili slack necessarie alla trasformazione.
#
# Tecnicamente, sperimentiamo la definizione di un BQM che dipende da un parametro
# lagrangiano, da istanziare opportunamente per distanziare soluzioni da non soluzioni.
################################################################################################

from pyqubo import Binary, Placeholder, Constraint

x1, x2, x3 = Binary('x1'), Binary('x2'), Binary('x3')
y1, y2     = Binary('y1'), Binary('y2')
z1, z2     = Binary('z1'), Binary('z2')

# Hamiltoniano principale
ham_obiettivo = (10*x1 + 7*x2 + 9*x3)

# Hamiltoniani penalità
ham_penalita0  = Constraint(( 2*x1 + 3*x2 + 2*x3              - 5)**2, label='cnstr0')
ham_penalita1  = Constraint(( 3*x1 + 2*x2 + 3*x3 + (y1+ 2*y2) - 5)**2, label='cnstr1')
ham_penalita2  = Constraint(( 2*x1 + 3*x2 +   x3 - (z1+ 2*z2) - 3)**2, label='cnstr2')

# Lagrangiano inserito nel modello con il ruolo di parametro
L = Placeholder('L')

# Hamiltoniano da minimizzare
ham = -ham_obiettivo + L*ham_penalita0 + L*ham_penalita1 + L*ham_penalita2 

# Singola compilazione che produce un Hamiltoniano parametrico in L
ham_internal = ham.compile()

# BQM parametrico corrispondente
bqm = ham_internal.to_bqm(feed_dict={'L': 3})
print(" -- bqm (componenti lineari):\n", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche):\n", bqm.quadratic)    # quadratiche
print(" -- bqm (offset):\n", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento con DWaveSampler
####################################################################
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
import dwave.inspector

DWHS = EmbeddingComposite(DWaveSampler())
n_reads    = 10 # Numero di campioni prodotti
# Determina il valore massimo del bias associato agli archi del modello
max_bias = max(abs(bias) for bias in bqm.quadratic.values())
c_strength = max_bias + 1  # Se l'energia associata ad un arco che costituisce una catena
                           # non ci dovrebbero essere catene rotte, in cui il majority
                           # voting non riesce a decidere quale spin assegnare a tutti i
                           # qbit nella catena
ann_time   = 30 # Potrebbe corrispondere al parametro num_sweep di SimulatedAnnealingSampler(?) 

sampleset_DWHS = DWHS.sample(bqm, chain_strength=c_strength, num_reads=n_reads, annealing_time=ann_time)
dwave.inspector.show(sampleset_DWHS)