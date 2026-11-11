
import numpy as np
import pytest

from quantum import QuantumCircuit, QuantumRegister, ClassicalRegister,Simulator, Basis, StateVector


def run(circuit, method="matrix_product_state", shots=1):
    return Simulator(method).run(circuit, shots=shots).result().get_counts()


def test_x():
    a = QuantumRegister(1, "a")
    out = ClassicalRegister(1, "o")
    qc = QuantumCircuit(a, out)
    qc.x(a[0]).measure(a[0], out[0])
    assert run(qc) == {"1": 1}


def test_cx():
    a = QuantumRegister(2, "a")
    out = ClassicalRegister(2, "o")
    qc = QuantumCircuit(a, out)
    qc.x(a[0]).cx(a[0], a[1])
    qc.measure(a[0], out[0]).measure(a[1], out[1])
    assert run(qc) == {"11": 1}


def test_toffoli():
    a = QuantumRegister(3, "a")
    out = ClassicalRegister(1, "o")
    qc = QuantumCircuit(a, out)
    qc.x(a[0]).x(a[1]).ccx(a[0], a[1], a[2])
    qc.measure(a[2], out[0])
    assert run(qc) == {"1": 1}


def test_toffoli_off():
    a = QuantumRegister(3, "a")
    out = ClassicalRegister(1, "o")
    qc = QuantumCircuit(a, out)
    qc.x(a[0]).ccx(a[0], a[1], a[2])     # second control is 0
    qc.measure(a[2], out[0])
    assert run(qc) == {"0": 1}


def test_shots_repeat():
    a = QuantumRegister(2, "a")
    out = ClassicalRegister(2, "o")
    qc = QuantumCircuit(a, out)
    qc.x(a[0]).cx(a[0], a[1])
    qc.measure(a[0], out[0]).measure(a[1], out[1])
    assert run(qc, shots=1000) == {"11": 1000}


def test_automatic_method():
    a = QuantumRegister(1, "a")
    out = ClassicalRegister(1, "o")
    qc = QuantumCircuit(a, out)
    qc.x(a[0]).measure(a[0], out[0])
    assert run(qc, method="automatic") == {"1": 1}


def test_auto_picks_basis():
    a = QuantumRegister(1, "a")
    out = ClassicalRegister(1, "o")
    qc = QuantumCircuit(a, out)
    qc.x(a[0]).measure(a[0], out[0])
    sim = Simulator("automatic")
    assert isinstance(sim.make_engine(qc, sim.backend), Basis)


def test_two_classical_registers():
    a = QuantumRegister(2, "a")
    qout = ClassicalRegister(1, "q")
    rout = ClassicalRegister(1, "r")
    qc = QuantumCircuit(a, qout, rout)

    qc.x(a[1]).measure(a[1], rout[0])    # rout = 1
    qc.measure(a[0], qout[0])            # qout = 0

    # rout added last -> leftmost: "1" + "0"
    assert run(qc) == {"10": 1}


def test_unmeasured_clbit_is_zero():
    a = QuantumRegister(2, "a")
    out = ClassicalRegister(2, "o")
    qc = QuantumCircuit(a, out)
    qc.x(a[0]).measure(a[0], out[0])     # out[1] never measured
    assert run(qc) == {"01": 1}


def test_basis_matches_statevector():
    ops = [("x", 0), ("cx", 0, 1), ("ccx", 1, 2, 3), ("x", 2)]

    b = Basis(4)
    s = StateVector(4)
    for op in ops:
        b.dispatch(op)
        s.dispatch(op)

    index = int(np.argmax(np.abs(s._state)))
    assert index == b.bits


def test_unknown_gate_on_basis():
    with pytest.raises(ValueError):
        Basis(2).dispatch(("h", 0))