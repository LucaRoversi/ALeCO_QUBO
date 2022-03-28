######################################
## Versione QUBO con matrice esplicita
######################################
from pyqubo import Binary # Un modello QUBO per ogni variabile binaria [0,1]

x1, x2, x3, x4 = Binary('x1'), Binary('x2'), Binary('x3'), Binary('x4')

# Codifica (ovvia) della funzione obiettivo.
ham = -5*x1 -3*x2 -8*x3 -6*x4 \
      +4*x1*x2 +8*x1*x3 \
      +4*x2*x3 +10*x3*x4

# Rappresentazione interna (D-Wave) dell'hamoltoniano.
# Servirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
ham_internal = ham.compile()

print("--------------------------")
print("Hamiltoninao in forma interna:\n", ham_internal)

# Rappresentazione interna del modello QUBO
from dimod import BinaryQuadraticModel
bqm = ham_internal.to_bqm()
print("--------------------------")
print("Rappresentazione QUBO:\n", bqm)

# "Campionamento" esaustivo spazio degli stati
from dimod import ExactSolver
ES = ExactSolver()
print("--------------------------")
print("Visita BF spazio stati:\n", ES.sample(bqm))





