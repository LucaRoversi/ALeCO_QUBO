# https://docs.ocean.dwavesys.com/en/stable/examples/multi_gate.html

# Starting circuit
from dimod.generators import and_gate, or_gate, xor_gate
from dimod import ExactSolver, Binary, BinaryQuadraticModel

bqm_gate2 = or_gate('b', 'c', 'out2')
bqm_gate3 = and_gate('a', 'b', 'out3')
bqm_gate3.flip_variable('b')
bqm_gate4 = or_gate('out2', 'd', 'out4')
bqm_gate5 = and_gate('out3', 'out4', 'out5')
bqm_gate7 = or_gate('out5', 'out4', 'z')
bqm_gate7.flip_variable('out4')

bqm = bqm_gate2 + bqm_gate3 + bqm_gate4 + bqm_gate5 + bqm_gate7
print(bqm.num_variables)
#solutions = ExactSolver().sample(bqm).lowest()
solutions = ExactSolver().sample(bqm)
#out_fields = [key for key in list(next(solutions.data(['sample'])))[0].keys() if 'out' in key]
#print(drop_variables(solutions, out_fields))
print(solutions)





# Performance Comparison: Embedding Executions (cannot work I gues: QCPU time missing)

#from dimod.generators import ran_r
#from dwave.system import DWaveSampler, EmbeddingComposite, FixedEmbeddingComposite
#problem_size = 20
#num_problems = 10
#submission_repeats = 2
#qpu = DWaveSampler(solver=dict(topology__type='pegasus'))
#sampler1 = EmbeddingComposite(qpu)
#bqm = ran_r(10, problem_size)
#samplesets = {}
#chain_len = []
#for runs in range(num_problems):
#   samplesets[runs] = []
#   print("Run {}".format(runs))
#   sampleset = sampler1.sample(bqm, num_reads=5000, return_embedding=True)
#   if sampleset.first.energy > 0:
#       samplesets[runs].append(0)
#   else:
#       samplesets[runs].append(sum(sampleset.lowest().record.num_occurrences))
#   embedding = sampleset.info["embedding_context"]["embedding"]  
#   chain_len.append(max(len(x) for x in embedding.values()))     
#   sampler2 = FixedEmbeddingComposite(qpu, embedding=embedding)  
#   for i in range(submission_repeats):
#       print("\tSubmitting {}--{}".format(runs, i))
#       sampleset = sampler2.sample(bqm, num_reads=5000, return_embedding=True)   
#       if sampleset.first.energy > 0:                  
#          samplesets[runs].append(0)
#       else:
#          samplesets[runs].append(sum(sampleset.lowest().record.num_occurrences))