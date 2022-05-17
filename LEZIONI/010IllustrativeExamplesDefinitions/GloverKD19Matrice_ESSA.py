###################################################################################
# Implementiamo un esempio in:
# "Quantum Bridge Analytics I: A Tutorial on Formulating and Using QUBO Models",
# ripreso anche dalle dispense, esplicitando la matrice triangolare superiore 
# corrispondente.
#
# L'esempio originale usa una matrice simmetrica.
###################################################################################
# Intuitivamente, Binary è una classe che permette (anche) di vedere singole 
# variabili come 'binary quadratic model'.
# (https://pyqubo.readthedocs.io/en/latest/reference/express.html)
#
from pyqubo import Binary 
num_vars = 4

# Definire parametricamente nomi di variabile.
#
variables = [Binary(f'x{j}') for j in range(num_vars)]

# Elenco variabili appena definite.
#
for i in variables:
    print("Variabile {}".format(i))

# Matrice come dictionary sulle variabili definite.
#
Q = {('x0','x0'): -5
    ,('x1','x1'): -3
    ,('x2','x2'): -8
    ,('x3','x3'): -6
    ,('x0','x1'):  4 
    ,('x0','x2'):  8
    ,('x1','x2'):  4
    ,('x2','x3'): 10 }
print("--------------------------")
print("Matrice QUBO:\n", Q)

# Rappresentazione interna del modello QUBO.
#
# La documentazione chiama 'qubo' la  matrice Q
# e 'binary quadratic model' la rappresentazione interna.
# (dimod.BinaryQuadraticModel.from_qubo
# https://test-projecttemplate-dimod.readthedocs.io/en/latest/reference/bqm/generated/dimod.BinaryQuadraticModel.from_qubo.html)
#
from dimod import BinaryQuadraticModel
bqm = BinaryQuadraticModel.from_qubo(Q)
print("--------------------------")
print("Rappresentazione BQM:\n", bqm)

# "Campionamento" esaustivo spazio degli stati.
#
# ExactSolver è una visita BF dello spazio degli stati relativo al 'binary quadratic model',
# cioè alla rappresentazione interna del QUBO/matrice.
# (https://test-projecttemplate-dimod.readthedocs.io/en/latest/reference/sampler_composites/samplers.html)
#
from dimod import ExactSolver
ES = ExactSolver()
print("--------------------------")
print("Visita BF spazio stati:\n", ES.sample(bqm))


# "Campionamento" spazio degli stati tramite Simulated Annealing.
#
# La documentazione è oltremodo scarna. 
# (https://test-projecttemplate-dimod.readthedocs.io/en/latest/reference/sampler_composites/samplers.html)
# I parametri dovrebbero avere il seguente significato:
# -- num_reads è il numero di righe stampate;
# -- num_sweeps è il numero di iterazioni che l'algorimto esegue per convergere al minimo globale.
# La prova sperimentale per confermare l'ipotesi si può avere:
# -- limitando ad 1 il numero di campioni che costituiscono la risposta;
# -- interpretando l'algoritmo con numeri crescenti di num_sweeps.
# 'Risultati' non da prove a mano, non automatizzate:
# -- num_sweeps= 1 --> ogni chiamata restituisce una risposta diversa 
# -- num_sweeps= 2 --> ogni chiamata restituisce una risposta diversa
# -- num_sweeps= 3 --> la risposta (energy=-11) compare frequentemente, ma inframezzata da non risposte
# -- num_sweeps=10 --> la risposta (energy=-11) compare nella quasi totalità dei casi.
#
from neal import SimulatedAnnealingSampler
SA = SimulatedAnnealingSampler()
print("--------------------------")
print("Campionamento spazio stati con Simulated Annealing:\n" \
        , SA.sample(bqm, num_reads=1, num_sweeps=100))
