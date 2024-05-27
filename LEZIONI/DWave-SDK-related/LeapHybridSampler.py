# Cut&Paste from
# https://docs.ocean.dwavesys.com/projects/system/en/stable/reference/samplers.html#leaphybridcqmsampler

from dimod import ConstrainedQuadraticModel, Integer
i = Integer('i', upper_bound=4)
j = Integer('j', upper_bound=4)
cqm = ConstrainedQuadraticModel()
cqm.set_objective(-i*j)
cqm.add_constraint(2*i+2*j <= 8, "Max perimeter")

from dwave.system import LeapHybridCQMSampler
sampler = LeapHybridCQMSampler()
sampleset = sampler.sample_cqm(cqm)
print(sampleset.first)                          
# --> Sample(sample={'i': 2.0, 'j': 2.0}, energy=-4.0, num_occurrences=1, is_feasible=True, is_satisfied=array([ True]))
