# https://pyqubo.readthedocs.io/en/latest/getting_started.html#solve-qubo-by-dimod-sampler

## Sviluppo di un esercizio simile nello spirito, ma più maneggevole, dell'Esempio alla Sezione 5.3 
# "General 0/1 Programming", pag. 24 de https://arxiv.org/ftp/arxiv/papers/1811/1811.11538.pdf .
# Lo scopo è passare da un problema espresso come insieme di vincoli in PLI alla sua forma QUBO.
# 
# Il punto fondamentale è trasformare disequazioni in equazioni tramite l'espansione binaria di 
# variabili slack necessarie alla trasformazione.
#
# ========================
print("## Esempio simile a quello in Sezione 5.3 \"General 0/1 Programming\"")
print(" pag. 24 de: \" Quantum Bridge Analytics I: A Tutorial\"")

# ==========================
from pyqubo import Binary, Placeholder, Constraint

x1, x2, x3 = Binary('x1'), Binary('x2'), Binary('x3')
y1, y2     = Binary('y1'), Binary('y2')
z1, z2     = Binary('z1'), Binary('z2')

ham_obiettivo = (10*x1 + 7*x2 + 9*x3)
ham_penalita0  = Constraint(( 2*x1 + 3*x2 + 2*x3              - 5)**2, label='cnstr0')
ham_penalita1  = Constraint(( 3*x1 + 2*x2 + 3*x3 + (y1+ 2*y2) - 5)**2, label='cnstr1')
ham_penalita2  = Constraint(( 2*x1 + 3*x2 +   x3 - (z1+ 2*z2) - 3)**2, label='cnstr2')
L = Placeholder('L')
ham = -ham_obiettivo + L*ham_penalita0 + L*ham_penalita1 + L*ham_penalita2 
# La compilazione avviene una sola volta ed il risultato è parametrico in L
ham_internal = ham.compile()
bqm = ham_internal.to_bqm(feed_dict={'L': 2})
print(" -- bqm (componenti lineari): ", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche): ", bqm.quadratic)    # quadratiche
print(" -- bqm (offset): ", bqm.offset)                       # scostamento costante da 0?


####################################################################
# Campionamento con ExactSolver (visita BF)
# -----------------------------------------
# Lo scopo è estrarre tutte le risposte, cioè le soluzioni che 
# soddisfano il vincolo e che hanno energia minima.
####################################################################
from dimod import ExactSolver

print("-----------------------------")
# Istanza del campionatore scelto
ES = ExactSolver()
print(" ES.parameters: ", ES.parameters)


print("-----------------------------")
# Campionatura sul BQM.
sampleset = ES.sample(bqm)
print("Sampleset:\n",sampleset)

print("-----------------------------")
# Energia minima dei sample che soddisfano il constraint.
#best_energy = min([s.energy for s in decoded_sampleset if (s.constraints().get('a + b = 1')[0]) ])
#print("Energia minima dei sample che soddisfano il constraint: ", best_energy)
# Un'alternativa è usare 
print("sampleset.first.energy: ", sampleset.first.energy) # per avere l'nergia del sample con energia minima.

print("-----------------------------")
from  neal import SimulatedAnnealingSampler

# Istanza del campionatore scelto
SA = SimulatedAnnealingSampler()
print(" SA.parameters: ", SA.parameters)

# Campionatura sul BQM.
sampleset = SA.sample(bqm, num_reads=10)
print("Sampleset:\n",sampleset)