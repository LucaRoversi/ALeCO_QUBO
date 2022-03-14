##############################
# Minimun Vertex Cover to QUBO
# ============================
# Risolviamo un istanza di problema, usando uno dei due grafi in 
# https://en.wikipedia.org/wiki/Vertex_cover
# 
#               v2-----v4------v6
#              / |      |
#             /  |      |
#           v1   |      |
#            \   |      |
#             \  |      |
#              \v3-----v5
#
#

from pyqubo import Binary, Placeholder, Constraint

v1, v2, v3, v4, v5, v6 = Binary('v1'), Binary('v2'), Binary('v3'), Binary('v4'), Binary('v5'), Binary('v6')

ham_obiettivo = sum([Binary(f'v{i}') for i in range (4)])
ham_penalita  = Constraint(1 - v1 - v2 + v1*v2, label='v1 + v2 >= 1') + Constraint(1 - v1 - v3 + v1*v3, label='v1 + v3 >= 1')
#L = Placeholder('L')
#ham_implicit = ham_obiettivo + L * ham_penalita
## La compilazione avviene una sola volta ed il risultato è parametrico in L
#qubo_implicit = ham_implicit.compile()
#for l in range(5,6,1):
#    # Fissa il valore del lagrangiano aggiornando il dizioinario
#    qubo = qubo_implicit.to_bqm(feed_dict={'L': l})
#    print(qubo)
#    print("Componenti lineari: ", qubo.linear, "con l=",l)
#    print("Componenti quadratiche: ", qubo.quadratic, "con l=",l)
#    print("Offset: ", qubo.offset, "con l=",l)
#
#### Verifica assenza di 'risposte' che violano il vincolo
## =======================================================
#import neal
#sa = neal.SimulatedAnnealingSampler()
#sampleset = sa.sample(qubo, num_reads=10)
#decoded_samples = qubo_implicit.decode_sampleset(sampleset)
#best_sample = min(decoded_samples, key=lambda x: x.energy)
#print(best_sample.sample)