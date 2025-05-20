# PyQUBO to create a Binary Quadratic Model (BQM). 
# D-Wave sampler to sample the BQM.

from pyqubo import Binary, Constraint, Placeholder

import dwave.inspector
import dwave.system

# Define binary variables
a, b = Binary('a'), Binary('b')

# Define objective function
H = 2*a + b

# Define constraint
P = Constraint((a + b - 1)**2, label='constraint')

# Lagrangian (symbolic)
L = Placeholder('L')

# Define Hamiltonian
H_total = H + L * P


# Compile the model into a BQM
model = H_total.compile()
bqm = model.to_bqm(feed_dict={'L': 2}) # Lagrangian set to 2
# bqm = model.to_bqm()

# Instance of D-Wave sampler
sampler = dwave.system.EmbeddingComposite(dwave.system.DWaveSampler())

# Sample the BQM
sampleset = sampler.sample(bqm, num_reads=10)

# Print the samples
print(sampleset)

# Show minor embedding 
dwave.inspector.show(sampleset)

# `H` is the target function, `P` is the penalty. 
# The total Hamiltonian `H_total` is the sum of these two. 
# This is compiled into a BQM using PyQUBO's `compile` method. 
# The BQM is then sampled using a D-Wave sampler. 
# The resulting samples are printed, and the embedding used by the sampler is also printed.

