from dwave.system import DWaveSampler, EmbeddingComposite, LeapHybridSampler
from dimod import BinaryQuadraticModel
import time

# Define a simple QUBO problem
Q = {(0, 0): -1, (1, 1): -1, (0, 1): 2}
bqm = BinaryQuadraticModel.from_qubo(Q)

# Using DWaveSampler (non-hybrid)
sampler = DWaveSampler()
embedding_sampler = EmbeddingComposite(sampler)

start_time = time.time()
sampleset_dw = embedding_sampler.sample(bqm, annealing_time=20)
dwave_runtime = time.time() - start_time

# Check if chain break fraction is available
chain_break_fraction = sampleset_dw.info.get('chain_break_fraction', 'N/A')

# Using LeapHybridSampler (hybrid)
hybrid_sampler = LeapHybridSampler()

start_time = time.time()
sampleset_hybrid = hybrid_sampler.sample(bqm)
hybrid_runtime = time.time() - start_time

# Print results and metrics
print("DWaveSampler results:")
for sample in sampleset_dw:
    print(sample)
print(f"DWaveSampler runtime: {dwave_runtime:.4f} seconds")
print(f"DWaveSampler minimum energy: {sampleset_dw.first.energy}")
print(f"DWaveSampler chain break fraction: {chain_break_fraction}")

print("\nLeapHybridSampler results:")
for sample in sampleset_hybrid:
    print(sample)
print(f"LeapHybridSampler runtime: {hybrid_runtime:.4f} seconds")
print(f"LeapHybridSampler minimum energy: {sampleset_hybrid.first.energy}")
