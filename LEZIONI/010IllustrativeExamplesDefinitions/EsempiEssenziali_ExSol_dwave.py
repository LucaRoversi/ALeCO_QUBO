############################################################################################
# RIFERIMENTO
# - https://pyqubo.readthedocs.io/en/latest/getting_started.html#solve-qubo-by-dimod-sampler
############################################################################################
############################################################################################


##################################################################################
# Modello essenziale
# --------------------------------------------------------------------------------
# - rappresentazione di un hamiltoniano come polinomio multivariato quadratico
# - sua rappresentazione interna con cui ricavare informazioni dal campionamento
# dello spazio degli stati
# - sua rappresentazione come BQM, da sottoporre ad un campionatore
# - estrazione di (liste di) attributi
# - estrazione di risposte con ExactSolver
##################################################################################

#################################
# Hamiltoniano (interno), BQM
#################################
# Supponiamo di avere il seguente modello:
# - funzione obiettivo: 2*a + b
# - vincolo: a + b = 1
# L'Hamiltoniano che corrisponde al vincolo, e che chiamiamo Hamiltoniano penalità è:
#       
#           (a + b − 1)**2
# 
# L'Hamiltoniano completo:
# 
#         (2*a + b) + L * (a + b − 1)**2
#
# con L parametro lagrangiano.

# Certo, posso aiutarti a convertire il tuo codice PyQUBO in un codice equivalente che utilizza le librerie disponibili in `dwave.system`. Ecco come potrebbe essere fatto:


from dimod import BinaryQuadraticModel, ExactSolver
from dwave.system import EmbeddingComposite, DWaveSampler

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Variabili binarie
a, b = 'a', 'b'

# Modello quadratico binario (BQM)
linear = {a: -2, b: -1}
quadratic = {(a, b): 2}
offset = 1
bqm = BinaryQuadraticModel(linear, quadratic, offset, 'BINARY')

print("BQM prodotto ")
print("bqm: ", bqm)

print(" -- componenti lineari: ", bqm.linear)           # lineari
print(" -- componenti quadratiche: ", bqm.quadratic)    # quadratiche
print(" -- offset: ", bqm.offset)                       # scostamento costante da 0


# Istanza del solver esatto
ES = ExactSolver()

print(" Insieme dei campioni ricavati dal BQM")
sampleset = ES.sample(bqm)
print(sampleset)

print(" Valore della minima energia dei campioni")
best_energy = min(sampleset.record.energy)
print(best_energy)

print(" Tutte e sole le risposte con energia minima ")
answers = [sample for sample in sampleset.data(['sample', 'energy']) if sample.energy == best_energy]
print("Energia:{},  risposta:{}.".format(best_energy, answers))


# Plot grafico energie
from plot_energies import plot_energies
plot_energies(sampleset)