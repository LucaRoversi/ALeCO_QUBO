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


# Campionatura sul BQM.
sampleset = SA.sample(bqm, num_reads=10)
print("Sampleset:\n",sampleset)
# La colonna 'num_oc.' sembra dover indicare il numero di volte che
# il sample corrispondente occorre nell'insieme di samples, ma
# stranamente(?) ad ogni sample viene contato una volta, indipendentemente
# dal fatto che nella tabella occorra più volte.

print("-----------------------------")
# Rappresentazione ad array della campionatura con attributi accessibili:
decoded_sampleset = ham_internal.decode_sampleset(sampleset)
print("Decoded_samplset: ", decoded_sampleset)
#   - singolo campione;
print(" -- decoded_sampleset[0]: ", decoded_sampleset[0])
#   - lista dei campioni;
print(" -- lista dei sample estratti dal decoded_sampleset: ", \
    [x.sample for x in decoded_sampleset])
#   - lista delle energie di ogni campione;
print(" -- lista delle sole enerige dei sample estratti dal decoded_sampleset: ",  \
    [x.energy for x in decoded_sampleset])
#   - lista dei vincoli di ogni campione;
print(" -- lista dei soli constraint dei sample estratti dal decoded_sampleset: ", \
     [x.constraints() for x in decoded_sampleset])
#   - lista dei campioni che non soddisfano il vincolo:
#       -- {'b': 0, 'a': 0} se il vincolo non è soddisfatto;
#       -- None             se il vincolo     è soddisfatto.
print(" -- lista dei sample che non soddisfano il constraint:", \
    [s.sample for s in decoded_sampleset if not(s.constraints().get('a + b = 1')[0])])
# Secondo:
# https://docs.ocean.dwavesys.com/en/latest/docs_dimod/reference/generated/dimod.SampleSet.filter.html
# se il sampleset offre l'attributo 'is_feasible', che indica se ilsample soddisfa i constraint,
# si può usare:
#feasible_sampleset = sampleset.filter(lambda d: d.is_feasible)

print("-----------------------------")
# Energia minima dei sample che soddisfano il constraint.
best_energy = min([s.energy for s in decoded_sampleset if (s.constraints().get('a + b = 1')[0]) ])
print("Energia minima dei sample che soddisfano il constraint: ", best_energy)
# Un'alternativa è usare 
# print(sampleset.first.energy) per avere l'ergia del sample con energia minima.

print("-----------------------------")
# Lista con tutte risposte, cioè soluzioni con energia minima che soddisfano i vincoli
answers = [s.sample for s in decoded_sampleset if (s.energy == best_energy) and (s.constraints().get('a + b = 1')[0])]
print("Tutte e sole le risposte con energia minima {} sono {}.".format(best_energy,answers))