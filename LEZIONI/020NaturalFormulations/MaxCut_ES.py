####################################################################
# Implementiamo la soluzione al problema MaxCut relativa al grafo:
# 
#              a--b--c
# 
# La  soluzione è illustrata in:
# https://drive.google.com/file/d/1XiTdpFvXEj40r5UMuuOlON4HtD5b9H5p/view?usp=sharing
#
from pyqubo import Binary, Constraint, Placeholder

a, b, c = Binary('a'), Binary('b'), Binary('c')

# Hamiltoniano completo nella rappresentazione funzionale ovvia.
#
ham  = -(a +2*b +c -2*a*b -2*b*c)

# Rappresentazione interna (D-Wave) dell'hamiltoniano.
# Servirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
#
ham_internal = ham.compile()

print("-----------------------------")
# BQM estratto dalla rappresentazione interna dell'Hamiltoniano ham.
#
bqm = ham_internal.to_bqm()
print("bqm:\n", bqm)

# Alcuni attributi del BQM.
#
print(" -- bqm (componenti lineari):\n", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche):\n", bqm.quadratic)    # quadratiche
print(" -- bqm (offset):\n", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento esaustivo
####################################################################
from dimod import ExactSolver

print("-----------------------------")
# Istanza del campionatore scelto
#
ES = ExactSolver()

print("-----------------------------")
# Campionatura sul BQM.
#
sampleset = ES.sample(bqm)
print("Sampleset:\n",sampleset)