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
# eguaglianza, immaginiam di applicare Greedy-split. L'ordine di inserimento ipotizzato è:
#
#                       3, 2, 0, 1
#
# perché a parità di profitto per unità di misura privilegiamo l'elemento che occupa 
# maggiore volume. Grredy-split inserisce i due elementi 3, 2, con un'occupazione pari a 15
# ed un profitto pari a 30.
# Serve quindi una sola variabile slack s.
################################################################################################

from pyqubo import Binary, Placeholder, Constraint

x0, x1, x2, x3  = Binary('x0'), Binary('x1'), Binary('x2'), Binary('x3')
s               = Binary('s')

# Hamiltoniano principale
#
ham_obiettivo = (10*x0 + 10*x1 + 12*x2 + 18*x3)

# Hamiltoniani penalità
#
ham_penalita  = Constraint((16 - (2*x0 + 4*x1 + 6*x2 + 9*x3 + s))**2, label='cnstr0')

# Lagrangiano inserito nel modello con il ruolo di parametro
#
L = Placeholder('L')

# Hamiltoniano da minimizzare
#
ham = -ham_obiettivo + L*ham_penalita

# Singola compilazione che produce un Hamiltoniamo parametrico in L
#
ham_internal = ham.compile()

# BQM parametrico corrispondente
#
bqm = ham_internal.to_bqm(feed_dict={'L': 20})
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
#
print(" ES.parameters:\n", ES.parameters)

print("-----------------------------")
# Campionatura sul BQM.
#
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
# Con L = 1
# s x0 x1 x2 x3 energy
# 0  1  0  1  1  -39.0 ===> profitto 10+12+18 con peso 0+2+6+9 = 17 <-- proposta come risposta errata
# 1  1  1  0  1  -38.0 ===> profitto 10+10+18 con peso 1+2+4+9 = 16 <-- sarebbe la risposta
#
# Con L = 2:
#  s x0 x1 x2 x3 energy 
#  1  1  1  0  1  -38.0 ===> profitto 10+10+18 con peso 1+2+4+9 = 16 <-- e la risposta
#  0  1  0  1  1  -38.0 ===> profitto 10+12+18 con peso 0+2+6+9 = 17 <-- proposta come risposta errata
#
# Con L = 3:
#  s x0 x1 x2 x3 energy 
#  1  1  1  0  1  -38.0 ===> profitto 10+10+18 con peso 1+2+4+9 = 16 <-- unica risposta
#  0  1  0  1  1  -37.0 ===> profitto 10+12+18 con peso 0+2+6+9 = 17 <-- non più risposta
#
# Quindi, con una sola variabile slack, la cui necessità abbiamo 
# giustificato tramite l'applicazione dell'algoritmo Greedy-split
# ponendo il lagrangiano almeno a 3, otteniamo la risposta.
#
# Siccome:
# - un'euristica derivata dall'esprienza  suggerisce di fissare un valore del lagrangiano 
# in un intervallo che varia tra il 70% ed il 150% del valore del polinomio da minimizzare,
# - la stima del profitto ottimale fornita dall'algoritmo Greedy-split è 30,
# proviamo a fissare L = 30.
#
# Nonostante questo tentativo, il campionamento tramite Simulated Annealing che segue,
# non sembra del tutto stabile ed affidabile.
###################################################################

####################################################################
# Campionamento con Simulated Annealing
####################################################################
print("-----------------------------")
from  neal import SimulatedAnnealingSampler

SA = SimulatedAnnealingSampler()
# print(" SA.parameters:\n", SA.parameters)

# Campionatura sul BQM.
#
sampleset = SA.sample(bqm, num_reads=3, num_sweeps=10)
print("Sampleset:\n",sampleset)