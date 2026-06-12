# SiSi_SiAnn

`SiSi_SiAnn.py` is a small application derived from the classroom script
`NumberPartitioning_SiAnn.py`.

It accepts an arbitrary integer sequence

```text
S = (v_1, ..., v_n)
```

and searches, by simulated annealing, for a subset `T` whose sum equals the sum
of its complement `S \ T`.

## Files

- `SiSi_SiAnn.py`: application entry point. It can run interactively or from the
  command line. The solver import is delayed so that interpreter/dependency
  errors are reported clearly.
- `sisi_qubo.py`: direct construction of the QUBO/BQM for the Hamiltonian.
  It implements the coefficients derived in the notes and does not require
  `pyqubo` at runtime.
- `sisi_tuning.py`: deterministic `n`-based tuning rules for `num_reads` and
  `num_sweeps`.
- `sisi_solver.py`: batched simulated-annealing search and result decoding.

Each function now has a docstring or inline comments explaining its role in the
mathematical-to-computational pipeline.

## Dependencies

The code expects the D-Wave Ocean packages that provide `dimod` and `neal`.

When using a conda environment, the easiest classroom workflow is often to open
this folder in an IDE that already uses the correct environment, then run
`SiSi_SiAnn.py` directly. In that case the script starts in interactive mode and
asks for the data.

## Interactive use

Run the entry point without command-line arguments:

```bash
python SiSi_SiAnn.py
```

The application asks for:

1. the integer sequence `S`, for example `1 3 4 2 6`;
2. the tuning profile: `classroom`, `balanced`, or `aggressive`;
3. an optional random seed;
4. whether to print the BQM coefficients.

Accepted sequence formats include:

```text
1 3 4 2 6
1, 3, 4, 2, 6
(1, 3, 4, 2, 6)
[1, 3, 4, 2, 6]
```

## Non-interactive command-line use

The previous command-line interface is still available:

```bash
python SiSi_SiAnn.py 1 3 4 2 6
python SiSi_SiAnn.py 1 1 1 1 1 --profile classroom
python SiSi_SiAnn.py 12 -3 7 4 2 --profile aggressive --seed 123
```

## Tuning policy

The selected parameters depend only on `n = len(S)`:

- `classroom`: low cost, compact output;
- `balanced`: default policy;
- `aggressive`: higher-cost heuristic run.

The solver runs reads in batches. After each batch it stops if it has already
found energy `0`. This preserves the `n`-based parameter rule while reducing the
actual cost on instances where a partition is found early.

No rule depending only on `n` can be mathematically optimal for every Number
Partitioning instance; the actual difficulty also depends on the values in `S`.
