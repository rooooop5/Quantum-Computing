# QuantumCircuit

A compact **statevector quantum circuit simulator** written in NumPy.

It provides single-qubit gates, controlled gates, and multi-qubit gates
(Toffoli, multi-controlled X, SWAP, Fredkin), together with projective
measurement. The whole simulator is one class with no dependencies beyond
NumPy, which makes it small enough to read end to end and easy to extend.

## Features

- Statevector simulation of `n` qubits (`2**n` complex amplitudes).
- Single-qubit gates: `X`, `Y`, `Z`, `H`, `S`.
- Controlled gates: `CNOT`, `CH`, `CZ`.
- Multi-qubit gates: Toffoli/CCX, multi-controlled X, controlled-U, SWAP,
  Fredkin/CSWAP.
- Projective measurement with state collapse and renormalization.
- Outcome probabilities for a single qubit, and the full joint distribution.
- Input validation for qubit indices, gate matrices, and initial states.
- Chainable gate API (`qc.h(0).cnot(0, 1)`).

## Contents

- [Conventions](#conventions)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Usage examples](#usage-examples)
- [API reference](#api-reference)
- [How it works](#how-it-works)
- [Testing](#testing)
- [Performance and limitations](#performance-and-limitations)
- [Project layout](#project-layout)
- [Roadmap](#roadmap)

## Conventions

- An `n`-qubit state is a complex vector of length `2**n`.
- **Qubit 0 is the leftmost and most significant bit** (big-endian):

  ```
  |q0 q1 ... q(n-1)>   <->   index = q0*2**(n-1) + q1*2**(n-2) + ... + q(n-1)
  ```

  For three qubits: `000 -> 0`, `001 -> 1`, `010 -> 2`, ..., `111 -> 7`.

- Gates mutate the state in place and return `self`, so calls can be chained:

  ```python
  qc.h(0).cnot(0, 1)
  ```

- All qubit indices are zero-based and must satisfy `0 <= q < n`.

## Requirements

- Python 3.10 or newer
- NumPy

## Installation

The project is managed with [uv](https://docs.astral.sh/uv/).

```bash
# clone, then from the project root:
uv sync

# NumPy is declared in pyproject.toml. If it is missing:
uv add numpy
```

Run scripts inside the project environment:

```bash
uv run python your_script.py
```

## Quick start

```python
from quantum import QuantumCircuit

qc = QuantumCircuit(2)          # |00>
qc.h(0)                         # (|00> + |10>) / sqrt(2)
qc.cnot(0, 1)                   # Bell state

print(qc.probabilities())
# [0.5 0.  0.  0.5]

print(qc.outcome_probability(0, 1))
# 0.5
```

## Usage examples

### Bell state

```python
qc = QuantumCircuit(2)
qc.h(0).cnot(0, 1)

print(qc.probabilities())
# [0.5 0.  0.  0.5]      -> |00> and |11>, each 50%
```

### GHZ state

```python
qc = QuantumCircuit(3)
qc.h(0).cnot(0, 1).cnot(1, 2)

print(qc.probabilities())
# [0.5 0.  0.  0.  0.  0.  0.  0.5]
```

### Toffoli

```python
qc = QuantumCircuit(3, initial_state=[0, 0, 0, 0, 0, 0, 1, 0])  # |110>
qc.toffoli(0, 1, 2)

print(qc.probabilities())
# [0. 0. 0. 0. 0. 0. 0. 1.]      -> |111>
```

### Measurement

```python
qc = QuantumCircuit(1)
qc.h(0)

print(qc.probabilities())   # [0.5 0.5]
bit = qc.measure(0)         # 0 or 1
print(bit)
print(qc.probabilities())   # [1. 0.] or [0. 1.]
```

Measuring the same qubit again returns the same value, because the state has
collapsed.

## API reference

### Constructor

```python
QuantumCircuit(n, initial_state=None)
```

| Argument | Meaning |
|---|---|
| `n` | number of qubits |
| `initial_state` | optional list/array of `2**n` amplitudes; must be normalized |

With no initial state, the circuit starts in `|00...0>`.

```python
qc = QuantumCircuit(3)                       # |000>
qc = QuantumCircuit(2, [0, 1, 0, 0])         # |01>
```

A wrong-length or unnormalized state raises `ValueError`.

### Single-qubit gates

| Method | Gate | Matrix |
|---|---|---|
| `x(t)` | Pauli X (NOT) | `[[0, 1], [1, 0]]` |
| `y(t)` | Pauli Y | `[[0, -i], [i, 0]]` |
| `z(t)` | Pauli Z | `[[1, 0], [0, -1]]` |
| `h(t)` | Hadamard | `[[1, 1], [1, -1]] / sqrt(2)` |
| `s(t)` | Phase | `[[1, 0], [0, i]]` |

```python
qc = QuantumCircuit(1)
qc.x(0)     # |0> -> |1>
qc.h(0)     # |1> -> (|0> - |1>) / sqrt(2)
```

### Controlled gates

| Method | Gate |
|---|---|
| `cnot(control, target)` | controlled-X |
| `ch(control, target)` | controlled-H |
| `cz(control, target)` | controlled-Z |

```python
qc = QuantumCircuit(2)
qc.cnot(0, 1)      # flip the target when the control is 1
qc.cz(0, 1)        # sign flip on |11>
```

### Multi-qubit gates

| Method | Gate |
|---|---|
| `toffoli(c1, c2, target)` / `ccx` | flip target when both controls are 1 |
| `mcx(controls, target)` | flip target when all controls are 1 |
| `multi_controlled(U, controls, target)` | apply a 2x2 `U` when all controls are 1 |
| `swap(a, b)` | exchange two qubits |
| `fredkin(control, a, b)` / `cswap` | swap `a` and `b` when control is 1 |

```python
qc = QuantumCircuit(3)
qc.toffoli(0, 1, 2)                              # CCX
qc.mcx([0, 1], 2)                                # multi-controlled X
qc.multi_controlled(QuantumCircuit.H, [0, 1], 2) # controlled-H
qc.swap(0, 2)                                    # SWAP
qc.fredkin(0, 1, 2)                              # controlled SWAP
```

`multi_controlled` is built from the projector identity

```
C(U) = I - P(all controls = 1) + P(all controls = 1) * U(target)
```

so a single function covers every controlled gate. An empty control list
applies `U` directly to the target.

### State and measurement

| Method | Returns |
|---|---|
| `probabilities()` | array of `2**n` probabilities, `abs(amplitude)**2` |
| `outcome_probability(q, bit)` | probability that qubit `q` measures as `bit` |
| `measure(q)` | samples qubit `q`, collapses the state, returns `0` or `1` |

`probabilities()` is the full joint distribution. For one qubit, use
`outcome_probability`:

```python
qc = QuantumCircuit(2)
qc.h(0).cnot(0, 1)

p0 = qc.outcome_probability(0, 0)   # 0.5
p1 = qc.outcome_probability(0, 1)   # 0.5
```

To make measurement reproducible:

```python
import numpy as np
QuantumCircuit.rng = np.random.default_rng(42)
```

## How it works

A single-qubit gate is embedded in the full register with a Kronecker
product:

```
I (x) ... (x) G (x) ... (x) I
```

and applied as a matrix-vector product:

```python
self._state = op @ self._state
```

Controlled gates use projectors `P0 = |0><0|` and `P1 = |1><1|`:

```
C(U) = P0 (x) I + P1 (x) U
```

The two terms have disjoint support, so the sum behaves exactly like an
`if/else` while remaining linear. Multi-controlled gates generalise this:

```
C(U) = I - P(all controls = 1) + P(all controls = 1) * U(target)
```

Measurement is the only non-unitary step: project onto the observed outcome
and renormalize.

## Testing

Tests live in the file tests.py :

```bash
uv run test.py
```

The coverage is one test per gate (truth table on basis states),
a unitarity/norm check on random states, and validation tests for invalid
qubit indices.

## Performance and limitations

| Resource | Cost |
|---|---|
| Statevector memory | `2**n` complex amplitudes |
| One gate | builds a `2**n x 2**n` operator, O(4^n) |
| Practical size | roughly `n <= 10` on a laptop |

- Memory doubles with every added qubit.
- `_operator` builds a full matrix per gate. Applying gates directly to index
  pairs would be O(2^n) and is the natural next optimisation.
- No noise model, no mid-circuit reset, and no density-matrix support.
- Measurement uses a shared class-level RNG.

## Project layout

```
.
├── pyproject.toml     # uv project metadata and dependencies
├── uv.lock            # locked dependency versions
├── quantum.py         # QuantumCircuit
├── tests.py           # test suite
└── README.md
```

## Roadmap

- Index-based gate application (O(2^n) per gate instead of O(4^n)).
- A circuit object that records gates separately from execution.
- A backend adapter so the same circuit code can run on different engines.
- Circuit serialization (JSON or OpenQASM).
- Noise models and density-matrix simulation.