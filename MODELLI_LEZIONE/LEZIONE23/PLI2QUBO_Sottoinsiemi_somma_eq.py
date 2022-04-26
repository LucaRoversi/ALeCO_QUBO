## Sviluppo del problema che nella Sezione 3.1 de
# "General 0/1 Programming", pag. 24 de https://arxiv.org/ftp/arxiv/papers/1811/1811.11538.pdf .
# viene chiamato "Number Partitioning Problem" e che io chiamo "Sottoinsiemi a Somma Identica".
# 
# È uno dei problemi che, con la formulazione corretta, è immediatamente in forma QUBO, anche
# se implicita.
#
# ========================
print("## \"Number Partitioning Problem\" o \"Sottoinsiemi a Somma Identica\"")
print(" pag. 6 de: \" Quantum Bridge Analytics I: A Tutorial\"")

from pyqubo import Binary, Constraint, Placeholder

x1, x2, x3, x4, x5 = Binary('x1'), Binary('x2'), Binary('x3'), Binary('x4'), Binary('x5')
v1 = 1
v2 = 3
v3 = 4
v4 = 2
v5 = 6

# Hamiltoniano completo nella rappresentazione funzionale ovvia.
ham = ((v1+v2+v3+v4+v5) - 2*(x1*v1+x2*v2+x3*v3+x4*v4+x5*v5))**2

# Rappresentazione interna (D-Wave) dell'hamoltoniano.
# Servirà per poter decodificare la struttura restituita dal campionatore
# che viene applicato ad un BQM (Binary Quadratic Model).
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
from dimod import ExactSolver

print("-----------------------------")
# Istanza del campionatore scelto
ES = ExactSolver()
print(" ES.parameters: ", ES.parameters)


print("-----------------------------")
# Campionatura sul BQM.
sampleset = ES.sample(bqm)
print("Sampleset:\n",sampleset)
#       ==> [DecodedSample(decoded_subhs=[Constraint(a + b = 1,energy=1.000000)] ...

print("-----------------------------")
# Rappresentazione ad array della campionatura con attributi accessibili:
decoded_sampleset = ham_internal.decode_sampleset(sampleset)
print("Decoded_samplset: ", decoded_sampleset)
#   - singolo campione;
print(" -- lista dei sample estratti dal decoded_sampleset: ", \
    [x.sample for x in decoded_sampleset])

