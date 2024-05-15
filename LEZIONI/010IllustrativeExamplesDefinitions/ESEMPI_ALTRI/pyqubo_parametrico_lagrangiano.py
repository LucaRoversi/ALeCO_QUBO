# https://pyqubo.readthedocs.io/en/latest/getting_started.html#solve-qubo-by-dimod-sampler

## Modelli con Lagrangiano
# ========================
print("## Modelli con Lagrangiano")
# Il problema Number Partition non ha vincoli espliciti da trasformare in un Hamiltoniano
# penalità, da pesare per mezzo del coeffieciente Lagrangiano.
# 
# Ci concetriamo quindi su un problema diverso, con le seguenti caratteristiche:
# - 2*a + b è la funzione obiettivo,
# - a + b = 1 è il vincolo.
# L'Hamiltoniano penalità è quindi:
#       
#           (a + b − 1)**2
# 
# e l'hamiltoniano completo assume la forma:
# 
#         (2*a + b) + L * (a + b − 1)**2
#
# Tipicamente, L va trovato sperimentalmente. 

### Esprimere il Lagrangiano
# ==========================
print("### Esprimere il Lagrangiano")
from pyqubo import Binary, Placeholder, Constraint

a, b = Binary('a'), Binary('b')

ham_obiettivo = (2*a + b)
ham_penalita  = Constraint((a + b - 1)**2, label='a + b = 1')
L = Placeholder('L')
ham_implicit = ham_obiettivo + L * ham_penalita
# La compilazione avviene una sola volta ed il risultato è parametrico in L
qubo_implicit = ham_implicit.compile()
for l in range(5,6,1):
    # Fissa il valore del lagrangiano aggiornando il dizioinario
    qubo = qubo_implicit.to_bqm(feed_dict={'L': l})
    print(qubo)
    print("Componenti lineari: ", qubo.linear, "con l=",l)
    print("Componenti quadratiche: ", qubo.quadratic, "con l=",l)
    print("Offset: ", qubo.offset, "con l=",l)

### Verifica assenza di 'risposte' che violano il vincolo
# =======================================================
import neal
sa = neal.SimulatedAnnealingSampler()
sampleset = sa.sample(qubo, num_reads=10)
decoded_samples = qubo_implicit.decode_sampleset(sampleset)
best_sample = min(decoded_samples, key=lambda x: x.energy)
print(best_sample.sample)
# Secondo me, dà segmentation fault perché decoded_samples
# è applicato a qubo_implicit che non è completamente determinato:
# esso contiene il lagrangiano L con valore ignoto.
# Questo tentativo è stato giustificato dalla curiosità di
# "automatizzare" la verifica che non ci siano false risposte,
# cioè risposte che assicurano il valore minimo per l'intero
# modello, costituito da Hamiltino obiettivo ed Hamiltoniano
# penalty.