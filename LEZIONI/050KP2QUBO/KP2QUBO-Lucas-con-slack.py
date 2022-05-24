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

from pyqubo import Binary, Placeholder, Constraint
num_variables = 4
num_slack     = 16

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
#
ham_obiettivo = (10*x0 +10*x1 +12*x2 +18*x3)

# Hamiltoniano penalità
#
ham_penalita  = \
    Constraint( ((y0 +2*y1 +4*y2 +8*y3 +16*y4) - (2*x0 +4*x1 +6*x2 +9*x3))**2 + (1-(y0+y1+y2+y3+y4))**2, \
    label='cnstr0')

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
bqm = ham_internal.to_bqm(feed_dict={'L': 50})
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