##############################################################################################
### Riferimento https://docs.ocean.dwavesys.com/en/stable/examples/hybrid_cqm_binpacking.html
##############################################################################################

import numpy as np # user manual https://numpy.org/doc/stable/numpy-user.pdf

#########################
# Istanza del bin packing 
#########################

# Supponiamo di dove distribuire 15 colli
num_items = 15
# il cui peso varia tra 3 e 7 unità.
item_weight_range = [3, 7]
# L'assegnazione dei pesi corrisponde a generare casualmente 15 valori compresi in [3, 4, 5, 6, 7]
weights = list(np.random.randint(*item_weight_range, num_items))
# La capacità di ogni bin è stabilita essere 10 volte il peso medio dei 15 item
bin_capacity = int(10 * np.mean(weights))
print("Problem: pack a total weight of {} into bins of capacity {}.".format(sum(weights), bin_capacity))  

###################################################
# Ogni bin come variabile binaria (modello binario)
###################################################
from dimod import Binary
# Produciamo tanti bin quanti sono gli item siccome, alla peggio, dstribuiamo un item per bin.
bin_used = [Binary(f'bin_used_{j}') for j in range(num_items)]
# Ogni bin può essere considerata una variabile con la struttura di un modello binario, cioè della 
# classe BinaryQuadraticModel in https://docs.ocean.dwavesys.com/en/stable/docs_dimod/reference/quadratic.html#dimod.binary.BinaryQuadraticModel.
# Ad esempio, questo significa che i valori assunti dalle variabili è uno in {0,1}.
print (bin_used[0])
# I bin hanno tutti la stessa struttura.
print(bin_used)

####################
# Funzione obiettivo
####################
from dimod import ConstrainedQuadraticModel
# Modelliamo il problema com Constraint Quadratic Model le cui variabili anno valori binari in [0,1].
cqm = ConstrainedQuadraticModel()
# Occorre una funzione obiettivo da minimizzare.
# Essa è la somma delle varibili binarie che modellano i bin. 
# In "LaTeX" scriveremmo \sum_{i = 0}^{num_items - 1} bin_used[i].
cqm.set_objective(sum(bin_used))
# La somma si traduce in un una nuova entry del dizionario cqm che contiene tutte le variabili
# bin_used[0] ... bin_used[num_items-1]
print(cqm.objective)

####################
# Vincoli
####################
# Ogni item deve essere assegnato ad un unico bin. Lo si esprime imponendo
# item<i>_in_bin<0> + ... + item<i>_in_bin<num_item-1> = 1, per ogni item i, 
# in cui ogni item<i>_in_bin<j> è una variabile binaria.
#
# Definizione delle variabili binarie.
item_in_bin = [[Binary(f'item_{i}_in_bin_{j}') for j in range(num_items)] for i in range(num_items)]
# Un qualsiasi elemento item_in_bin[i] contiene tutte le variabili binarie item_0_in_bin_j, per ogni j
# Questo permette di definire tutti i vincoli sull'unicità di inserimento di ogni item.
for i in range(num_items):
    one_bin_per_item = cqm.add_constraint(sum(item_in_bin[i]) == 1, label=f'item_placing_{i}')

# Il peso degli item assegnati ad un bin j non può superare bin_capacity. Lo si esprime con
# item<0>_in_bin<j>*weights[0] + ... + item<num_item-1>_in_bin<j>*weights[num_item-1] <= bin_capacity, per ogni bin j, 
# in cui ogni item<i>_in_bin<j> è una variabile binaria.
for j in range(num_items):
    bin_up_to_capacity = cqm.add_constraint(
        sum(weights[i] * item_in_bin[i][j] for i in range(num_items)) - bin_used[j] * bin_capacity <= 0, label=f'capacity_bin_{j}')
# Osservazione:
# il vincolo non è 
# sum(weights[i] * item_in_bin[i][j] for i in range(num_items)) - bin_capacity <= 0
# ma:
# sum(weights[i] * item_in_bin[i][j] for i in range(num_items)) - bin_used[j] * bin_capacity <= 0



# La libreria penaltymodel a https://docs.ocean.dwavesys.com/en/stable/docs_penalty/sdk_index.html
# potrebbe fare al caso tuo per trasformare ogni vincolo in un BQM da sommare, pesato, alla
# funzione da minimizzare, così da ottenere un unico BQM.





#########################################################################
# La soluzione richiede un campionatore ibrido per cui non ho i permessi.
#########################################################################
#from dwave.system import LeapHybridCQMSampler
#resp = dimod.ExactSolver().sample(bqm)
