######################################
## Versione QUBO con matrice esplicita
# ====================================
from pyqubo import Binary # per definire un modello QUBO con variabili in [0,1]
num_vars = 4
xs = [Binary(f'x{j}') for j in range(num_vars)]
print(xs[0])

Q = {('x0','x0'): -5
    ,('x1','x1'): -3
    ,('x2','x2'): -8
    ,('x3','x3'): -6
    ,('x0','x1'):  4 
    ,('x0','x2'):  8
    ,('x1','x2'):  4
    ,('x2','x3'): 10 }
print(Q)

### Soluzione bruteforce
# ======================
from dimod import BinaryQuadraticModel
glover = BinaryQuadraticModel.from_qubo(Q)
 
from dimod import ExactSolver
def bruteforce(qubo_model):
    return ExactSolver().sample(qubo_model)
print(bruteforce(glover))


######################################
### Soluzione con  Simulated Annealing
# ====================================
import neal
sampler = neal.SimulatedAnnealingSampler()
sampleset = sampler.sample(glover, num_reads=3, num_sweeps=10)
print(sampleset)


######################################
# Versione QUBO con funzione obiettivo
# ====================================



######################################
# Versione Ising con matrice esplicita
# ====================================
