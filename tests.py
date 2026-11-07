"""Simple tests for every gate and function in QuantumCircuit.

Run:  python3 test_simple.py
Change the import to your module.
"""

import numpy as np

from quantum import QuantumCircuit


def basis(n, bits):
    v = np.zeros(2 ** n, dtype=complex)
    v[int(bits, 2)] = 1.0
    return v


def check(got, expected, name):
    assert np.allclose(got, expected, atol=1e-9), (
        f"{name} failed\n  got     = {np.round(got, 4)}\n"
        f"  expected= {np.round(expected, 4)}"
    )
    print(f"ok   {name}")


# ---------------------------------------------------------------- basics
def test_initial_state():
    check(QuantumCircuit(3)._state, basis(3, "000"), "default state |000>")
    check(QuantumCircuit(2, [0, 1, 0, 0])._state, basis(2, "01"), "given state")

    try:
        QuantumCircuit(2, [1, 0])
        assert False, "wrong length should raise"
    except ValueError:
        pass

    try:
        QuantumCircuit(1, [1, 1])
        assert False, "unnormalized should raise"
    except ValueError:
        pass

    print("ok   initial state validation")


# ------------------------------------------------------------ single qubit
def test_x():
    check(QuantumCircuit(3, basis(3, "000")).x(0)._state, basis(3, "100"), "x")


def test_y():
    check(QuantumCircuit(1, basis(1, "0")).y(0)._state,
          np.array([0, 1j]), "y")


def test_z():
    check(QuantumCircuit(1, basis(1, "1")).z(0)._state,
          np.array([0, -1]), "z")


def test_h():
    check(QuantumCircuit(1, basis(1, "0")).h(0)._state,
          np.array([1, 1]) / np.sqrt(2), "h")


def test_s():
    check(QuantumCircuit(1, basis(1, "1")).s(0)._state,
          np.array([0, 1j]), "s")


# ------------------------------------------------------------ controlled
def test_cnot():
    check(QuantumCircuit(2, basis(2, "10")).cnot(0, 1)._state,
          basis(2, "11"), "cnot on")
    check(QuantumCircuit(2, basis(2, "00")).cnot(0, 1)._state,
          basis(2, "00"), "cnot off")


def test_ch():
    check(QuantumCircuit(2, basis(2, "00")).ch(0, 1)._state,
          basis(2, "00"), "ch off")
    check(QuantumCircuit(2, basis(2, "10")).ch(0, 1)._state,
          np.array([0, 0, 1, 1]) / np.sqrt(2), "ch on")


def test_cz():
    check(QuantumCircuit(2, basis(2, "11")).cz(0, 1)._state,
          -basis(2, "11"), "cz on")
    check(QuantumCircuit(2, basis(2, "01")).cz(0, 1)._state,
          basis(2, "01"), "cz off")


# ------------------------------------------------------------ multi-qubit
def test_toffoli():
    check(QuantumCircuit(3, basis(3, "110")).toffoli(0, 1, 2)._state,
          basis(3, "111"), "toffoli on")
    check(QuantumCircuit(3, basis(3, "100")).toffoli(0, 1, 2)._state,
          basis(3, "100"), "toffoli off")


def test_ccx():
    check(QuantumCircuit(3, basis(3, "110")).ccx(0, 1, 2)._state,
          basis(3, "111"), "ccx")


def test_mcx():
    check(QuantumCircuit(4, basis(4, "1110")).mcx([0, 1, 2], 3)._state,
          basis(4, "1111"), "mcx on")
    check(QuantumCircuit(4, basis(4, "1100")).mcx([0, 1, 2], 3)._state,
          basis(4, "1100"), "mcx off")


def test_multi_controlled():
    psi = basis(2, "11")
    check(QuantumCircuit(2, psi).multi_controlled(QuantumCircuit.Z, [0], 1)._state,
          QuantumCircuit(2, psi).cz(0, 1)._state,
          "multi_controlled = cz")


def test_swap():
    check(QuantumCircuit(2, basis(2, "01")).swap(0, 1)._state,
          basis(2, "10"), "swap 01")
    check(QuantumCircuit(2, basis(2, "10")).swap(0, 1)._state,
          basis(2, "01"), "swap 10")


def test_fredkin():
    check(QuantumCircuit(3, basis(3, "101")).fredkin(0, 1, 2)._state,
          basis(3, "110"), "fredkin on")
    check(QuantumCircuit(3, basis(3, "001")).fredkin(0, 1, 2)._state,
          basis(3, "001"), "fredkin off")


def test_cswap():
    check(QuantumCircuit(3, basis(3, "101")).cswap(0, 1, 2)._state,
          basis(3, "110"), "cswap")


# ------------------------------------------------------------ internals
def test_operator():
    M = QuantumCircuit(2)._operator({0: QuantumCircuit.X})
    check(M, np.kron(QuantumCircuit.X, QuantumCircuit.I), "_operator")


def test_probabilities():
    qc = QuantumCircuit(1, basis(1, "0")).h(0)
    check(qc.probabilities(), [0.5, 0.5], "probabilities")


def test_probabilities_and_indices():
    qc = QuantumCircuit(2, basis(2, "00")).h(0).cnot(0, 1)
    p, idx = qc._probabilities_and_indices(0, 1)
    check(p, 0.5, "_probabilities_and_indices probability")
    check(idx, [2, 3], "_probabilities_and_indices indices")


def test_outcome_probability():
    qc = QuantumCircuit(2, basis(2, "00")).h(0).cnot(0, 1)
    check([qc.outcome_probability(0, 0), qc.outcome_probability(0, 1)],
          [0.5, 0.5], "outcome_probability")


# ------------------------------------------------------------ measurement
def test_measure():
    assert QuantumCircuit(1, basis(1, "0")).measure(0) == 0
    assert QuantumCircuit(1, basis(1, "1")).measure(0) == 1

    qc = QuantumCircuit(1, basis(1, "0")).h(0)
    first = qc.measure(0)
    assert qc.measure(0) == first, "re-measuring a collapsed qubit must agree"

    print("ok   measure")



TESTS = [
    test_initial_state,
    test_x, test_y, test_z, test_h, test_s,
    test_cnot, test_ch, test_cz,
    test_toffoli, test_ccx, test_mcx, test_multi_controlled,
    test_swap, test_fredkin, test_cswap,
    test_operator,
    test_probabilities, test_probabilities_and_indices, test_outcome_probability,
    test_measure
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print(f"\n{len(TESTS)} tests passed")