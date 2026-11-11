# quantum

A small quantum circuit simulator with two interchangeable backends:

- **`StateVector`** — dense amplitudes; superposition, entanglement, arbitrary
  single-qubit gates.
- **`Basis`** — one integer; exact for `X`, `CNOT`, `Toffoli`; scales to
  arithmetic circuits with tens of qubits.

A circuit records operations. A backend executes them. The simulator chooses a
backend and turns measurement results into counts.

```
registers -> circuit (recorder) -> backend -> simulator (runner)
```

## Features

- Named quantum and classical registers with slicing and iteration.
- A recorder that stores gates as tuples of global integer indices.
- `StateVector` backend: `X`, `Y`, `Z`, `H`, `S`, `CNOT`, `CH`, `CZ`,
  Toffoli/CCX, multi-controlled X, generic controlled-U, SWAP, Fredkin.
- `Basis` backend: exact `X`, `CNOT`, `Toffoli` on a single integer.
- Automatic backend selection from the circuit contents.
- Projective measurement with collapse and renormalization.
- Shots and a Qiskit-shaped `run(...).result().get_counts()` result.
- No dependencies beyond NumPy.

## Contents

- [Conventions](#conventions)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Registers](#registers)
- [Circuit API](#circuit-api)
- [Backends](#backends)
- [Simulator](#simulator)
- [How it works](#how-it-works)
- [Testing](#testing)
- [Performance and limitations](#performance-and-limitations)
- [Using it from another project](#using-it-from-another-project)
- [Project layout](#project-layout)

## Conventions

- An `n`-qubit state is a complex vector of length `2**n`.
- **Qubit 0 is the least significant bit** (little-endian, matching Qiskit):

  ```
  |q0 q1 ... q(n-1)>   <->   index = q(n-1)*2**(n-1) + ... + q1*2 + q0
  ```

  For two qubits: `|00> -> 0`, `|01> -> 1`, `|10> -> 2`, `|11> -> 3`,
  where the rightmost character is qubit 0.

- Counts strings follow Qiskit: the **last-added classical register is
  leftmost**, and clbit 0 is rightmost within its register.

- Gates return `self`, so calls can be chained.

## Installation

The project is managed with [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

With pip:

```bash
pip install -e .
```

## Quick start

```python
from quantum import QuantumCircuit, QuantumRegister, ClassicalRegister, Simulator

a = QuantumRegister(2, "a")
out = ClassicalRegister(2, "out")

qc = QuantumCircuit(a, out)
qc.x(a[0])
qc.cx(a[0], a[1])
qc.measure(a[0], out[0])
qc.measure(a[1], out[1])

counts = Simulator("matrix_product_state").run(qc, shots=1).result().get_counts()
print(counts)
# {'11': 1}
```

## Registers

```python
a   = QuantumRegister(3, "a")        # qubits 0, 1, 2
out = ClassicalRegister(2, "out")    # clbits 0, 1
```

Registers behave like sequences:

```python
len(a)          # 3
a[0]            # a Qubit handle
a[1:]           # a list of handles
list(a)         # all handles
for q in a: ... # iteration
```

Each handle stores one global index, assigned when the register is added to a
circuit.

## Circuit API

```python
qc = QuantumCircuit(a, b, out)
qc.add_register(other_register)
```

| Method | Gate |
|---|---|
| `x(qubit)` | Pauli X |
| `cx(control, target)` | CNOT |
| `ccx(c1, c2, target)` | Toffoli |
| `measure(qubit, clbit)` | record a measurement |

```python
qc.x(a[0]).cx(a[0], a[1]).measure(a[1], out[0])
```

The circuit stores only operations:

```python
qc.ops
# [('x', 0), ('cx', 0, 1), ('measure', 1, 0)]
```

No amplitudes are allocated until the simulator runs.

## Backends

### `StateVector(n, initial_state=None)`

Stores `2**n` complex amplitudes and supports the full gate set.

```python
from quantum import StateVector

s = StateVector(2)
s.dispatch(("h", 0))
s.dispatch(("cx", 0, 1))

print(s.probabilities())
# [0.5 0.  0.  0.5]

print(s.measure(0))
# 0 or 1, state collapses
```

| Method | Gate |
|---|---|
| `x`, `y`, `z`, `h`, `s` | single-qubit |
| `cnot`, `ch`, `cz` | controlled |
| `ccx`, `toffoli`, `mcx` | multi-controlled X |
| `multi_controlled(U, controls, target)` | controlled-U |
| `swap(a, b)` | SWAP |
| `fredkin(c, a, b)` / `cswap` | controlled SWAP |
| `dispatch(op)` | route a circuit operation |
| `measure(q)` | sample and collapse |
| `probabilities()`, `outcome_probability(q, bit)` | statistics |

Direct gate methods take argument tuples, mirroring `dispatch`:

```python
s.x((0,))
s.cnot((0, 1))
s.ccx((0, 1, 2))
```

Normally you use `dispatch`:

```python
s.dispatch(("h", 0))
s.dispatch(("cx", 0, 1))
s.dispatch(("ccx", 0, 1, 2))
```

### `Basis(n, initial_state=0)`

Stores the state as **one integer**. This is exact whenever the circuit never
leaves the computational basis, which is the case for all permutation
circuits: `X`, `CNOT`, `Toffoli`, and measurement.

```python
from quantum import Basis

b = Basis(3)                 # |000>
b.dispatch(("x", 0))         # |001>
b.dispatch(("cx", 0, 1))     # |011>
b.dispatch(("ccx", 0, 1, 2)) # |111>

print(b)                     # "111"
print(b.measure(2))          # 1
```

| Method | Gate |
|---|---|
| `x(op)` | flip one qubit |
| `cx(op)` | conditional flip |
| `ccx(op)` | two-control conditional flip |
| `dispatch(op)` | route a circuit operation |
| `measure(q)` | read a bit (deterministic) |
| `bit(q)` | read a bit |

The state is the integer `b.bits`; `str(b)` prints the bitstring.

#### Why it exists

A statevector stores `2**n` amplitudes. For the arithmetic circuits used by the
calculator:

| Circuit | Qubits | Statevector memory |
|---|---|---|
| add / subtract | 13 | 128 KiB |
| multiply | 30 | 16 GiB |
| divide | 47 | 2 PiB |

But these circuits never create entanglement — they are product states. An
integer stores exactly the one occupied basis state, so memory is O(1) and
each gate is a few bit operations. This is the same observation that makes a
matrix product state with bond dimension 1 cheap.

#### What it cannot do

`Basis` cannot represent superposition, phase, rotations, or noise. It is only
valid when every operation is `x`, `cx`, `ccx`, or `measure`. It raises
`ValueError` for any other operation.

### Choosing a backend

`Simulator(method=...)` maps the method to a backend:

| Method | Backend |
|---|---|
| `automatic`, `auto` | choose from the circuit contents |
| `matrix_product_state` | `Basis` |
| `statevector` | `StateVector` |

The automatic rule: if every operation is `x`, `cx`, `ccx`, or `measure`, use
`Basis`; otherwise use `StateVector`.

## Simulator

```python
sim = Simulator(method="automatic")
job = sim.run(circuit, shots=1)
counts = job.result().get_counts()
```

The `Job`/`Result` split mirrors Qiskit's API so existing code can call
`run(...).result().get_counts()` without changes.

### Shots

- `shots=1` returns one outcome.
- `shots=N` re-runs the circuit N times and accumulates a histogram.
- With the basis backend every shot is identical, so the result is
  `{key: N}`.

Measurement is executed inline. A mid-circuit measurement collapses the state
before later gates, which is the correct semantics, but it forces one full
simulation per shot with the statevector backend.

## How it works

### Statevector backend

A single-qubit gate is embedded with a Kronecker product:

```
I (x) ... (x) G (x) ... (x) I
```

and applied as a matrix-vector product:

```python
self._state = op @ self._state
```

Controlled gates use projectors `P0 = |0><0|`, `P1 = |1><1|`:

```
C(U) = P0 (x) I + P1 (x) U
```

Multi-controlled gates generalise this:

```
C(U) = I - P(all controls = 1) + P(all controls = 1) * U(target)
```

Measurement samples from `|amplitude|²`, zeroes the inconsistent branches,
and renormalizes.

### Basis backend

```
X(q)       bits ^= 1 << q
CX(c, t)   if bit(c): bits ^= 1 << t
CCX(a,b,t) if bit(a) and bit(b): bits ^= 1 << t
```

No amplitudes, no matrices, no sampling. Measurement is a bit read.

## Testing

```bash
uv run pytest
```

The suite covers registers, the recorder, both backends, backend agreement, and
end-to-end runs through the simulator.

## Performance and limitations

| | `StateVector` | `Basis` |
|---|---|---|
| memory | `2**n` amplitudes | one integer |
| one gate | builds a `2**n x 2**n` operator | a few bit operations |
| practical size | ~10 qubits | tens of qubits |
| gate set | arbitrary unitaries | permutations only |
| measurement | probabilistic + collapse | deterministic |
| mid-circuit measurement | supported, per-shot cost | trivial |

Other limitations:

- No noise, density-matrix simulation, or mid-circuit reset.
- `StateVector._operator` builds a full matrix per gate; applying gates to
  index pairs would be O(2^n) and is the natural optimization.
- Measurement uses a shared class-level RNG; seed it for reproducible runs.
- No classical feed-forward.

## Using it from another project

Install this package into the other project's environment:

```bash
pip install -e /path/to/quantum
```

Then:

```python
from quantum import QuantumCircuit, QuantumRegister, ClassicalRegister, Simulator
```

For a pip project, add to `requirements.txt`:

```text
-e /path/to/quantum
```

or, from GitHub:

```text
quantum @ git+https://github.com/USER/quantum.git
```

## Project layout

```
.
├── pyproject.toml
├── uv.lock
├── quantum/
│   ├── __init__.py          public exports
│   ├── registers.py         Qubit, ClassicalBit, registers
│   ├── circuits.py          QuantumCircuit (recorder)
│   ├── simulator.py         Result, Job, Simulator
│   └── backends/
│       ├── basis.py         integer backend
│       └── statevector.py   amplitude backend
└── tests/
    └── test_*.py
```
