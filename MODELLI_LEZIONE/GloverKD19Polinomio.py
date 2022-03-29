######################################
## Versione QUBO con matrice esplicita
######################################
from pyqubo import Binary # Un modello QUBO per ogni variabile binaria [0,1]

x0, x1, x2, x3 = Binary('x0'), Binary('x1'), Binary('x2'), Binary('x3')

# Codifica (ovvia) della funzione obiettivo.
ham = -5*x0 -3*x1 -8*x2 -6*x3 \
      +4*x0*x1 +8*x0*x2 \
      +4*x1*x2 +10*x2*x3

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





