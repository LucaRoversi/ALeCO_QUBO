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

import dimod

from pyqubo import Binary # modulo pyqubo con classe Binary
num_vars = 4

# Definire parametricamente nomi di variabile con le f-string di Python. 
#
variables = [Binary(f'x{j}') for j in range(num_vars)]

# Elenco variabili appena definite.
#
for i in variables:
    print("Variabile {}".format(i))

# Matrice come dictionary sulle variabili definite.

Q = {('x0','x0'): -5    #     0
    ,('x1','x1'): -3    #    / \
    ,('x2','x2'): -8    #   /   \
    ,('x3','x3'): -6    #  1-----2
    ,('x0','x1'):  4    #       / 
    ,('x0','x2'):  8    #      /
    ,('x1','x2'):  4    #     3
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

###################################################################
# "Campionamento" spazio degli stati tramite Simulated Annealing.
###################################################################
from neal import SimulatedAnnealingSampler
SA = SimulatedAnnealingSampler()

n_reads  = 10
n_sweeps = 10
sampleset_SA = SA.sample(bqm, num_reads=n_reads, num_sweeps=n_sweeps)
print("--------------------------")
print("Campionamento spazio stati con Simulated Annealing:\n", sampleset_SA)

##############################################
# Campionatore ibrido(?) con DWaveSampler
##############################################
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
import dwave.inspector

DWHS = EmbeddingComposite(DWaveSampler())
c_strength = 1  # Più il valore è alto, più può essere difficile trovare la risposta (a causa della precisione dell'hardware?)
ann_time   = 20 # Potrebbe corrispondere al parametro num_sweep di SimulatedAnnealingSampler(?) 

sampleset_DWHS = DWHS.sample(bqm, chain_strength=c_strength, num_reads=n_reads, annealing_time=ann_time)
dwave.inspector.show(sampleset_DWHS)
