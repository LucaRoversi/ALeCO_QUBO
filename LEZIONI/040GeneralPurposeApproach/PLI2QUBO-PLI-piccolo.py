
"""Reduce a small binary linear-integer program to a QUBO.

The example contains one constraint of each kind:

    maximize  10*x[0] + 7*x[1] + 9*x[2]

    subject to
        2*x[0] + 3*x[1] + 2*x[2] == 5,
        3*x[0] + 2*x[1] + 3*x[2] <= 5,
        2*x[0] + 3*x[1] +   x[2] >= 3,

where every decision variable is binary.

The equality needs no auxiliary variable.  The upper-bound inequality uses
a nonnegative slack, while the lower-bound inequality uses a nonnegative
surplus that is subtracted from its left-hand side.

All constraint expressions have integer coefficients.  An infeasible state
therefore has at least one squared penalty of value 1 or more.  Since

    sum(profits) = 26,

the conservative strict choice lambda = 27 makes that one penalty larger
than the greatest possible profit advantage of any binary assignment.
"""

from __future__ import annotations

from typing import Any, NamedTuple, Sequence, cast

from dimod import BinaryQuadraticModel, ExactSolver, SampleSet
from neal import SimulatedAnnealingSampler
from pyqubo import Array, Constraint, Placeholder


# ---------------------------------------------------------------------------
# 1. Problem data
# ---------------------------------------------------------------------------

PROFITS: tuple[int, ...] = (10, 7, 9)

EQUALITY_COEFFICIENTS: tuple[int, ...] = (2, 3, 2)
EQUALITY_VALUE = 5

UPPER_COEFFICIENTS: tuple[int, ...] = (3, 2, 3)
UPPER_BOUND = 5

LOWER_COEFFICIENTS: tuple[int, ...] = (2, 3, 1)
LOWER_BOUND = 3

NUMBER_OF_ITEMS = len(PROFITS)

if not (
    len(EQUALITY_COEFFICIENTS)
    == len(UPPER_COEFFICIENTS)
    == len(LOWER_COEFFICIENTS)
    == NUMBER_OF_ITEMS
):
    raise ValueError("Every coefficient tuple must have one entry per item")


# The sufficient bound is strict.  Adding one gives the smallest integer
# strictly greater than the sum of the nonnegative profits.
PENALTY_STRENGTH = float(sum(PROFITS) + 1)


# ---------------------------------------------------------------------------
# 2. Exact bounded-binary ranges for slack and surplus variables
# ---------------------------------------------------------------------------

def _binary_vectors(length: int):
    """Yield all binary tuples of the requested length."""

    for number in range(1 << length):
        yield tuple((number >> bit) & 1 for bit in range(length))


def bounded_binary_coefficients(maximum: int) -> tuple[int, ...]:
    """Return coefficients whose subset sums cover exactly [0, maximum]."""

    if maximum < 0:
        raise ValueError("maximum must be nonnegative")
    if maximum == 0:
        return ()

    number_of_bits = maximum.bit_length()
    ordinary_coefficients = [1 << bit for bit in range(number_of_bits - 1)]
    last_coefficient = maximum - sum(ordinary_coefficients)
    coefficients = tuple(ordinary_coefficients + [last_coefficient])

    represented = {
        sum(coefficient for bit, coefficient in zip(bits, coefficients) if bit)
        for bits in _binary_vectors(len(coefficients))
    }
    assert represented == set(range(maximum + 1))
    assert sum(coefficients) == maximum

    return coefficients


# For A(x) <= U with nonnegative coefficients, the all-zero assignment gives
# the greatest possible slack U - 0.  Hence the full independent range is
# 0,...,UPPER_BOUND.
UPPER_SLACK_MAXIMUM = UPPER_BOUND
UPPER_SLACK_COEFFICIENTS = bounded_binary_coefficients(UPPER_SLACK_MAXIMUM)

# For L <= A(x), the greatest surplus is max(A(x)) - L.  Nonnegative binary
# coefficients give max(A(x)) by setting every x variable to one.
LOWER_SURPLUS_MAXIMUM = sum(LOWER_COEFFICIENTS) - LOWER_BOUND
LOWER_SURPLUS_COEFFICIENTS = bounded_binary_coefficients(
    LOWER_SURPLUS_MAXIMUM
)


# ---------------------------------------------------------------------------
# 3. Symbolic QUBO construction
# ---------------------------------------------------------------------------

class CompiledPLI(NamedTuple):
    """Objects needed to sample the compiled QUBO."""

    model: Any
    bqm: BinaryQuadraticModel


def weighted_expression(coefficients: Sequence[int], variables: Any):
    """Build a symbolic weighted sum using pyqubo-compatible indexing.

    A ``pyqubo.Array`` does not support slices such as ``variables[1:]``.
    Integer indexing keeps this helper compatible with pyqubo and ordinary
    Python sequences.
    """

    if len(coefficients) == 0 or len(variables) == 0:
        return 0
    if len(coefficients) != len(variables):
        raise ValueError("coefficients and variables must have the same length")

    expression = coefficients[0] * variables[0]
    for index in range(1, len(coefficients)):
        expression += coefficients[index] * variables[index]
    return expression


def build_qubo() -> CompiledPLI:
    """Construct, compile, and instantiate the parametric PLI QUBO."""

    item = Array.create("x", shape=NUMBER_OF_ITEMS, vartype="BINARY")
    upper_slack = Array.create(
        "y", shape=len(UPPER_SLACK_COEFFICIENTS), vartype="BINARY"
    )
    lower_surplus = Array.create(
        "z", shape=len(LOWER_SURPLUS_COEFFICIENTS), vartype="BINARY"
    )

    profit = weighted_expression(PROFITS, item)
    equality_left = weighted_expression(EQUALITY_COEFFICIENTS, item)
    upper_left = weighted_expression(UPPER_COEFFICIENTS, item)
    lower_left = weighted_expression(LOWER_COEFFICIENTS, item)

    encoded_upper_slack = weighted_expression(
        UPPER_SLACK_COEFFICIENTS, upper_slack
    )
    encoded_lower_surplus = weighted_expression(
        LOWER_SURPLUS_COEFFICIENTS, lower_surplus
    )

    # Equality: A_E(x) = E.
    equality_penalty = Constraint(
        (equality_left - EQUALITY_VALUE) ** 2,
        label="equality",
    )

    # Upper bound: A_U(x) <= U iff A_U(x) + S_U(y) = U.
    upper_penalty = Constraint(
        (upper_left + encoded_upper_slack - UPPER_BOUND) ** 2,
        label="upper_bound",
    )

    # Lower bound: L <= A_L(x) iff A_L(x) - S_L(z) = L.
    lower_penalty = Constraint(
        (lower_left - encoded_lower_surplus - LOWER_BOUND) ** 2,
        label="lower_bound",
    )

    penalty_parameter = Placeholder("lambda")
    qubo_expression = -profit + penalty_parameter * (
        equality_penalty + upper_penalty + lower_penalty
    )

    # pyqubo's type annotations do not expose compile() reliably.  This cast
    # affects static checking only; the run-time symbolic expression is
    # unchanged.
    model = cast(Any, qubo_expression).compile()
    bqm = model.to_bqm(feed_dict={"lambda": PENALTY_STRENGTH})

    return CompiledPLI(model=model, bqm=bqm)


# ---------------------------------------------------------------------------
# 4. Decode samples in the language of the original PLI problem
# ---------------------------------------------------------------------------

class DecodedRow(NamedTuple):
    """A binary sample interpreted as a PLI candidate."""

    energy: float
    decision: tuple[int, ...]
    profit: int
    equality_left: int
    upper_left: int
    lower_left: int
    upper_slack: int
    lower_surplus: int
    penalties: tuple[int, int, int]
    feasible: bool
    occurrences: int


def decode_row(sample: dict[str, int], energy: float, occurrences: int) -> DecodedRow:
    """Compute original objectives, constraints, and penalties for one sample."""

    decision = tuple(sample[f"x[{index}]"] for index in range(NUMBER_OF_ITEMS))

    profit = sum(value * coefficient for value, coefficient in zip(decision, PROFITS))
    equality_left = sum(
        value * coefficient
        for value, coefficient in zip(decision, EQUALITY_COEFFICIENTS)
    )
    upper_left = sum(
        value * coefficient
        for value, coefficient in zip(decision, UPPER_COEFFICIENTS)
    )
    lower_left = sum(
        value * coefficient
        for value, coefficient in zip(decision, LOWER_COEFFICIENTS)
    )

    upper_slack = sum(
        coefficient * sample[f"y[{index}]"]
        for index, coefficient in enumerate(UPPER_SLACK_COEFFICIENTS)
    )
    lower_surplus = sum(
        coefficient * sample[f"z[{index}]"]
        for index, coefficient in enumerate(LOWER_SURPLUS_COEFFICIENTS)
    )

    equality_penalty = (equality_left - EQUALITY_VALUE) ** 2
    upper_penalty = (upper_left + upper_slack - UPPER_BOUND) ** 2
    lower_penalty = (lower_left - lower_surplus - LOWER_BOUND) ** 2

    feasible = (
        equality_left == EQUALITY_VALUE
        and upper_left <= UPPER_BOUND
        and lower_left >= LOWER_BOUND
    )

    return DecodedRow(
        energy=float(energy),
        decision=decision,
        profit=profit,
        equality_left=equality_left,
        upper_left=upper_left,
        lower_left=lower_left,
        upper_slack=upper_slack,
        lower_surplus=lower_surplus,
        penalties=(equality_penalty, upper_penalty, lower_penalty),
        feasible=feasible,
        occurrences=occurrences,
    )


def decode_samples(sampleset: SampleSet) -> list[DecodedRow]:
    """Decode all samples in increasing QUBO-energy order."""

    rows: list[DecodedRow] = []

    for record in sampleset.data(
        fields=["sample", "energy", "num_occurrences"], sorted_by="energy"
    ):
        # SampleSet.data() creates a named-tuple-like record dynamically.
        # Consequently, dimod's static type information cannot declare the
        # attributes sample, energy, and num_occurrences, even though they are
        # present at run time because they were requested in fields above.
        dynamic_record = cast(Any, record)

        # dimod also uses a generic Variable type for sample keys and may
        # return NumPy scalar types for values, energy, and occurrence counts.
        # pyqubo labels are strings in this model, so normalize all values
        # explicitly before passing them to the strongly typed decoder.
        normalized_sample: dict[str, int] = {
            str(variable): int(value)
            for variable, value in dynamic_record.sample.items()
        }
        rows.append(
            decode_row(
                normalized_sample,
                float(dynamic_record.energy),
                int(dynamic_record.num_occurrences),
            )
        )

    return rows


def print_best(label: str, sampleset: SampleSet, limit: int = 10) -> None:
    """Print a compact view of the lowest-energy decoded samples."""

    print(f"\n{label}")
    print("-" * len(label))
    print(f"lambda = {PENALTY_STRENGTH:g}")
    print(f"upper slack coefficients = {UPPER_SLACK_COEFFICIENTS}")
    print(f"lower surplus coefficients = {LOWER_SURPLUS_COEFFICIENTS}")
    print("energy | x         | profit | A_E | A_U | A_L | slack | surplus | penalties | feasible | reads")

    for row in decode_samples(sampleset)[:limit]:
        print(
            f"{row.energy:6.1f} | {str(row.decision):9} | {row.profit:6d} |"
            f" {row.equality_left:3d} | {row.upper_left:3d} |"
            f" {row.lower_left:3d} | {row.upper_slack:5d} |"
            f" {row.lower_surplus:7d} | {str(row.penalties):9} |"
            f" {str(row.feasible):8} | {row.occurrences:5d}"
        )


# ---------------------------------------------------------------------------
# 5. Exact and heuristic sampling
# ---------------------------------------------------------------------------

def run_exact_solver(bqm: BinaryQuadraticModel) -> SampleSet:
    """Enumerate every BQM state; suitable only for small examples."""

    return ExactSolver().sample(bqm)


def run_simulated_annealing(bqm: BinaryQuadraticModel) -> SampleSet:
    """Sample heuristically; returned candidates still require decoding."""

    sampler = SimulatedAnnealingSampler()
    return sampler.sample(bqm, num_reads=100, num_sweeps=1_000, seed=7)


def main() -> None:
    """Build the QUBO, run both samplers, and report decoded candidates."""

    compiled = build_qubo()

    exact_samples = run_exact_solver(compiled.bqm)
    print_best("ExactSolver: lowest-energy states", exact_samples)

    annealed_samples = run_simulated_annealing(compiled.bqm)
    print_best("Simulated annealing: lowest-energy samples", annealed_samples)

    # ExactSolver checks every state of this small BQM.  The expected optimum
    # is x=(1,1,0), with profit 17.  Simulated annealing is heuristic and does
    # not provide the same proof of optimality.
    exact_best = decode_samples(exact_samples)[0]
    assert exact_best.feasible
    assert exact_best.decision == (1, 1, 0)
    assert exact_best.profit == 17


if __name__ == "__main__":
    main()



# ORIGINALE 

################################################################################################
# Riduzione di un problema in PLI, con vincoli arbitrari in QUBO.
# Sviluppiamo un esempio nell stile della sezione :
# 
# "General 0/1 Programming", de:
# "Quantum Bridge Analytics I: a tutorial on formulating and using QUBO models"
# 
# Il punto fondamentale dell'esempio è trasformare disequazioni in equazioni tramite 
# l'espansione binaria di variabili slack necessarie alla trasformazione.
#
# Tecnicamente, sperimentiamo la definizione di un BQM che dipende da un parametro
# lagrangiano, da istanziare opportunamente per distanziare soluzioni da non soluzioni.
#
# Utile riferimento nella documentazione:
# https://pyqubo.readthedocs.io/en/latest/getting_started.html#solve-qubo-by-dimod-sampler
################################################################################################

from pyqubo import Binary, Placeholder, Constraint

x1, x2, x3 = Binary('x1'), Binary('x2'), Binary('x3')
y1, y2     = Binary('y1'), Binary('y2')
z1, z2     = Binary('z1'), Binary('z2')

# Hamiltoniano principale
ham_obiettivo = (10*x1 + 7*x2 + 9*x3)

# Hamiltoniani penalità
ham_penalita0  = Constraint(( 2*x1 + 3*x2 + 2*x3              - 5)**2, label='cnstr0')
ham_penalita1  = Constraint(( 3*x1 + 2*x2 + 3*x3 + (y1+ 2*y2) - 5)**2, label='cnstr1')
ham_penalita2  = Constraint(( 2*x1 + 3*x2 +   x3 - (z1+ 2*z2) - 3)**2, label='cnstr2')

# Lagrangiano inserito nel modello con il ruolo di parametro
L = Placeholder('L')

# Hamiltoniano da minimizzare
ham = -ham_obiettivo + L*ham_penalita0 + L*ham_penalita1 + L*ham_penalita2 

# Singola compilazione che produce un Hamiltoniano parametrico in L
ham_internal = ham.compile()

# BQM parametrico corrispondente
bqm = ham_internal.to_bqm(feed_dict={'L': 3})
print(" -- bqm (componenti lineari):\n", bqm.linear)           # lineari
print(" -- bqm (componenti quadratiche):\n", bqm.quadratic)    # quadratiche
print(" -- bqm (offset):\n", bqm.offset)                       # scostamento costante da 0?

####################################################################
# Campionamento con ExactSolver (visita BF)
####################################################################
from dimod import ExactSolver

print("-----------------------------")
ES = ExactSolver()
# Parametri disponibili in ES
#
print(" ES.parameters:\n", ES.parameters)

print("-----------------------------")
# Campionatura sul BQM.
sampleset = ES.sample(bqm)
print("Sampleset:\n",sampleset)

####################################################################
# Campionamento con Simulated Annealing
####################################################################
print("-----------------------------")
from  neal import SimulatedAnnealingSampler

SA = SimulatedAnnealingSampler()
print(" SA.parameters:\n", SA.parameters)

# Campionatura sul BQM.
sampleset = SA.sample(bqm, num_reads=5, num_sweeps=30)
print("Sampleset:\n",sampleset)