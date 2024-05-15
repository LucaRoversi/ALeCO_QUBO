# DOMANDA CGPT
# Esempio di codice che utilizza il modulo pyqubo che prima definisce una funzione obiettivo con variabili binarie, poi definisce una funzione di penalità, e infine le combina in una singola funzione per produrre un modello QUBO per dwave sdk

from pyqubo import Array, Constraint

from pyqubo import Array, Constraint

# Define binary variables
x = Array.create('x', shape=4, vartype='BINARY')

# Define the objective function
H_obj = sum(x)

# Define the penalty function for a constraint
H_penalty = Constraint((sum(x) - 2)**2, label='penalty')

# Combine the objective function and the penalty function
H = H_obj + H_penalty

# Compile the model into a QUBO model
model = H.compile()

# Get the QUBO
Q = model.to_qubo()

print(Q)

# 1. funzione obiettivo: somma delle variabili binarie nell'array `x` 
# 2. funzione penalità che penalizza le soluzioni in cui la somma delle variabili binarie non è uguale a 2. È definita, utilizzando la classe `Constraint` da `pyqubo`. 
# Al termine, funzione obiettivo e funzione penalità sono combinate in una singola funzione `H`, compilata in un modello QUBO.