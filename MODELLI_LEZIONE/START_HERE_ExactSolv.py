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
# - estrazione di risposte con Simulated Annealing e ExactSolver
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

# BQM corrispondete all'Hamiltoniano ham.
# È nuovamente una rappresentazione interna che gioca il ruolo
# della matrice quadrata triangolare superiore, o simmetrica,
# che caratterizza una istanza QUBO.
#bqm = ham_internal.to_bqm(feed_dict={'L': 2})
bqm = ham_internal.to_bqm()
print(bqm)

# Alcuni attributi del BQM.
print("Componenti lineari: ", bqm.linear)           # lineari
print("Componenti quadratiche: ", bqm.quadratic)    # quadratiche
print("Offset: ", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento con ExactSolver (visita BF)
# -----------------------------------------
# Lo scopo è estrarre tutte le risposte, cioè le soluzioni che 
# soddisfano il vincolo e che hanno energia minima.
# Un passo intermedio è individuare l'esistenza di non soluzioni,
# cioè di campioni che non soddsifano il vincolo (esplicito).
####################################################################
from dimod import ExactSolver

# Istanza del campionatore scelto
ES = ExactSolver()

# Campionatura sul BQM tale che:
# - ??
# - ??
sampleset = ES.sample(bqm)
print(sampleset)
#       ==> [DecodedSample(decoded_subhs=[Constraint(a + b = 1,energy=1.000000)] ...

# Rappresentazione ad array della campionatura con attributi accessibili:
decoded_sampleset = ham_internal.decode_sampleset(sampleset)
print(decoded_sampleset)
#   - singolo campione;
print(decoded_sampleset[0])
#   - lista dei campioni;
print(list(map(lambda x: x.sample       , decoded_sampleset)))
#   - lista delle energie di ogni campione;
print(list(map(lambda x: x.energy       , decoded_sampleset)))
#   - lista dei vincoli di ogni campione;
print(list(map(lambda x: x.constraints(), decoded_sampleset)))
#   - lista dei campioni che non soddisfano il vincolo:
#       -- {'b': 0, 'a': 0} se il vincolo non è soddisfatto;
#       -- None             se il vincolo     è soddisfatto.
print(list(map(lambda s: (s.sample if (s.constraints().get('a + b = 1')[0]) == False else None), decoded_sampleset)))

# Uno dei migliori campioni, cioè uno tra quelli con energia minima.
best_sample = min(decoded_sampleset, key=(lambda s: s.energy))
print(best_sample.sample)
# Energia di uno dei migliori campioni che soddisfino, o meno, il vincolo
print("best_sample.energy: ", best_sample.energy)

# Sovralista delle risposte, cioè soluzioni con energia minima che soddisfano i vincoli
answers_rough = list(map(lambda s: (s.sample if (s.constraints().get('a + b = 1')[0]) == True and (s.energy == best_sample.energy) else None), decoded_sampleset))
print(answers_rough)

# Lista di tutt e sole le risposte
answers = list(filter(lambda s: s != None, answers_rough))
print(answers)

