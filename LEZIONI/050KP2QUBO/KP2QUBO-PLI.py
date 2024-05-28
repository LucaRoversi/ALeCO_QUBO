################################################################################################
# Riduzione di una istanza di KP a QUBO, vedendo KP come problema in PLI.
# L'obiettivo è quindi minimizzare il polinomio lineare dei profitti controbilanciando
# i valori che esso assume con un polinomio penalità ricavato dal vincolo sullo spazio
# disponibile.
#
# L'istanza di riferimento di KP è:
# 
#                     |  0  |  1 |  2 |  3
#           ---------------------------------  W = 16
#           profitti  | 10  | 10 | 12 | 18
#           pesi      |  2  |  4 |  6 |  9
#           
# Per ridurre il numero di slack variables necessarie a trasformare il vincolo:
# 
#           2*x1 +4*x2 +6*x3 +9*x4 <= 16
# 
# in eguaglianza, ipotizziamo che il profitto non sarà mai inferiore a quello 
# offerto dal Greedy-split. Ipotizzando l'ordine di inserimento:
#
#        0      1      2      3
#
#      10/2 > 10/4 > 12/2 = 18/2
#
# Greedy-split inserisce i tre elementi 0, 1 e 2, occupando 12 unità con 
# profitto 32. Lo spazio residuo da riempire per arrivare a 16 è 4.
# Quindi tre variabili slack s0, s1 e s2 son sufficienti a coprire almeno
# la differenza tra lo riempimento dello Greedy-split e il massimo consentito.
################################################################################################
from pyqubo import Binary, Placeholder, Constraint

x0, x1, x2, x3  = Binary('x0'), Binary('x1'), Binary('x2'), Binary('x3')
s0, s1, s2      = Binary('s0'), Binary('s1'), Binary('s2')

# Hamiltoniano principale
ham_obiettivo = (10*x0 + 10*x1 + 12*x2 + 18*x3)

# Hamiltoniani penalità
ham_penalita  = Constraint((16 - (2*x0 + 4*x1 + 6*x2 + 9*x3 \
                                  + s0 + 2*s1 + 4*s2))**2,  \
                label='cnstr0')

# Lagrangiano inserito nel modello con il ruolo di parametro
L = Placeholder('L')

# Hamiltoniano da minimizzare
ham = -ham_obiettivo + L*ham_penalita

# Singola compilazione che produce un Hamiltoniano parametrico in L
ham_internal = ham.compile()

# BQM parametrico corrispondente
bqm = ham_internal.to_bqm(feed_dict={'L': 40})
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

###############################################
# Risultati al variare di L.
#
# Con L = 2:
# s0 s1 s2 x0 x1 x2 x3 energy 
# 0   0  0  1  0  1  1  -38.0 ===> profitto 10+12+18 = 40 con peso 2+6+9 = 17 <-- non soluzione
# 1   0  0  1  1  0  1  -38.0 ===> profitto 10+10+18 = 38 con peso 2+4+9 = 15 <-- risposta
#
# Con L = 3:
# s0 s1 s2 x0 x1 x2 x3 energy 
# 1   0  0  1  1  0  1  -38.0 ===> profitto 10+10+18 = 38 con peso 1+2+4+9 = 16 <-- risposta
# 0   0  0  1  0  1  1  -37.0 ===> profitto 10+12+18 = 40 con peso 0+2+6+9 = 17 <-- non soluzione
#
# Sembra che ponendo il lagrangiano almeno a 3, otteniamo dia già sufficiente a ottenere la risposta.
# Una valutazione più "sofisticata" su come determinare il valore del Lagrangiano è sulle dispense. 
###################################################################

####################################################################
# Campionamento con Simulated Annealing
####################################################################
print("-----------------------------")
from  neal import SimulatedAnnealingSampler

SA = SimulatedAnnealingSampler()
# print(" SA.parameters:\n", SA.parameters)

# Campionatura sul BQM.
sampleset = SA.sample(bqm, num_reads=10, num_sweeps=100)
print("Sampleset:\n",sampleset)

####################################################################
# Campionatore con DWaveSampler
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
ann_time   = 20 # Potrebbe corrispondere al parametro num_sweep di SimulatedAnnealingSampler(?) 

sampleset_DWHS = DWHS.sample(bqm, chain_strength=c_strength, num_reads=n_reads, annealing_time=ann_time)
dwave.inspector.show(sampleset_DWHS)