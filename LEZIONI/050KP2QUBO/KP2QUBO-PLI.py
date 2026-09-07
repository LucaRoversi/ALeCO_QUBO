
"""Reduce a 0--1 knapsack instance to QUBO and solve it pedagogically.

The knapsack instance is

    maximize 10*x[0] + 10*x[1] + 12*x[2] + 18*x[3]
    subject to 2*x[0] + 4*x[1] + 6*x[2] + 9*x[3] <= 16,

where every decision variable is binary.

The inequality is changed into an equality by adding a nonnegative binary
slack S(s):

    2*x[0] + 4*x[1] + 6*x[2] + 9*x[3] + S(s) = 16.

The QUBO minimizes negative profit plus a squared constraint penalty.  The
penalty strength uses the readily available strict bound developed in the
teaching notes:

    lambda > sum(profits).

Because the profits are integers, this script chooses

    lambda = sum(profits) + 1 = 51.
"""

from __future__ import annotations

from typing import Any, NamedTuple, Sequence, cast

from dimod import BinaryQuadraticModel, ExactSolver, SampleSet
from neal import SimulatedAnnealingSampler
from pyqubo import Array, Constraint, Placeholder


# ---------------------------------------------------------------------------
# 1. Problem data
# ---------------------------------------------------------------------------

PROFITS: tuple[int, ...] = (10, 10, 12, 18)
WEIGHTS: tuple[int, ...] = (2, 4, 6, 9)
CAPACITY = 16

if len(PROFITS) != len(WEIGHTS):
    raise ValueError("PROFITS and WEIGHTS must have the same length")


# The bound in the notes is strict: lambda must be greater than the sum of
# the nonnegative profits.  Adding one is a natural margin for integer data.
PENALTY_STRENGTH = float(sum(PROFITS) + 1)


# ---------------------------------------------------------------------------
# 2. Bounded binary encoding of an integer interval
# ---------------------------------------------------------------------------

def bounded_binary_coefficients(maximum: int) -> tuple[int, ...]:
    """Return coefficients whose binary subset sums cover exactly [0, maximum].

    For maximum > 0, let k = ceil(log2(maximum + 1)).  The first k-1
    coefficients are ordinary powers of two.  The last coefficient is
    adjusted so that the greatest representable value is exactly ``maximum``.

    For example, maximum = 16 gives

        (1, 2, 4, 8, 1).

    With the last bit equal to zero, the first four bits represent 0,...,15.
    With the last bit equal to one, they represent 1,...,16.  Their union is
    therefore exactly 0,...,16.  Duplicate representations are harmless:
    slack variables are auxiliary variables, and only the represented value
    enters the knapsack equality.
    """

    if maximum < 0:
        raise ValueError("maximum must be nonnegative")
    if maximum == 0:
        return ()

    # For a positive integer M, M.bit_length() equals ceil(log2(M + 1)).
    number_of_bits = maximum.bit_length()
    ordinary_coefficients = [1 << bit for bit in range(number_of_bits - 1)]
    last_coefficient = maximum - sum(ordinary_coefficients)

    coefficients = tuple(ordinary_coefficients + [last_coefficient])

    # These assertions document and check the two essential properties of
    # the bounded encoding used by the QUBO construction.
    represented = {
        sum(coefficient for bit, coefficient in zip(bits, coefficients) if bit)
        for bits in _binary_vectors(len(coefficients))
    }
    assert represented == set(range(maximum + 1))
    assert sum(coefficients) == maximum

    return coefficients


def _binary_vectors(length: int):
    """Yield all binary tuples of the requested length."""

    for number in range(1 << length):
        yield tuple((number >> bit) & 1 for bit in range(length))


SLACK_COEFFICIENTS = bounded_binary_coefficients(CAPACITY)


# ---------------------------------------------------------------------------
# 3. Symbolic QUBO construction
# ---------------------------------------------------------------------------

class CompiledKnapsack(NamedTuple):
    """Objects needed to sample and decode the compiled QUBO."""

    model: Any
    bqm: BinaryQuadraticModel


def weighted_expression(coefficients: Sequence[int], variables: Any):
    """Build a symbolic weighted sum using pyqubo-compatible indexing.

    ``pyqubo.Array`` accepts an integer index (or a tuple of integer indices),
    but it does not implement Python slicing.  In particular, an expression
    such as ``variables[1:]`` raises ``TypeError``.  The explicit index loop
    below works both for a pyqubo Array and for an ordinary Python sequence.
    """

    if len(coefficients) == 0 or len(variables) == 0:
        return 0
    if len(coefficients) != len(variables):
        raise ValueError("coefficients and variables must have the same length")

    expression = coefficients[0] * variables[0]
    for index in range(1, len(coefficients)):
        expression += coefficients[index] * variables[index]
    return expression


def build_qubo() -> CompiledKnapsack:
    """Construct, compile, and instantiate the parametric knapsack QUBO."""

    item = Array.create("x", shape=len(PROFITS), vartype="BINARY")
    slack = Array.create(
        "s", shape=len(SLACK_COEFFICIENTS), vartype="BINARY"
    )

    profit = weighted_expression(PROFITS, item)
    occupied_capacity = weighted_expression(WEIGHTS, item)
    encoded_slack = weighted_expression(SLACK_COEFFICIENTS, slack)

    # A feasible item selection admits a slack assignment that makes this
    # expression zero.  An overweight selection cannot do so because every
    # slack coefficient is nonnegative.
    capacity_discrepancy = occupied_capacity + encoded_slack - CAPACITY
    capacity_penalty = Constraint(
        capacity_discrepancy**2,
        label="capacity",
    )

    # Placeholder keeps lambda symbolic during compilation.  It is assigned
    # the justified value PENALTY_STRENGTH when the BQM is produced.
    penalty_parameter = Placeholder("lambda")
    qubo_expression = -profit + penalty_parameter * capacity_penalty

    # pyqubo has incomplete static type information.  The cast tells type
    # checkers that this symbolic expression supplies compile(); it does not
    # change the object or its run-time behavior.
    model = cast(Any, qubo_expression).compile()
    bqm = model.to_bqm(feed_dict={"lambda": PENALTY_STRENGTH})

    return CompiledKnapsack(model=model, bqm=bqm)


# ---------------------------------------------------------------------------
# 4. Decoding in the language of the original knapsack problem
# ---------------------------------------------------------------------------

class DecodedRow(NamedTuple):
    """A sampled state interpreted as a knapsack candidate."""

    energy: float
    selected_items: tuple[int, ...]
    weight: int
    profit: int
    slack: int
    discrepancy: int
    penalty: int
    feasible: bool
    occurrences: int


def decode_row(sample: dict[str, int], energy: float, occurrences: int) -> DecodedRow:
    """Translate one binary sample into knapsack quantities."""

    selected_items = tuple(
        index for index in range(len(PROFITS)) if sample[f"x[{index}]"] == 1
    )
    weight = sum(WEIGHTS[index] for index in selected_items)
    profit = sum(PROFITS[index] for index in selected_items)
    slack_value = sum(
        coefficient * sample[f"s[{index}]"]
        for index, coefficient in enumerate(SLACK_COEFFICIENTS)
    )
    discrepancy = weight + slack_value - CAPACITY
    penalty = discrepancy**2

    return DecodedRow(
        energy=float(energy),
        selected_items=selected_items,
        weight=weight,
        profit=profit,
        slack=slack_value,
        discrepancy=discrepancy,
        penalty=penalty,
        feasible=weight <= CAPACITY,
        occurrences=occurrences,
    )


def decode_samples(sampleset: SampleSet) -> list[DecodedRow]:
    """Decode and order all returned samples by increasing QUBO energy."""

    rows = [
        decode_row(dict(record.sample), record.energy, record.num_occurrences)
        for record in sampleset.data(
            fields=["sample", "energy", "num_occurrences"], sorted_by="energy"
        )
    ]
    return rows


def print_best(label: str, sampleset: SampleSet, limit: int = 10) -> None:
    """Print a compact, pedagogical view of the lowest-energy samples."""

    print(f"\n{label}")
    print("-" * len(label))
    print(f"lambda = {PENALTY_STRENGTH:g}")
    print(f"slack coefficients = {SLACK_COEFFICIENTS}")
    print("energy | items       | weight | profit | slack | penalty | feasible | reads")

    for row in decode_samples(sampleset)[:limit]:
        print(
            f"{row.energy:6.1f} | {str(row.selected_items):11} |"
            f" {row.weight:6d} | {row.profit:6d} | {row.slack:5d} |"
            f" {row.penalty:7d} | {str(row.feasible):8} | {row.occurrences:5d}"
        )


# ---------------------------------------------------------------------------
# 5. Exact and heuristic sampling
# ---------------------------------------------------------------------------

def run_exact_solver(bqm: BinaryQuadraticModel) -> SampleSet:
    """Enumerate every binary state; suitable only for small examples."""

    return ExactSolver().sample(bqm)


def run_simulated_annealing(bqm: BinaryQuadraticModel) -> SampleSet:
    """Sample heuristically; returned samples still require explicit checks."""

    sampler = SimulatedAnnealingSampler()
    return sampler.sample(bqm, num_reads=100, num_sweeps=1_000, seed=7)


def main() -> None:
    """Build the model, run both samplers, and display decoded candidates."""

    compiled = build_qubo()

    exact_samples = run_exact_solver(compiled.bqm)
    print_best("ExactSolver: lowest-energy states", exact_samples)

    annealed_samples = run_simulated_annealing(compiled.bqm)
    print_best("Simulated annealing: lowest-energy samples", annealed_samples)

    # ExactSolver enumerates all states, so its best state is a proof for this
    # tiny BQM.  Simulated annealing is heuristic: failure to see a better
    # state is not a proof that no better state exists.
    exact_best = decode_samples(exact_samples)[0]
    assert exact_best.feasible
    assert exact_best.profit == 38


if __name__ == "__main__":
    main()



######## ORIGINAL

################################################################################################
# Riduzione di una istanza di KP a QUBO, vedendo KP come problema in PLI.
# L'obiettivo è quindi minimizzare il polinomio lineare dei profitti controbilanciando
# i valori che esso assume con un polinomio penalità ricavato dal vincolo sullo spazio
# disponibile.
#
# L'istanza di riferimento di KP è:
# 
#                     |  0  |  1 |  2 |  3
#           ---------------------------------  W = 16
#           profitti  | 10  | 10 | 12 | 18
#           pesi      |  2  |  4 |  6 |  9
#           
# Per ridurre il numero di slack variables necessarie a trasformare il vincolo:
# 
#           2*x1 +4*x2 +6*x3 +9*x4 <= 16
# 
# in eguaglianza, ipotizziamo che il profitto non sarà mai inferiore a quello 
# offerto dal Greedy-split. Ipotizzando l'ordine di inserimento:
#
#        0      1      2      3
#
#      10/2 > 10/4 > 12/2 = 18/2
#
# Greedy-split inserisce i tre elementi 0, 1 e 2, occupando 12 unità con 
# profitto 32. Lo spazio residuo da riempire per arrivare a 16 è 4.
# Quindi tre variabili slack s0, s1 e s2 son sufficienti a coprire almeno
# la differenza tra lo riempimento dello Greedy-split e il massimo consentito.
################################################################################################
from pyqubo import Binary, Placeholder, Constraint

x0, x1, x2, x3  = Binary('x0'), Binary('x1'), Binary('x2'), Binary('x3')
s0, s1, s2      = Binary('s0'), Binary('s1'), Binary('s2')

# Hamiltoniano principale
ham_obiettivo = (10*x0 + 10*x1 + 12*x2 + 18*x3)

# Hamiltoniani penalità
ham_penalita  = Constraint((16 - (2*x0 + 4*x1 + 6*x2 + 9*x3 \
                                  + s0 + 2*s1 + 4*s2))**2,  \
                label='cnstr0')

# Lagrangiano inserito nel modello con il ruolo di parametro
L = Placeholder('L')

# Hamiltoniano da minimizzare
ham = -ham_obiettivo + L*ham_penalita

# Singola compilazione che produce un Hamiltoniano parametrico in L
ham_internal = ham.compile()

# BQM parametrico corrispondente
bqm = ham_internal.to_bqm(feed_dict={'L': 40})
# print(" -- bqm (componenti lineari):\n", bqm.linear)           # lineari
# print(" -- bqm (componenti quadratiche):\n", bqm.quadratic)    # quadratiche
# print(" -- bqm (offset):\n", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento con ExactSolver (visita BF)
####################################################################
from dimod import ExactSolver

print("-----------------------------")
ES = ExactSolver()
# Parametri disponibili in ES
print(" ES.parameters:\n", ES.parameters)

print("-----------------------------")
# Campionatura sul BQM.
sampleset = ES.sample(bqm)
print("Sampleset:\n",sampleset)

print("-----------------------------")
# Energia minima dei sample che soddisfano il constraint.
#best_energy = min([s.energy for s in decoded_sampleset if (s.constraints().get('a + b = 1')[0]) ])
#print("Energia minima dei sample che soddisfano il constraint: ", best_energy)
# Un'alternativa è usare 
print("sampleset.first.energy: ", sampleset.first.energy) # per avere l'energia del sample con energia minima.

###############################################
# Risultati al variare di L.
#
# Con L = 2:
# s0 s1 s2 x0 x1 x2 x3 energy 
# 0   0  0  1  0  1  1  -38.0 ===> profitto 10+12+18 = 40 con peso 2+6+9 = 17 <-- non soluzione
# 1   0  0  1  1  0  1  -38.0 ===> profitto 10+10+18 = 38 con peso 2+4+9 = 15 <-- risposta
#
# Con L = 3:
# s0 s1 s2 x0 x1 x2 x3 energy 
# 1   0  0  1  1  0  1  -38.0 ===> profitto 10+10+18 = 38 con peso 1+2+4+9 = 16 <-- risposta
# 0   0  0  1  0  1  1  -37.0 ===> profitto 10+12+18 = 40 con peso 0+2+6+9 = 17 <-- non soluzione
#
# Sembra che ponendo il lagrangiano almeno a 3, otteniamo dia già sufficiente a ottenere la risposta.
# Una valutazione più "sofisticata" su come determinare il valore del Lagrangiano è sulle dispense. 
###################################################################

####################################################################
# Campionamento con Simulated Annealing
####################################################################
print("-----------------------------")
from  neal import SimulatedAnnealingSampler

SA = SimulatedAnnealingSampler()
# print(" SA.parameters:\n", SA.parameters)

# Campionatura sul BQM.
sampleset = SA.sample(bqm, num_reads=10, num_sweeps=100)
print("Sampleset:\n",sampleset)
