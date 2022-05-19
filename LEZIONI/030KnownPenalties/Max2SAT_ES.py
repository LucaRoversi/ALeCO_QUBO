###################################################################################
# Implementiamo l'esempio Max2Sat sviluppato nelle note.
###################################################################################
from pyqubo import Binary # Un modello QUBO per ogni variabile binaria [0,1]

# Elenco dei 'Binary Quadratic Model' (BQM) corrispondenti.
#
x, y, z = Binary('x'), Binary('y'), Binary('z')

# Funzione obiettivo.
# 
# Hamiltoniano che esprime l'energia del sistema rappresentato dal problema da risolvere.
#
ham = 2 +y -z -x*y +x*z +y*z

# Compilazione della funzione obiettivo in un formato interno.
# 
# Servirà per poter decodificare la struttura restituita dal campionatore
# che verrà applicato ad un 'binary quadratic model'.
#
ham_internal = ham.compile()
print("--------------------------")
print("Hamiltoninao in forma interna:\n", ham_internal)

# Da Hamiltoniano in forma interna a 'binary quadratic model'
#
from dimod import BinaryQuadraticModel
bqm = ham_internal.to_bqm()
print("--------------------------")
print("Rappresentazione BQM:\n", bqm)


# "Campionamento" spazio degli stati tramite ExactSolver
#
from dimod import ExactSolver

ES = ExactSolver()
print("-----------------------------")
print("Campionamento spazio stati con ExactSolver:\n",ES.sample(bqm))

# "Campionamento" spazio degli stati tramite Simulated Annealing.
#
from neal import SimulatedAnnealingSampler
SA = SimulatedAnnealingSampler()
print("--------------------------")
print("Campionamento spazio stati con Simulated Annealing:\n" \
        , SA.sample(bqm, num_reads=1, num_sweeps=100))