"""Small tests for the StateVector backend."""

import numpy as np
import pytest

from backends.statevector import StateVector
from backends.basis import Basis


def basis_state(n, index):
    psi = np.zeros(2 ** n, dtype=complex)
    psi[index] = 1.0
    return psi


def test_initial_state():
    s = StateVector(2)
    assert np.allclose(s._state, basis_state(2, 0))


def test_given_state():
    s = StateVector(2, basis_state(2, 2))
    assert np.allclose(s._state, basis_state(2, 2))


def test_x_on_qubit_0():
    s = StateVector(2)
    s.dispatch(("x", 0))
    assert np.allclose(s._state, basis_state(2, 0b01))


def test_x_on_qubit_1():
    s = StateVector(2)
    s.dispatch(("x", 1))
    assert np.allclose(s._state, basis_state(2, 0b10))


def test_h():
    s = StateVector(1)
    s.dispatch(("h", 0))
    assert np.allclose(s._state, [1, 1] / np.sqrt(2))


def test_bell():
    s = StateVector(2)
    s.dispatch(("h", 0))
    s.dispatch(("cx", 0, 1))
    assert np.allclose(s._state, [1, 0, 0, 1] / np.sqrt(2))


def test_cz_phase():
    s = StateVector(2, basis_state(2, 0b11))
    s.dispatch(("cz", 0, 1))
    assert np.allclose(s._state, [0, 0, 0, -1])


def test_toffoli():
    s = StateVector(3, basis_state(3, 0b011))   # q0 = q1 = 1
    s.dispatch(("ccx", 0, 1, 2))
    assert np.allclose(s._state, basis_state(3, 0b111))


def test_toffoli_off():
    s = StateVector(3, basis_state(3, 0b001))   # q0 = 1, q1 = 0
    s.dispatch(("ccx", 0, 1, 2))
    assert np.allclose(s._state, basis_state(3, 0b001))


def test_probabilities():
    s = StateVector(1)
    s.dispatch(("h", 0))
    assert np.allclose(s.probabilities(), [0.5, 0.5])


def test_outcome_probability():
    s = StateVector(1)
    s.dispatch(("h", 0))
    assert np.isclose(s.outcome_probability(0, 0), 0.5)
    assert np.isclose(s.outcome_probability(0, 1), 0.5)


def test_measure_is_deterministic_on_basis_state():
    s = StateVector(1, basis_state(1, 1))
    assert s.measure(0) == 1


def test_measure_collapses():
    s = StateVector(1)
    s.dispatch(("h", 0))

    outcome = s.measure(0)
    assert outcome in (0, 1)

    expected = basis_state(1, outcome)
    assert np.allclose(s._state, expected)
    assert s.measure(0) == outcome


def test_basis_and_statevector_agree():
    ops = [("x", 0), ("cx", 0, 1), ("ccx", 1, 2, 3), ("x", 2)]

    s = StateVector(4)
    b = Basis(4)
    for op in ops:
        s.dispatch(op)
        b.dispatch(op)

    index = int(np.argmax(np.abs(s._state)))
    assert index == b.bits


def test_rejects_wrong_length():
    with pytest.raises(ValueError):
        StateVector(2, [1, 0])


def test_rejects_unnormalized():
    with pytest.raises(ValueError):
        StateVector(1, [1, 1])


def test_unknown_gate():
    with pytest.raises(ValueError):
        StateVector(1).dispatch(("q", 0))