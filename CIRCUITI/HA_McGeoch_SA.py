##############################################################
## Half Adder come formalizzato in 
## Theory versus practice in annealing-based quantum computing
## Catherine C. McGeoch
##
## Somma due bit a, b, fissati, usando SA come campionatore.
## Lo scopo è evidenziare il comportamento aleatorio di SA.
##
## Siccome SA ha un comportamento aleatorio, occorre un certo 
## numero di tentativi per avere l'istanza della relazione 
## con a, b e la corrispondente coppia s, c.
## 
## Il campionamento con SA avviene per tentativi, con
## un solo ciclo di campionamenti per volta, finché non 
## viene campionata l'istanza cercata.
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

print("-----------------------------")
# BQM corrispondete all'Hamiltoniano ham.
# È nuovamente una rappresentazione interna che gioca il ruolo
# della matrice quadrata triangolare superiore, o simmetrica,
# che caratterizza una istanza QUBO.
bqm = ham_internal.to_bqm()
print("bqm: ", bqm)

print("--------------------------")
print("Hamiltoniano in forma interna:\n", ham_internal)


####################################################################
# Campionamento con ExactSolver (visita BF)
# -----------------------------------------
# Lo scopo è estrarre tutte le risposte, cioè le soluzioni che 
# soddisfano il vincolo e che hanno energia minima.
####################################################################
from neal import SimulatedAnnealingSampler
print("-----------------------------")
# Istanza del campionatore scelto
SA = SimulatedAnnealingSampler()
print(" SA.parameters: ", SA.parameters)

####################################
# Calcola la somma dei due bit a e b
a, b = 0, 1

num_reads_count = 1
num_iter = 0
found = False
while (not found):
    # Campionatura sul BQM.
    sampleset = SA.sample(bqm, num_reads=num_reads_count)
    print(sampleset)
    decoded_sampleset = ham_internal.decode_sampleset(sampleset)
    bit_sum = [x.sample for x in decoded_sampleset if (x.sample["a"] == a) and (x.sample["b"] == b)]
    found = not(bit_sum == [])
    num_iter += 1
    # nnum_reads_count = num_reads_count + 1 # decommentare se ad ogni iterazione
                                             # si vuole incrementare il numero di
                                             # campioni generati

print("{}+{} = (s:{}, c:{}) con {} tentativi".format(str(a),str(b),str(bit_sum[0]["s"]),str(bit_sum[0]["c"]),str(num_iter)))
