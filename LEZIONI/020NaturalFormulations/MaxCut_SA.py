####################################################################
# Implementiamo la soluzione al problema MaxCut relativa al grafo:
# 
#              a--b--c
# 
# La  soluzione è illustrata in:
# https://drive.google.com/file/d/1XiTdpFvXEj40r5UMuuOlON4HtD5b9H5p/view?usp=sharing
#
from pyqubo import Binary, Constraint, Placeholder

a, b, d = Binary('a'), Binary('b'), Binary('d')

# Hamiltoniano completo nella rappresentazione funzionale ovvia.
#
ham  = -(a +2*b +d -2*a*b -2*b*d)

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
# Campionamento con Simulated Annealing
####################################################################
from neal import SimulatedAnnealingSampler

# Istanza del campionatore scelto
#
SA = SimulatedAnnealingSampler()

print("-----------------------------")
# Campionatura sul BQM.
#
sampleset = SA.sample(bqm, num_reads=2, num_sweeps=3)
print("Sampleset:\n",sampleset)
#       ==> [DecodedSample(decoded_subhs=[Constraint(a + b = 1,energy=1.000000)] ...
print("Lunghezza Sampleset: ", len(sampleset))

print("-----------------------------")
# Rappresentazione ad array della campionatura con attributi accessibili:
decoded_sampleset = ham_internal.decode_sampleset(sampleset)
