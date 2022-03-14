##################################
# # penaltymodel https://docs.ocean.dwavesys.com/en/stable/docs_penalty/sdk_index.html
##################################

# Un approccio per risolvere un constraint satisfaction problem (CSP),
# consiste nel ridurre ogni singolo vincolo del CSP ad un modello Ising/QUBO
# di dimensioni contenute. 
# Per convenzione, chiamiamo "modello penalità" il modello Ising/QUBO risultate.

# Per semplicità, supponiamo di voler ridurre la rappresentazione della funzione 
# booleana AND, data in termini di un polinomio, ad un modello QUBO. 
# Come al solito, lo scopo è che tutte e sole le risposte del modello QUBO, cioè le 
# soluzioni minimizzano l'energia, corrispondono ad istanza della relazione che esprime
# la dipendenza I/O dell'operatore AND. 

# Cominciamo con l'importare i package necessari.

import penaltymodel.core as pm
import dimod
import networkx as nx

# Vedendo AND come relazione ternaria:
#
#        x1 x2 z
#       ----------------------------------------
#         0  0 0  <-- deve avere energia minima
#         0  0 1
#         0  1 0  <-- deve avere energia minima
#         0  1 1
#         1  0 0  <-- deve avere energia minima
#         1  0 1
#         1  1 0  
#         1  1 1  <-- deve avere energia minima
#
# sappiamo decidere quali sono le terne che, in una rappresenzatione
# Ising/QUBO devono avere energia minima.

answers = {(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)}

# Costruire il modello Ising/QUBO coincide col determinare la struttura del grafo
# di relazioni in grado di descrivere l'interazione tra le copie di variabili con
# cui abbiamo descritto la relazione AND.

graph = nx.Graph()
graph.add_edges_from([('x1', 'x2'), ('x1', 'z'), ('x2', 'z')])
decision_variables = ['x1', 'x2', 'z']

# Avendo stabilito:
# - il nome delle variabili che costruiscono la relazione AND;
# - la struttura del grafo che descrive i legami tra le variabili;
# - l'insieme delle risposte,
# l'API permette di costruire il modello Ising/QUBO, fissando il tipo delle variabili
# che modellano la relazione AND; scegliamo che siano variabili binarie.

model_specification = pm.Specification(graph, decision_variables, answers, dimod.BINARY)

# Abbiamo cioè stabilito di lavorare con un modello QUBO.

# Due strade sono possibili.

################################################################################################## 
# La prima potrebbe appoggiarsi alle così dette 'factories' che l'API mette a disposizione
# per definire il penalty model corrispondente a AND. Il metodo 'get_penalty_model' disponibile
# nella libreria 'penaltymodel' è quello che servirebbe, applicandolo alla 'model_specification':

p_model = pm.get_penalty_model(model_specification)


################################################################################################## 
# La seconda strada è, però, più istruttiva, perché costruisce il mdello QUBO passo passo.
#
# Cominciamo con l'osservare che:
#
# ham_and(x, y, z) = 3*z +(x*y) -2*x*z -2*y*z
#
# può essere preso come Hamiltoniano di AND, siccome abbiano:
#
#        x1 x2 z  3*z +(x1*x2) -2*x1*z -2*x2*z
#       --------------------------------------
#         0  0 0                0
#         0  0 1                3
#         0  1 0                0
#         0  1 1                1
#         1  0 0                0
#         1  0 1                1
#         1  1 0                1
#         1  1 1                0
#
# Segue la definzione del modello QUBO indotto da ham_and(x, y, z):

qubo = dimod.BinaryQuadraticModel({'x1': 0., 'x2': 0., 'z': 3.}, {('x1', 'x2'): 1., ('x1', 'z'): 2., ('x2', 'z'): 2.}, 0.0, dimod.BINARY)

# Il modello è un dizionario che descrive la matrice diagonale superiore che caratterizza un
# modello QUBO. Il penultimo parametro '0.0', è l'offset, cioè la costante tipicamente presente
# in un Hamiltoniano. L'offset è nullo perché potremmo scrivere ham_and(x, y, z) come:
# 
#           3*z +(x*y) -2*x*z -2*y*z + 0.0
#

# L'API permette di calcolare il valore di un Hamiltoniano per una precisa istanza della relazione
# cui esso è associato:

ground_energy = qubo.energy({'x1': 0, 'x2': 1, 'z': 0})

# restituisce il valore 0, come del resto ci attendiamo.
# 
# L'ultimo parametro necessario per ottenere il penalty model, seguendo questa secnda strada, è
# la differenza tra:
#  - il minimo valore energetico assunto dall'Hamiltoniano in corrispondenza delle configurazioni 
# che *non* sono risposte;
#  - l'*unico valore* energetico assunto dall'Hamiltoniano in corrispondenza di tutte le configurazioni
# che *sono* risposte.
#
# Nel nostro caso, la differenza vale 1:

classical_gap = 1

# NOTA. Sembra ragionevole che non ci sia un metodo dell'API per fornire questo valore.

# 
p_model = pm.PenaltyModel.from_specification(model_specification, qubo, classical_gap, ground_energy)

# Le funzionalità dei package associati a penaltymodel sono a 
# https://docs.ocean.dwavesys.com/en/stable/docs_penalty/packages/index.html

