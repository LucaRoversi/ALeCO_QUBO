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
# lagrangiano, da instanziare opportunamente per distanziare soluzioni da non soluzioni.
#
# Utile riferimento nella documentazione:
# https://pyqubo.readthedocs.io/en/latest/getting_started.html#solve-qubo-by-dimod-sampler
################################################################################################

from pyqubo import Binary, Placeholder, Constraint

x1, x2, x3 = Binary('x1'), Binary('x2'), Binary('x3')
y1, y2     = Binary('y1'), Binary('y2')
z1, z2     = Binary('z1'), Binary('z2')

# Hamiltoniano primcipale
#
ham_obiettivo = (10*x1 + 7*x2 + 9*x3)

# Hamiltoniani penalità
#
ham_penalita0  = Constraint(( 2*x1 + 3*x2 + 2*x3              - 5)**2, label='cnstr0')
ham_penalita1  = Constraint(( 3*x1 + 2*x2 + 3*x3 + (y1+ 2*y2) - 5)**2, label='cnstr1')
ham_penalita2  = Constraint(( 2*x1 + 3*x2 +   x3 - (z1+ 2*z2) - 3)**2, label='cnstr2')

# Lagrangiano inserito nel modello con il ruolo di parametro
#
L = Placeholder('L')

# Hamiltoniano da minimizzare
#
ham = -ham_obiettivo + L*ham_penalita0 + L*ham_penalita1 + L*ham_penalita2 

# Singola compilazione che produce un Hamiltoniamo parametrico in L
#
ham_internal = ham.compile()

# BQM parametrico corrispondente
#
bqm = ham_internal.to_bqm(feed_dict={'L': 2})
print(" -- bqm (componenti lineari):\n", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche):\n", bqm.quadratic)    # quadratiche
print(" -- bqm (offset):\n", bqm.offset)                       # scostamento costante da 0?

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
print("sampleset.first.energy: ", sampleset.first.energy) # per avere l'nergia del sample con energia minima.

####################################################################
# Campionamento con Simulated Annealing
####################################################################
print("-----------------------------")
from  neal import SimulatedAnnealingSampler

SA = SimulatedAnnealingSampler()
print(" SA.parameters:\n", SA.parameters)

# Campionatura sul BQM.
#
sampleset = SA.sample(bqm, num_reads=10, num_sweeps=10)
print("Sampleset:\n",sampleset)