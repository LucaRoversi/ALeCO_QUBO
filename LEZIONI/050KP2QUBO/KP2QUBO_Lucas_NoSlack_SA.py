"""Simulated-annealing implementation of the Lucas KP-to-QUBO example.

This source uses the same no-slack, one-hot QUBO model as the exhaustive
implementation. The difference is only the sampler: simulated annealing
examines a selected collection of candidate states instead of every state.
"""

from neal import SimulatedAnnealingSampler
from pyqubo import Binary, Constraint, Placeholder


# ---------------------------------------------------------------------------
# 1. Reference KP instance
# ---------------------------------------------------------------------------
# x_i = 1 means that item i is placed in the knapsack.
profits = (10, 10, 12, 18)
weights = (2, 4, 6, 9)
capacity = 16


# ---------------------------------------------------------------------------
# 2. Binary variables
# ---------------------------------------------------------------------------
# Keep plain variable names separate from the symbolic PyQUBO objects.
x_names = tuple(f"x{i}" for i in range(len(profits)))
x = [Binary(name) for name in x_names]

# y_c = 1 declares that the occupied weight is exactly c.
# This is a one-hot modeling choice, not a binary slack-variable encoding.
y_names = tuple(f"y{c}" for c in range(capacity + 1))
y = [Binary(name) for name in y_names]


# ---------------------------------------------------------------------------
# 3. Objective and penalty Hamiltonians
# ---------------------------------------------------------------------------
# KP maximizes profit, whereas the QUBO sampler minimizes energy.
profit = sum(value * variable for value, variable in zip(profits, x))

# Exactly one target weight must be selected.
one_hot_penalty = (1 - sum(y)) ** 2

# The selected target weight must equal the actual loaded weight.
declared_weight = sum(c * variable for c, variable in enumerate(y))
loaded_weight = sum(weight * variable for weight, variable in zip(weights, x))
weight_penalty = (declared_weight - loaded_weight) ** 2

penalty = Constraint(
    one_hot_penalty + weight_penalty,
    label="penalty",
)


# ---------------------------------------------------------------------------
# 4. Parametric QUBO construction
# ---------------------------------------------------------------------------
L = Placeholder("L")
hamiltonian = -profit + L * penalty
compiled_hamiltonian = hamiltonian.compile()

# For this reference instance, this penalty separates feasible solutions from
# the relevant low-energy constraint-violating assignments.
penalty_strength = 20
bqm = compiled_hamiltonian.to_bqm(feed_dict={"L": penalty_strength})


# ---------------------------------------------------------------------------
# 5. Simulated-annealing sampling
# ---------------------------------------------------------------------------
# Unlike ExactSolver, simulated annealing does not enumerate all 2^21 states.
# It performs many stochastic searches, each starting from a candidate state
# and gradually reducing the effective temperature.
sampler = SimulatedAnnealingSampler()

num_reads = 100
num_sweeps = 1000
sampleset = sampler.sample(
    bqm,
    num_reads=num_reads,
    num_sweeps=num_sweeps,
    seed=123,
)


# ---------------------------------------------------------------------------
# 6. Decode samples and identify feasible KP encodings
# ---------------------------------------------------------------------------
def decode_sample(sample, energy):
    """Return the KP meaning of one binary assignment."""

    # A SampleSet is indexed by plain names such as "x0".  It is not indexed
    # by the representation of a symbolic object, such as "Binary('x0')".
    selected_items = [i for i, name in enumerate(x_names) if sample[name] == 1]
    selected_targets = [c for c, name in enumerate(y_names) if sample[name] == 1]

    total_profit = sum(profits[i] for i in selected_items)
    total_weight = sum(weights[i] for i in selected_items)

    one_hot = len(selected_targets) == 1
    target_matches_weight = one_hot and selected_targets[0] == total_weight
    feasible = one_hot and target_matches_weight and total_weight <= capacity

    return {
        "items": selected_items,
        "target_weights": selected_targets,
        "profit": total_profit,
        "weight": total_weight,
        "feasible": feasible,
        "energy": energy,
    }


# The sampler may return infeasible states. We therefore select the best
# feasible state found among all simulated-annealing reads.
feasible_records = []
for sample, energy in sampleset.data(fields=["sample", "energy"]):
    record = decode_sample(sample, energy)
    if record["feasible"]:
        feasible_records.append(record)

if not feasible_records:
    raise RuntimeError(
        "No feasible state was found. Increase num_reads or num_sweeps."
    )

best_feasible = min(feasible_records, key=lambda record: record["energy"])
first_state = decode_sample(sampleset.first.sample, sampleset.first.energy)


# ---------------------------------------------------------------------------
# 7. Reader-oriented report
# ---------------------------------------------------------------------------
print("Number of BQM variables:", len(bqm.variables))
print("Number of simulated-annealing reads:", len(sampleset))
print("Number of sweeps per read:", num_sweeps)
print("Penalty strength L:", penalty_strength)
print("Feasible states found:", len(feasible_records))
print("Best feasible KP state found:", best_feasible)
print("First state returned by the sampler:", first_state)