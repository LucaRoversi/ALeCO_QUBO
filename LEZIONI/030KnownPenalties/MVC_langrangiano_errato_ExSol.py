################################################################################
# Risolviamo in maniera errata un'istanza del problema Minimun Vertex Cover 
# relativa al grafo:
# 
#              v2--v3
#               |   | \
#               |   |  v5
#               |   | /
#              v1--v4
#
# Esempio tratto da:
# "Quantum Bridge Analytics I: A Tutorial on Formulating and Using QUBO Models".
################################################################################
from pyqubo import Binary, Constraint

v1, v2, v3, v4, v5 = Binary('v1'), Binary('v2'), Binary('v3'), Binary('v4'), Binary('v5')

# Hamiltoniano espresso nella forma naturale di un polinomio.
ham_obiettivo  = v1 + v2 + v3 + v4 + v5

# Elenco dei polinomi penalità con cui estenderemo l'Hamiltoniano.
ham_penalita   = Constraint(1 - v1 - v2 + v1*v2, label="constr0")
ham_penalita  += Constraint(1 - v2 - v3 + v2*v3, label="constr1") 
ham_penalita  += Constraint(1 - v3 - v4 + v3*v4, label="constr2") 
ham_penalita  += Constraint(1 - v4 - v1 + v4*v1, label="constr3") 
ham_penalita  += Constraint(1 - v3 - v5 + v3*v5, label="constr4") 
ham_penalita  += Constraint(1 - v4 - v5 + v4*v5, label="constr5") 

# Istanza errata, cioè troppo piccola, del Lagrangiano.
L = 1

# Hamiltoniano completo nella rappresentazione funzionale ovvia,
# con lagrangiano e penalità.
ham = ham_obiettivo + L * ham_penalita 

# Rappresentazione interna (D-Wave) dell'Hamiltoniano.
# Servirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
ham_internal = ham.compile()

print("-----------------------------")
# BQM corrispondete all'Hamiltoniano ham.
bqm = ham_internal.to_bqm()
print("bqm:\n", bqm)

# Alcuni attributi del BQM.
print(" -- bqm (componenti lineari):\n", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche):\n", bqm.quadratic)    # quadratiche
print(" -- bqm (--->> OFFSET):\n", bqm.offset)                 # scostamento costante da 0?

####################################################################
# Campionamento con ExactSolver (visita BF)
####################################################################
from dimod import ExactSolver

# Istanza del campionatore scelto
ES = ExactSolver()

print("-----------------------------")
# Campionatura sul BQM.
sampleset = ES.sample(bqm)
print("Sampleset:\n",sampleset)
#       ==> [DecodedSample(decoded_subhs=[Constraint(a + b = 1,energy=1.000000)] ...
print("Lunghezza Sampleset: ", len(sampleset))

print("-----------------------------")
# Rappresentazione ad array della campionatura con attributi accessibili:
decoded_sampleset = ham_internal.decode_sampleset(sampleset)
#print("Decoded_samplset:\n", decoded_sampleset)
#   - singolo campione;
print(" -- decoded_sampleset: rappresentazione interna.\n", decoded_sampleset[0])
#   --- struttura penalità di un campione;
print(" ---- decoded_sampleset[0]: lista penalità. \n", decoded_sampleset[0].constraints())
print(" ---- decoded_sampleset[0]: singola penalità. \n", decoded_sampleset[0].constraints().get('constr0'))
print(" ---- decoded_sampleset[0]: penalità soddisfatta? \n", decoded_sampleset[0].constraints().get('constr0')[0])
print(" ---- decoded_sampleset[0]: valore penalità. \n", decoded_sampleset[0].constraints().get('constr0')[1])
#   - lista dei campioni;
print(" -- lista dei sample estratti dal decoded_sampleset:\n", [x.sample for x in decoded_sampleset])
#   - lista delle energie di ogni campione;
#print(" -- lista delle sole energie dei sample estratti dal decoded_sampleset: ",  [x.energy for x in decoded_sampleset])
#   - lista dei vincoli di ogni campione;
#print(" -- lista dei soli constraint dei sample estratti dal decoded_sampleset: ", [x.constraints() for x in decoded_sampleset])
#   - lista dei campioni che non soddisfano i vincoli:
non_solutions = [s.sample for s in decoded_sampleset \
    if not(s.constraints().get('constr0')[0]) or \
       not(s.constraints().get('constr1')[0]) or \
       not(s.constraints().get('constr2')[0]) or \
       not(s.constraints().get('constr3')[0]) or \
       not(s.constraints().get('constr4')[0]) or \
       not(s.constraints().get('constr5')[0])]
#print(" -- lista dei sample che non soddisfano il constraint:", non_solutions)
print(" -- lunghezza della lista dei sample che non soddisfano almeno un vincolo:\n", len(non_solutions))

print("-----------------------------")
# Energia minima dei sample che soddisfano i vincoli.
best_energy = min([s.energy for s in decoded_sampleset \
    if s.constraints().get('constr0')[0] and \
       s.constraints().get('constr1')[0] and \
       s.constraints().get('constr2')[0] and \
       s.constraints().get('constr3')[0] and \
       s.constraints().get('constr4')[0] and \
       s.constraints().get('constr5')[0]])
print("Energia minima dei sample che soddisfano tutti i vincoli:\n", best_energy)

print("-----------------------------")
# Lista con tutte risposte, cioè soluzioni con energia minima che soddisfano i vincoli.
answers = [s.sample for s in decoded_sampleset \
    if (s.energy == best_energy) and \
        s.constraints().get('constr0')[0] and \
        s.constraints().get('constr1')[0] and \
        s.constraints().get('constr2')[0] and \
        s.constraints().get('constr3')[0] and \
        s.constraints().get('constr4')[0] and \
        s.constraints().get('constr5')[0]]
print("Tutte e sole le risposte con energia minima {} che soddisfano i vincoli: {}.".format(best_energy,answers))

print("-----------------------------")
# Lista con tutte le non soluzioni (sample che non soddisfano almeno un vinvolo) 
# ma che hanno energia minima.
answers = [s.sample for s in decoded_sampleset \
    if (s.energy == best_energy) and \
        (not(s.constraints().get('constr0')[0]) or \
        not(s.constraints().get('constr1')[0]) or \
        not(s.constraints().get('constr2')[0]) or \
        not(s.constraints().get('constr3')[0]) or \
        not(s.constraints().get('constr4')[0]) or \
        not(s.constraints().get('constr5')[0]))]
print("Tutte e sole le *non* risposte con energia minima {}: {}.".format(best_energy,answers))