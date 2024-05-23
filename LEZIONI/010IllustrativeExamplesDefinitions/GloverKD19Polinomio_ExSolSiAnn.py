###################################################################################
# Implementiamo un esempio in:
# "Quantum Bridge Analytics I: A Tutorial on Formulating and Using QUBO Models",
# ripreso anche dalle dispense, esplicitando direttamente il polinomio da
# minimizzare.
#
# L'esempio originale usa una matrice simmetrica.
###################################################################################
from pyqubo import Binary # Un modello QUBO per ogni variabile binaria [0,1]

# Elenco dei 'Binary Quadratic Model' (BQM) corrispondenti.
#
x0, x1, x2, x3 = Binary('x0'), Binary('x1'), Binary('x2'), Binary('x3')

# Funzione obiettivo.
# 
# Hamiltoniano che esprime l'energia del sistema rappresentato dal problema da risolvere.
#
ham = -5*x0 -3*x1 -8*x2 -6*x3 \
      +4*x0*x1 +8*x0*x2 \
      +4*x1*x2 +10*x2*x3

# Compilazione della funzione obiettivo in un formato interno.
# 
# Servirà per poter decodificare la struttura restituita dal campionatore
# che verrà applicato ad un 'binary quadratic model'.
#
ham_internal = ham.compile()
print("--------------------------")
print("Hamiltoniano in forma interna:\n", ham_internal)

# Da Hamiltoniano in forma interna a 'binary quadratic model'
#
from dimod import BinaryQuadraticModel
bqm = ham_internal.to_bqm()
print("--------------------------")
print("Rappresentazione BQM:\n", bqm)

# "Campionamento" spazio degli stati tramite Simulated Annealing.
#
from neal import SimulatedAnnealingSampler
SA = SimulatedAnnealingSampler()
print("--------------------------")
print("Campionamento spazio stati con Simulated Annealing:\n" \
        , SA.sample(bqm, num_reads=1, num_sweeps=100))