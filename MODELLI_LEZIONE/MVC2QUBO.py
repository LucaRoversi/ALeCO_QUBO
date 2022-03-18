##############################
# Minimun Vertex Cover to QUBO
# ============================
# Risolviamo un istanza di problema, usando uno dei due grafi in 
# https://en.wikipedia.org/wiki/Vertex_cover
# 
#              c1--c3--c5
#             / |   |
#           c0  |   |
#             \ |   |
#              c2--c4
#
#

from pyqubo import Binary, Placeholder, Constraint

c0, c1, c2, c3, c4, c5 = Binary('c0'), Binary('c1'), Binary('c2'), Binary('c3'), Binary('c4'), Binary('c5')

ham_obiettivo  = c0 + c1 + c2 + c3 + c4 + c5
ham_penalita   = 1 - c0 - c1 + c0*c1
ham_penalita  += 1 - c0 - c2 + c0*c2 
ham_penalita  += 1 - c1 - c3 + c1*c3 
ham_penalita  += 1 - c2 - c4 + c2*c4 
ham_penalita  += 1 - c3 - c4 + c3*c4 
ham_penalita  += 1 - c3 - c5 + c3*c5 
ham = ham_obiettivo + ham_penalita # hamiltoniano da minimizzare
modello = ham.compile() # permette di leggere la struttura delle soluzioni
qubo = modello.to_bqm() # argomento per ExactSolver

from dimod import ExactSolver

def bruteforce_num_partition(qubo_model):
    return ExactSolver().sample(qubo_model) # bruteforce non è un vero campionamento
                                            # siccome ricerca esaustivamente 
solutions = ExactSolver().sample(qubo)
print(solutions)

# Per avere accesso alle componenti che formano solutions
# https://pyqubo.readthedocs.io/en/latest/reference/model.html#id1
decoded_solutions = modello.decode_sampleset(solutions)
answer = min(decoded_solutions, key=lambda s: s.energy)
print(decoded_solutions[0].sample)
