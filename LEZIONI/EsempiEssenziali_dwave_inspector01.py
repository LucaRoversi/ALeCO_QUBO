# Example from https://docs.ocean.dwavesys.com/en/stable/docs_cloud/intro.html?_gl=1*17ro5p0*_ga*NDAzMDg2Mjk1LjE2OTYyNjQ2MTM.*_ga_DXNKH9HE3W*MTcxMDI3NDczOS4xNC4xLjE3MTAyNzc2NDQuOS4wLjA.#configurationfiles
import dimod
import dwave.inspector
import dwave.system

bqm = dimod.generators.ran_r(1, 20)
sampler = dwave.system.EmbeddingComposite(dwave.system.DWaveSampler())
sampleset = sampler.sample(bqm, num_reads=100)
dwave.inspector.show(sampleset)