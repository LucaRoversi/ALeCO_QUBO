# DOMANDE CGPT
# 1. Riformula l'esempio funzionante per pyqubo in uno equivalente che usa solo moduli e classi di dwave sdk per python 3.11.
# 2. All'esempio precedente aggiungi la stampa del modello bqm, prima che venga risolto.
# 3. The added command rises an error saying that type object 'BinaryQuadraticModel' has no attribute 'from_csp'

from dimod import ExactSolver
from dwavebinarycsp import ConstraintSatisfactionProblem, stitch

# Define binary variables
variables = ['q1', 'q2', 'q3', 'q4']

# Create a Constraint Satisfaction Problem (CSP)
csp = ConstraintSatisfactionProblem('BINARY')

# Define the objective function as a constraint
def objective(q1, q2, q3, q4):
    return q1 + q2 + q3 + q4 == 2
csp.add_constraint(objective, variables)

# Define the penalty function as a constraint
def penalty(q1, q2, q3, q4):
    return q1 + q2 + q3 + q4 != 2
csp.add_constraint(penalty, variables)

# Convert the CSP to a Binary Quadratic Model (BQM) using the 'stitch' function
bqm = stitch(csp)

# Print the BQM
print("Binary Quadratic Model:")
print(bqm)

# Create an exact solver to solve the BQM
solver = ExactSolver()

# Solve the BQM
solution = solver.sample(bqm)

# Print the solution
print("\nSolution:")
print(solution)

# 1. la funzione obiettivo è la somma delle variabili binarie q1, q2, q3, q4 che deve essere uguale a 2
# 2. una funzione penalitàç penalizza soluzioni in cui la somma delle variabili binarie non è uguale a 2. 
# Entrambe le funzioni sono sommate come vincoli al CSP. 
# Il CSP viene quindi convertito in un BQM risolto da un `ExactSolver` senza l'ausilio di QCPU.