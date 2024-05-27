################################################################################################
# Riduzione di una istanza di KP a QUBO, secondo la riduzione suggerita da Lucas, 
# completa di variabili slack.
#
# L'istanza di riferimento di KP è:
# 
#                     |  0  |  1 |  2 |  3
#           ---------------------------------  W = 16
#           profitti  | 10  | 10 | 12 | 18
#           pesi      |  2  |  4 |  6 |  9
#           
################################################################################################
import dimod
import dwave.inspector
import dwave.system

from pyqubo import Binary, Placeholder, Constraint

# Definire parametricamente nomi di variabile.
#
x0  = Binary('x0' )
x1  = Binary('x1' )
x2  = Binary('x2' )
x3  = Binary('x3' )
y0  = Binary('y0' )
y1  = Binary('y1' )
y2  = Binary('y2' )
y3  = Binary('y3' )
y4  = Binary('y4' )

# Hamiltoniano principale
ham_obiettivo = (10*x0 +10*x1 +12*x2 +18*x3)

# Hamiltoniano penalità
ham_penalita  = \
    Constraint( ((y0 +2*y1 +4*y2 +8*y3 +16*y4) - (2*x0 +4*x1 +6*x2 +9*x3))**2, \
    label='penalita')

# Lagrangiano inserito nel modello con il ruolo di parametro
L = Placeholder('L')

# Hamiltoniano da minimizzare
ham = -ham_obiettivo + L*ham_penalita

# Singola compilazione che produce un Hamiltoniano parametrico in L
ham_internal = ham.compile()

# BQM parametrico corrispondente
bqm = ham_internal.to_bqm(feed_dict={'L': 100}) # maggiore de (miglior profitto + 1)
# print(" -- bqm (componenti lineari):\n", bqm.linear)           # lineari
# print(" -- bqm (componenti quadratiche):\n", bqm.quadratic)    # quadratiche
# print(" -- bqm (offset):\n", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento con ExactSolver (visita BF)
####################################################################
from dimod import ExactSolver

print("-----------------------------")
ES = ExactSolver()
# Parametri disponibili in ES
print(" ES.parameters:\n", ES.parameters)

print("-----------------------------")
# Campionatura sul BQM.
sampleset = ES.sample(bqm)
print("Sampleset:\n",sampleset)

print("-----------------------------")
# Energia minima dei sample che soddisfano il constraint.
#best_energy = min([s.energy for s in decoded_sampleset if (s.constraints().get('a + b = 1')[0]) ])
#print("Energia minima dei sample che soddisfano il constraint: ", best_energy)
# Un'alternativa è usare 
print("sampleset.first.energy: ", sampleset.first.energy) # per avere l'energia del sample con energia minima.

####################################################################
# Campionamento con Simulated Annealing
####################################################################
print("-----------------------------")
from  neal import SimulatedAnnealingSampler

SA = SimulatedAnnealingSampler()
# print(" SA.parameters:\n", SA.parameters)

# Campionatura sul BQM.
sampleset = SA.sample(bqm, num_reads=3, num_sweeps=10)
print("Sampleset:\n",sampleset)

##############################################
# Campionatore con DWaveSampler
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
ann_time   = 20 # Potrebbe corrispondere al parametro num_sweep di SimulatedAnnealingSampler(?) 

sampleset_DWHS = DWHS.sample(bqm, chain_strength=c_strength, num_reads=n_reads, annealing_time=ann_time)
dwave.inspector.show(sampleset_DWHS)
