# https://docs.dwavesys.com/docs/latest/doc_handbook.html
# 

from dimod.generators import and_gate, or_gate, xor_gate
from dimod import ExactSolver, Binary, BinaryQuadraticModel
import neal


x = Binary('x')
y1 = Binary('y1')
z1 = Binary('z1')
x2 = Binary('x2')
y2 = Binary('y3')
z2 = Binary('z3')


#xor_gate_mine = BinaryQuadraticModel(x*y1)
#print(ExactSolver().sample(xor_gate_mine))


# Half-adder con uno xor definito a partire dall'equivalenza:
#
#       xor x y = or (and (not x) y) (and x (not y)) 
#
# Siccome stiamo pensando ai valori sia delle variabili,
# sia delle funzioni booleane come se fossero valori energetici, 
# il valore 1 è più energetico del valore 0, lo xor deve essere
# rappresentato dall'equivalenza logica:
#
#       xor x y = and (or (not x) y) (or x (not y)) 
#
# Segue l'Half-adder corrispondente:
bqm_or1 = or_gate('x' , 'y', 'or1')
bqm_or1.flip_variable('y')
bqm_or2 = or_gate('x', 'y', 'or2')
bqm_or1.flip_variable('x')
bqm_s = and_gate('or1', 'or2', 's')
bqm_c = and_gate('x', 'y', 'c')
ha = bqm_or1 + bqm_or2 + bqm_s + bqm_c
#print(ExactSolver().sample(ha))
sampler = neal.SimulatedAnnealingSampler()
sampleset = sampler.sample(ha, num_reads=8, num_sweeps=20)

print(sampleset)


print('-------------------------------------')

# Half-adder definito in base a un hamitoniano
# built-in perlo xor:
bqm_s1 = xor_gate('x', 'y', 's', 'ancilla')
bqm_c1 = and_gate('x', 'y', 'c1')
ha1 = bqm_s1 + bqm_c1
#print(ExactSolver().sample(ha1))
sampler1 = neal.SimulatedAnnealingSampler()
sampleset1 = sampler1.sample(ha1, num_reads=8, num_sweeps=20)
print(sampleset1)
