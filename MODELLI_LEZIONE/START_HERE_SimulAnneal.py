############################################################################################
# RISORSE (In ordine cronologico inverso)
# - https://www.youtube.com/watch?v=lz4d6XYBJok (DA GUARDARE!!)
# - https://pyqubo.readthedocs.io/en/latest/getting_started.html#solve-qubo-by-dimod-sampler
############################################################################################


##################################################################################
# Modello essenziale
# --------------------------------------------------------------------------------
# - rappresentazione di un hamiltoniano come polinomio multivariato quadratico
# - sua rappresentazione interna con cui ricavare informazioni dal campionamento
# dello spazio degli stati
# - sua rappresentazione come BQM, da sottoporre ad un campionatore
# - estrazione di (liste di) attributi
# - estrazione di risposte con Simulated Annealing
##################################################################################

#################################
# Hamiltoniano (interno), BQM
#################################
# Supponiamo di avere il seguente modell:
# - funzione obiettivo: 2*a + b
# - vincolo: a + b = 1
# L'Hamiltoniano che corrisponde al vincolo, e che chiamiamo Hamiltoniano penalità è:
#       
#           (a + b − 1)**2
# 
# L'hamiltoniano completo:
# 
#         (2*a + b) + L * (a + b − 1)**2
#
#  L parametro lagrangiano.

from pyqubo import Binary, Constraint, Placeholder

a, b = Binary('a'), Binary('b')

# Codifica (ovvia) della funzione obiettivo.
ham_obiettivo = (2*a + b)

# Codifica del vincolo come funzione penalità quadratica.
ham_penalita  = Constraint((a + b - 1)**2, label='a + b = 1') 

# Lagrangiano definito come variabile con lo stesso tipo delle 
# variabili che compaiono nei due hamiltoinani appena definiti.
L = 1

# hamiltoniano completo nella rappresentazione "ovvia"
ham = ham_obiettivo + L * ham_penalita 

# Rappresentazione interna dell'hamoltoniano.
# È fondamentale per poter decodificare la struttura restituita 
# dai campionatori applicabili ad un BQM (Binary Quadratic Model).
ham_internal = ham.compile()

print("-----------------------------")
# BQM corrispondete all'Hamiltoniano ham.
# È nuovamente una rappresentazione interna che gioca il ruolo
# della matrice quadrata triangolare superiore, o simmetrica,
# che caratterizza una istanza QUBO.
#bqm = ham_internal.to_bqm(feed_dict={'L': 2})
bqm = ham_internal.to_bqm()
print("bqm: ", bqm)

# Alcuni attributi del BQM.
print(" -- bqm (componenti lineari): ", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche): ", bqm.quadratic)    # quadratiche
print(" -- bqm (offset): ", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento con Simulated Annealing
# -------------------------------------
# Lo scopo è estrarre tutte le risposte, cioè le soluzioni che 
# soddisfano il vincolo e che hanno energia minima.
####################################################################
import neal
# Istanza del campionatore scelto
SA = neal.SimulatedAnnealingSampler()

# Campionatura sul BQM.
sampleset = SA.sample(bqm, num_reads=3)
print("Sampleset: ",sampleset)
#       ==> [DecodedSample(decoded_subhs=[Constraint(a + b = 1,energy=1.000000)] ...

print("-----------------------------")
# Rappresentazione ad array della campionatura con attributi accessibili:
decoded_sampleset = ham_internal.decode_sampleset(sampleset)
print("Decoded_samplset: ", decoded_sampleset)
#   - singolo campione;
print(" -- decoded_sampleset[0]: ", decoded_sampleset[0])
#   - lista dei campioni;
print(" -- lista dei sample estratti dal decoded_sampleset: ", [x.sample for x in decoded_sampleset])
#   - lista delle energie di ogni campione;
print(" -- lista delle sole enerige dei sample estratti dal decoded_sampleset: ",  [x.energy for x in decoded_sampleset])
#   - lista dei vincoli di ogni campione;
print(" -- lista dei soli constraint dei sample estratti dal decoded_sampleset: ", [x.constraints() for x in decoded_sampleset])
#   - lista dei campioni che non soddisfano il vincolo:
#       -- {'b': 0, 'a': 0} se il vincolo non è soddisfatto;
#       -- None             se il vincolo     è soddisfatto.
print(" -- lista dei sample che non soddisfano il constraint:", [s.sample for s in decoded_sampleset if not(s.constraints().get('a + b = 1')[0])])

print("-----------------------------")
# Energia minima dei sample che soddisfano il constraint.
best_energy = min([s.energy for s in decoded_sampleset if (s.constraints().get('a + b = 1')[0]) ])
print("Energia minima dei sample che soddisfano il constraint: ", best_energy)

print("-----------------------------")
# Lista con tutte risposte, cioè soluzioni con energia minima che soddisfano i vincoli
answers = [s.sample for s in decoded_sampleset if (s.energy == best_energy) and (s.constraints().get('a + b = 1')[0])]
print("Tutte e sole le risposte con energia minima {} sono {}.".format(best_energy,answers))