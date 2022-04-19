# https://pyqubo.readthedocs.io/en/latest/getting_started.html#solve-qubo-by-dimod-sampler

## Sviluppo dell'Esempio alla Sezione 5.3 "General 0/1 Programming", pag. 24 de
# https://arxiv.org/ftp/arxiv/papers/1811/1811.11538.pdf
# in cui si descrive in generale come passare da un porblema espresso come insieme
# di vincoli in PLI alla sua forma QUBO.
# 
# Il problema richiede di trasformare disequazioni in equazioni tramite l'espansione
# binaria delle variabili slack necessarie.
#
# Qui sperimento espansioni binarie diverse, meno efficienti, di quelle suggerite nel testo.
#
# ========================
print("## Esempio Sezione 5.3 \"General 0/1 Programming\", pag. 24 de: \" Quantum Bridge Analytics I: A Tutorial\" ")
# Il problema Number Partition non ha vincoli espliciti da trasformare in un Hamiltoniano
# penalità, da pesare per mezzo del coeffieciente Lagrangiano.
# 
# Ci concetriamo quindi su un problema diverso, con le seguenti caratteristiche:
# - 2*a + b è la funzione obiettivo,
# - a + b = 1 è il vincolo.
# L'Hamiltoniano penalità è quindi:
#       
#           (a + b − 1)**2
# 
# e l'hamiltoniano completo assume la forma:
# 
#         (2*a + b) + L * (a + b − 1)**2
#
# Tipicamente, L va trovato sperimentalmente. 

### Esprimere il Lagrangiano
# ==========================
print("### Esprimere il Lagrangiano")
from pyqubo import Binary, Placeholder, Constraint

x1, x2, x3, x4, x5 = Binary('x1'), Binary('x2'), Binary('x3'), Binary('x4'), Binary('x5')
y1, y2, y3         = Binary('y1'), Binary('y2'), Binary('y3')
z1, z2, z3, z4     = Binary('z1'), Binary('z2'), Binary('z3'), Binary('z4')

ham_obiettivo = (6*x1 + 4*x2 + 8*x3 + 5*x4 + 5*x5)
ham_penalita0  = Constraint((  x1 + 2*x2 + 2*x3 +   x4 + 2*x5                          - 4)**2, label='cnstr0')
ham_penalita1  = Constraint((2*x1 + 2*x2 + 4*x3 + 3*x4 + 2*x5 + y1+ 2*y2 + 4*y3        - 7)**2, label='cnstr1')
ham_penalita2  = Constraint((3*x1 + 3*x2 + 2*x3 + 4*x4 + 4*x5 + z1+ 2*z2 + 4*z3 + 8*z4 - 5)**2, label='cnstr2')
L = Placeholder('L')
ham = -ham_obiettivo + L * (ham_penalita0 + ham_penalita1 + ham_penalita2) 
# La compilazione avviene una sola volta ed il risultato è parametrico in L
ham_internal = ham.compile()
bqm = ham_internal.to_bqm(feed_dict={'L': 10})
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