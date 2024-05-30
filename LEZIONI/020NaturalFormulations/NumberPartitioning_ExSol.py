#################################################################################
# Implementiamo la soluzione per una istanza del  problema "Number Partitioning", 
# già visto come "Sottoinsiemi a Somma Identica",  da:
# "Quantum Bridge Analytics I: A Tutorial on Formulating and Using QUBO Models",
#
# Sviluppiamo due istanze, una caratterizzata da un insieme di due risposte,
# l'altra dal non avere alcuna risposta. 
#################################################################################
print("## \"Number Partitioning Problem\" o \"Sottoinsiemi a Somma Identica\"\n")

from pyqubo import Binary, Constraint, Placeholder
x1, x2, x3, x4, x5 = Binary('x1'), Binary('x2'), Binary('x3'), Binary('x4'), Binary('x5')

################################################################################ 
# Prima istanza: due risposte
################################################################################ 
v1 = 1
v2 = 3
v3 = 4
v4 = 2
v5 = 6

# Hamiltoniano completo nella rappresentazione funzionale ovvia.
ham = ((v1+v2+v3+v4+v5) - 2*(x1*v1+x2*v2+x3*v3+x4*v4+x5*v5))**2

# Rappresentazione interna (D-Wave) dell'Hamiltoniano.
# Servirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
ham_internal = ham.compile()

print("-----------------------------")
# BQM estratto dalla rappresentazione interna dell'Hamiltoniano ham.
bqm = ham_internal.to_bqm()
print("bqm:\n", bqm)

# Alcuni attributi del BQM.
print(" -- bqm (componenti lineari):\n", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche):\n", bqm.quadratic)    # quadratiche
print(" -- bqm (offset):\n", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento con ExactSolver (visita BF)
####################################################################
from dimod import ExactSolver

print("-----------------------------")
# Istanza del campionatore.
ES = ExactSolver()
print("ES.parameters:\n", ES.parameters)

print("-----------------------------")
# Campionatura sul BQM.
sampleset = ES.sample(bqm)
print("Sampleset:\n",sampleset)
#       ==> [DecodedSample(decoded_subhs=[Constraint(a + b = 1,energy=1.000000)] ...

print("-----------------------------")
# Rappresentazione ad array della campionatura con attributi accessibili:
decoded_sampleset = ham_internal.decode_sampleset(sampleset)
print("Decoded_samplset: ", decoded_sampleset)
#   - singolo campione;
print(" -- lista dei sample estratti dal decoded_sampleset: ", \
    [x.sample for x in decoded_sampleset])


################################################################################ 
# Seconda istanza: no risposte
################################################################################ 
# v1 ha ancora valore 1 
v2 = 1
v3 = 1
v4 = 1
v5 = 1

# Hamiltoniano completo nella rappresentazione funzionale ovvia.
ham = ((v1+v2+v3+v4+v5) - 2*(x1*v1+x2*v2+x3*v3+x4*v4+x5*v5))**2

# Rappresentazione interna (D-Wave) dell'Hamiltoniano.
# Servirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
ham_internal = ham.compile()

print("-----------------------------")
# BQM corrispondete all'Hamiltoniano ham.
# È nuovamente una rappresentazione interna che gioca il ruolo
# della matrice quadrata triangolare superiore, o simmetrica,
# che caratterizza una istanza QUBO.
bqm = ham_internal.to_bqm()
print("bqm:\n", bqm)

# Alcuni attributi del BQM.
print(" -- bqm (componenti lineari):\n", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche):\n", bqm.quadratic)    # quadratiche
print(" -- bqm (--->> OFFSET):\n", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento con ExactSolver (visita BF)
####################################################################
from dimod import ExactSolver

print("-----------------------------")
# Istanza del campionatore scelto
ES = ExactSolver()
print("ES.parameters:\n", ES.parameters)

print("-----------------------------")
# Campionatura sul BQM.
sampleset = ES.sample(bqm)
print("Sampleset:\n",sampleset)
#       ==> [DecodedSample(decoded_subhs=[Constraint(a + b = 1,energy=1.000000)] ...

print("-----------------------------")
# Rappresentazione ad array della campionatura con attributi accessibili:
decoded_sampleset = ham_internal.decode_sampleset(sampleset)
print("Decoded_samplset:\n", decoded_sampleset)
#   - singolo campione;
print(" -- lista dei sample estratti dal decoded_sampleset:\n", \
    [x.sample for x in decoded_sampleset])
