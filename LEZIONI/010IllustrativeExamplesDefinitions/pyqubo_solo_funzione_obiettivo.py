
## Uso basilare di pyqubo 
# =======================
print("## Uso basilare di pyqubo")

# https://pyqubo.readthedocs.io/en/latest/getting_started.html#solve-qubo-by-dimod-sampler


### Creare l'Hamiltoniano in modo ovvio
# =====================================
print("### Creare l'Hamiltoniano in modo ovvio")
# Ne creiamo uno relativo al problema Number Partitioning del quale consideriamo
# l'istanza S = {4, 2, 6}.
#
# Ricordiamo che, dato S, il problema richiede di trovare due sottoinsiemi
# X, Y che siano una partizione di S, tale che la somma degli elementi in
# X eguagli la somma degli elementi in Y.
#
# Il modo naturale di risolverlo è:
# - assegnare il seguente significato alle seguenti variabili:
#   - x = 1 se 4 appartiene a X, x = 0 se 4 appartiene a Y
#   - y = 1 se 2 appartiene a X, y = 0 se 2 appartiene a Y
#   - z = 1 se 6 appartiene a X, z = 0 se 6 appartiene a Y
# - scrivere la funzione obiettivo che determina l'equivalenza tra la somma
# degli elementi in X e la somma degli elementi in Y:
# 
#       4*x + 2*y + 6*z = 4*(1-x) + 2*(1-y) + 6*(1-z)           <==>
#       4*x + 2*y + 6*z - 4*(1-x) - 2*(1-y) - 6*(1-z) = 0     <==>
#       2*4*x + 2*2*y + 2*6*z -4 -2 -6 = 0

from pyqubo import Binary # per definire un modello QUBO con variabili in [0,1]

# Definiamo un Hamiltoniano di base per ogni variabile del problema, imponendo
# che i valori delle variabili siano in [0,1].

x, y, z = Binary('x'), Binary('y'), Binary('z')

# Esprimiamo l'Hamiltoniano in maniera implicita, cioè come quadrato della
# differenza tra parte sinistra e parte destra dell'equazione che vogliamo
# soddisfare.

ham_implicit = (4*x + 2*y + 6*z - 4*(1-x) - 2*(1-y) - 6*(1-z))**2

# Compiliamo l'Hamiltoniano in forma implicita nel corrispondente modello QUBO.

qubo_implicit = ham_implicit.compile()

# Il modello QUBO è caratterizzato da una matrice triangolare superiore ricavabile
# sotto forma di dizionario.

num_partition = qubo_implicit.to_bqm()
print(num_partition)
# ==> {'y'       : -80.0,        'x': -128.0,        'z': -144.0},
#     {('x', 'y'):  64.0, ('z', 'y'):   96.0, ('z', 'x'):  192.0}
# nel quale si possono apprezzare i coefficienti della matrice triangolare superiore.
# È possibile distinguere tra le componenti lineari e quadratiche.

print("Componenti lineari: ", num_partition.linear)
print("Componenti quadratiche: ", num_partition.quadratic)

# L'offset è il valore cui ammonta la costante dello sviluppo del polinomio:
# 
#            (4*x + 2*y + 6*z - 4*(1-x) - 2*(1-y) - 6*(1-z))**2 
#
print("Offset: ", num_partition.offset)  # ==> 144.0 


### Soluzione bruteforce di num_partition
# =======================================
print("### Soluzione bruteforce di num_partition")

# ExactSolver sviluppa le risposte con la visita esaustiva dello spazio degli stati.

from dimod import ExactSolver

def bruteforce_num_partition(qubo_model):
    return ExactSolver().sample(qubo_model) # bruteforce non è un vero campionamento
                                            # siccome ricerca esaustivamente 

print(bruteforce_num_partition(num_partition))


### Soluzione tramite Simulated Annealing di num_partition
# ========================================================
print("### Soluzione tramite Simulated Annealing di num_partition")

import neal
sa = neal.SimulatedAnnealingSampler()
sampleset = sa.sample(num_partition, num_reads=10)
decoded_samples = qubo_implicit.decode_sampleset(sampleset)
best_sample = min(decoded_samples, key=lambda x: x.energy)
print(best_sample.sample)
# ==> {'x': 1, 'y': 0, 'z': 0}