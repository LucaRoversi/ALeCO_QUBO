######################################
## Versione QUBO con matrice esplicita
######################################
from pyqubo import Binary # Un modello QUBO per ogni variabile binaria [0,1]
num_vars = 4

variables = [Binary(f'x{j}') for j in range(num_vars)]

# Elenco variabili appena definite
for i in variables:
    print("Variabile {}".format(i))

# Matrice QUBO
Q = {('x0','x0'): -5
    ,('x1','x1'): -3
    ,('x2','x2'): -8
    ,('x3','x3'): -6
    ,('x0','x1'):  4 
    ,('x0','x2'):  8
    ,('x1','x2'):  4
    ,('x2','x3'): 10 }
print("--------------------------")
print("Matrice QUBO:\n", Q)

# Rappresentazione interna del modello QUBO
from dimod import BinaryQuadraticModel
bqm = BinaryQuadraticModel.from_qubo(Q)
print("--------------------------")
print("Rappresentazione QUBO:\n", bqm)

# "Campionamento" esaustivo spazio degli stati
from dimod import ExactSolver
ES = ExactSolver()
print("--------------------------")
print("Visita BF spazio stati:\n", ES.sample(bqm))

# Soluzione con  Simulated Annealing
from neal import SimulatedAnnealingSampler
SA = SimulatedAnnealingSampler()
print("--------------------------")
print("Campionamento spazio stati con Simulated Annealer:\n" \
        , SA.sample(bqm, num_reads=3, num_sweeps=10))




