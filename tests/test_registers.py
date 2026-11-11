"""Tests for the QuantumCircuit recorder (Qiskit argument order)."""

from quantum import QuantumRegister, ClassicalRegister,QuantumCircuit


def make():
    a = QuantumRegister(3, "a")        # qubits 0,1,2
    b = QuantumRegister(2, "b")        # qubits 3,4
    c = QuantumRegister(1, "c")        # qubit 5
    out = ClassicalRegister(2, "out")  # clbits 0,1
    return QuantumCircuit(a, b, c, out), a, b, c, out


def test_empty():
    qc = QuantumCircuit()
    assert qc.ops == [] and qc.q_idx == 0 and qc.c_idx == 0


def test_indices():
    qc, a, b, c, out = make()
    assert [a[i]._idx for i in range(3)] == [0, 1, 2]
    assert [b[i]._idx for i in range(2)] == [3, 4]
    assert c[0]._idx == 5
    assert [out[i]._idx for i in range(2)] == [0, 1]
    assert qc.q_idx == 6 and qc.c_idx == 2


def test_registers():
    qc, a, b, c, out = make()
    assert qc.qregs == [a, b, c]
    assert qc.cregs == [out]
    assert len(a) == 3 and list(b) == [b[0], b[1]]
    assert a[1:] == [a[1], a[2]]


def test_ops():
    qc, a, b, c, out = make()
    qc.x(a[1])
    qc.cx(a[0], b[1])
    qc.ccx(a[0], b[1], c[0])
    qc.measure(c[0], out[1])           # measure(qubit, clbit)
    assert qc.ops == [
        ("x", 1),
        ("cx", 0, 4),
        ("ccx", 0, 4, 5),
        ("measure", 5, 1),
    ]


def test_measure_order():
    qc, a, b, c, out = make()
    qc.measure(b[1], out[0])           # qubit 4 -> clbit 0
    assert qc.ops == [("measure", 4, 0)]


def test_chaining():
    qc, a, b, c, out = make()
    assert qc.x(a[0]).cx(a[0], b[0]) is qc
    assert len(qc.ops) == 2


def test_no_state():
    qc, a, b, c, out = make()
    assert not hasattr(qc, "_state")


if __name__ == "__main__":
    for t in (test_empty, test_indices, test_registers, test_ops,
              test_measure_order, test_chaining, test_no_state):
        t()
        print("ok  ", t.__name__)
    print("\n7 tests passed")