##############################################################
## Half Adder come formalizzato in 
## Theory versus practice in annealing-based quantum computing
## Catherine C. McGeoch
##############################################################

from pyqubo import Binary # Un modello QUBO per ogni variabile binaria [0,1]

a, b, s, c = Binary('a'), Binary('b'), Binary('s'), Binary('c')

# Relazione principale tra gli input a, b dell'HA e gli output s(um) e c(arry).
# Fornisce energia minima quando i valori assunti da a, b ed i valori assunti
# da s, c sono tali che s rapperenza la somma binaria tra a, b e c rappresenta
# il riporto di tale somma.
ham_objective = a + b + s + 4*c + 2*a*b - 2*a*s - 4*a*c - 2*b*s - 4*b*c + 4*s*c

# Penalty esprime una relazione che si può osservare dalla tabella dei valori
# di verità di un Half Adder:
#
#     a  b  |  s  c
#     -------------
#     0  0  |  0  0
#     0  1  |  1  0
#     1  0  |  1  0
#     1  1  |  0  1
#
# La coppia di valori s, c è tale che s + c <= 1, che si riduce ad un classico
# prodotto, il quale vale 0 non appena una delle due variabil è 0.
ham_penalty = s * c

# Lagrangiano che accentua la non sensatezza di avere s, c entrambi a 1 
alpha = 2

# Hamiltoniano completo da minimizzare
ham = ham_objective + alpha * ham_penalty

# Rappresentazione interna (D-Wave) dell'hamoltoniano.
# Servirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
ham_internal = ham.compile()

print("--------------------------")
print("Hamiltoniano in forma interna:\n", ham_internal)

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
