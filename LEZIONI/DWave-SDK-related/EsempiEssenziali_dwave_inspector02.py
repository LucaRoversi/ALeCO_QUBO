from dwave.system import DWaveSampler
import dwave.inspector

# Get solver
sampler = DWaveSampler(solver=dict(topology__type='pegasus'))

# Define a problem
h = {}
J = {(2136, 4181): -1, (2136, 2151): -0.5, (2151, 4196): 0.5, (4181, 4196): 1}

# Sample
response = sampler.sample_ising(h, J, num_reads=100)

# Inspect
dwave.inspector.show(response)
