#################################################################################
# Implementiamo la soluzione per una istanza del  problema "Number Partitioning", 
# già visto come "Sottoinsiemi a Somma Identica",  da:
# "Quantum Bridge Analytics I: A Tutorial on Formulating and Using QUBO Models",
#
# Sviluppiamo due istanze, una caratterizata da un insieme di due risposte,
# l'altra dal non avere alcuna risposta. 
#################################################################################
print("## \"Number Partitioning Problem\" o \"Sottoinsiemi a Somma Identica senza risposta\"\n")

from pyqubo import Binary, Constraint, Placeholder
x1, x2, x3, x4, x5 = Binary('x1'), Binary('x2'), Binary('x3'), Binary('x4'), Binary('x5')

################################################################################ 
# Istanza senza risposte
################################################################################ 
v1 = 1
v2 = 1
v3 = 1
v4 = 1
v5 = 1

# Hamiltoniano completo nella rappresentazione funzionale ovvia.
ham = ((v1+v2+v3+v4+v5) - 2*(x1*v1+x2*v2+x3*v3+x4*v4+x5*v5))**2

# Rappresentazione interna (D-Wave) dell'Hamiltoniano.
# Servirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
ham_internal = ham.compile()

# BQM corrispondete all'Hamiltoniano ham.
# È nuovamente una rappresentazione interna che gioca il ruolo
# della matrice quadrata triangolare superiore, o simmetrica,
# che caratterizza una istanza QUBO.
bqm = ham_internal.to_bqm()

##############################################
# Campionatore con DWaveSampler
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
import dwave.inspector

DWHS = EmbeddingComposite(DWaveSampler())
n_reads    = 10 # Numero di campioni prodotti
# Determina il valore massimo del bias associato agli archi del modello
max_bias = max(abs(bias) for bias in bqm.quadratic.values())
c_strength = max_bias + 1  # Se l'energia associata ad un arco che costituisce una catena
                           # non ci dovrebbero essere catene rotte, in cui il majority
                           # voting non riesce a decidere quale spin assegnare a tutti i
                           # qbit nella catena
ann_time   = 20 # Potrebbe corrispondere al parametro num_sweep di SimulatedAnnealingSampler(?) 

sampleset_DWHS = DWHS.sample(bqm, chain_strength=c_strength, num_reads=n_reads, annealing_time=ann_time)
dwave.inspector.show(sampleset_DWHS)
