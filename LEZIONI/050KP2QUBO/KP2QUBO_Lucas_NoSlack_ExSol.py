"""Exact, no-slack implementation of the Lucas KP-to-QUBO example.

The auxiliary variables y_0, ..., y_W use a one-hot target-weight
representation. They are not binary slack variables.
"""

from dimod import ExactSolver
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
# Keep the plain names separately from the symbolic PyQUBO objects.
x_names = tuple(f"x{i}" for i in range(len(profits)))
x = [Binary(name) for name in x_names]

# y_c = 1 means that the occupied weight is declared to be exactly c.
# This one-hot encoding is a modeling choice for clarity. It is not a
# binary slack-variable encoding.
y_names = tuple(f"y{c}" for c in range(capacity + 1))
y = [Binary(name) for name in y_names]


# ---------------------------------------------------------------------------
# 3. Objective and penalty Hamiltonians
# ---------------------------------------------------------------------------
# KP maximizes profit, whereas the QUBO model minimizes energy.
profit = sum(value * variable for value, variable in zip(profits, x))

# Exactly one target weight must be selected.
one_hot_penalty = (1 - sum(y)) ** 2

# The selected target weight must equal the actual weight of the items.
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

# Penalty value used for this reference instance.
penalty_strength = 20
bqm = compiled_hamiltonian.to_bqm(feed_dict={"L": penalty_strength})


# ---------------------------------------------------------------------------
# 5. Exhaustive enumeration with ExactSolver
# ---------------------------------------------------------------------------
# There are 4 decision variables and 17 one-hot variables:
# 2^(4+17) = 2^21 assignments are visited.
solver = ExactSolver()
sampleset = solver.sample(bqm)

expected_states = 2 ** (len(x) + len(y))
assert len(sampleset) == expected_states


# ---------------------------------------------------------------------------
# 6. Decode samples and identify feasible KP encodings
# ---------------------------------------------------------------------------
def decode_sample(sample, energy):
    """Return the KP meaning of one binary assignment."""

    # Important: str(Binary("x0")) is "Binary('x0')", but the SampleSet
    # is indexed by the plain name "x0". Therefore use x_names and y_names.
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


# ExactSolver returns every assignment. Decode that complete SampleSet while
# retaining only the best feasible record.
best_feasible = None
for sample, energy in sampleset.data(fields=["sample", "energy"]):
    record = decode_sample(sample, energy)
    if record["feasible"] and (
        best_feasible is None or record["energy"] < best_feasible["energy"]
    ):
        best_feasible = record

assert best_feasible is not None

# The global ground state must also be feasible for a sufficient penalty.
ground_state = decode_sample(sampleset.first.sample, sampleset.first.energy)
assert ground_state["feasible"]
assert ground_state["energy"] == best_feasible["energy"]


# ---------------------------------------------------------------------------
# 7. Reader-oriented report
# ---------------------------------------------------------------------------
print("Number of BQM variables:", len(bqm.variables))
print("Number of enumerated states:", len(sampleset))
print("Expected states:", expected_states)
print("Penalty strength L:", penalty_strength)
print("Best feasible KP state:", best_feasible)
print("Global ground state:", ground_state)