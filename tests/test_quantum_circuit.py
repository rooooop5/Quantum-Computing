from registers import QuantumRegister,ClassicalRegister
from circuits import QuantumCircuit

def make():
    a = QuantumRegister(3,'a')        # qubits 0,1,2
    b = QuantumRegister(2,'b')        # qubits 3,4
    c = QuantumRegister(1,'c')        # qubit 5
    out = ClassicalRegister(2,'out')  # clbits 0,1
    return QuantumCircuit(a, b, c, out), a, b, c, out


def test_empty():
    qc = QuantumCircuit()
    assert qc.ops == [] and qc.q_idx == 0 and qc.c_idx == 0


def test_indices():
    qc, a, b, c, out = make()
    assert a[0]._idx == 0 and a[2]._idx == 2
    assert b[0]._idx == 3 and b[1]._idx == 4
    assert c[0]._idx == 5
    assert out[0]._idx == 0 and out[1]._idx == 1
    assert qc.q_idx == 6 and qc.c_idx == 2


def test_registers():
    qc, a, b, c, out = make()
    assert qc.qregs == [a, b, c]
    assert qc.cregs == [out]
    assert len(a) == 3 and list(b) == [b[0], b[1]]
    assert a[1:] == [a[1], a[2]]


def test_gates_record():
    qc, a, b, c, out = make()
    qc.x(a[1])
    qc.cx(a[0], b[1])
    qc.ccx(a[0], b[1], c[0])
    qc.measure(c[0], out[1])
    assert qc.ops == [
        ("x", 1),
        ("cx", 0, 4),
        ("ccx", 0, 4, 5),
        ("measure", 5, 1),
    ]


def test_chaining():
    qc, a, b, c, out = make()
    assert qc.x(a[0]).cx(a[0], b[0]) is qc
    assert len(qc.ops) == 2
    print(qc.ops)


def test_no_state():
    qc, a, b, c, out = make()
    assert not hasattr(qc, "_state")


if __name__ == "__main__":
    for test in (test_empty, test_indices, test_registers,
                 test_gates_record, test_chaining, test_no_state):
        test()
        print("ok  ", test.__name__)
    print("\n6 tests passed")