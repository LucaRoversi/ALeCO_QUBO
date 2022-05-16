##############################
# Minimun Vertex Cover to QUBO
# ============================
# Risolviamo un istanza di problema, usando uno dei due grafi in 
# https://en.wikipedia.org/wiki/Vertex_cover
# 
#              a--b--c
#
#

from pyqubo import Binary, Constraint, Placeholder

a, b, c = Binary('a'), Binary('b'), Binary('c')

ham  = -(a +2*b +c -2*a*b -2*b*c)

# hamiltoniano completo nella rappresentazione funzionale ovvia.
# Rappresentazione interna (D-Wave) dell'hamoltoniano.
# Sercirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
#
ham_internal = ham.compile()

print("-----------------------------")
# BQM corrispondete all'Hamiltoniano ham.
# È nuovamente una rappresentazione interna che gioca il ruolo
# della matrice quadrata triangolare superiore, o simmetrica,
# che caratterizza una istanza QUBO.
bqm = ham_internal.to_bqm()
print("bqm: ", bqm)

# Alcuni attributi del BQM.
print(" -- bqm (componenti lineari): ", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche): ", bqm.quadratic)    # quadratiche
print(" -- bqm (offset): ", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento con ExactSolver (visita BF)
# -----------------------------------------
# Lo scopo è estrarre tutte le risposte, cioè le soluzioni che 
# soddisfano il vincolo e che hanno energia minima.
####################################################################
from neal import SimulatedAnnealingSampler

# Istanza del campionatore scelto
SA = SimulatedAnnealingSampler()

print("-----------------------------")
# Campionatura sul BQM.
sampleset = SA.sample(bqm, num_reads=2, num_sweeps=3)
print("Sampleset: ",sampleset)
#       ==> [DecodedSample(decoded_subhs=[Constraint(a + b = 1,energy=1.000000)] ...
print("Lunghezza Sampleset: ", len(sampleset))

print("-----------------------------")
# Rappresentazione ad array della campionatura con attributi accessibili:
decoded_sampleset = ham_internal.decode_sampleset(sampleset)
#print("Decoded_samplset: ", decoded_sampleset)
#   - singolo campione;
#print(" -- decoded_sampleset[0]: ", decoded_sampleset[0])
#   - lista dei campioni;
#print(" -- lista dei sample estratti dal decoded_sampleset: ", [x.sample for x in decoded_sampleset])
#   - lista delle energie di ogni campione;
#print(" -- lista delle sole enerige dei sample estratti dal decoded_sampleset: ",  [x.energy for x in decoded_sampleset])
#   - lista dei vincoli di ogni campione;
#print(" -- lista dei soli constraint dei sample estratti dal decoded_sampleset: ", [x.constraints() for x in decoded_sampleset])
#   - lista dei campioni che non soddisfano il vincolo:
