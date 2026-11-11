class Basis:
    def __init__(self, n: int, initial_state: int = 0):
        if not isinstance(n, int) or n < 1:
            raise ValueError("n must be a positive integer")
        if not (0 <= initial_state < 2 ** n):
            raise ValueError("initial_state does not fit in n bits")

        self.n = n
        self.bits = initial_state
        self.dispatcher = {
            'x': self.x,
            'cx': self.cx,
            'ccx': self.ccx,
        }

    def _check_qubits(self, *qubits):
        for q in qubits:
            if not (0 <= q < self.n):
                raise IndexError(f"{q} is out of range for range {self.n}")

        if len(set(qubits)) != len(qubits):
            raise ValueError("qubits must be distinct")

    def bit(self, qubit: int) -> int:
        return (self.bits >> qubit) & 1

    def x(self, op: tuple):
        target = op[0]
        self._check_qubits(target)

        self.bits ^= 1 << target

        return self

    def cx(self, op: tuple):
        control, target = op
        self._check_qubits(control, target)

        if self.bit(control):
            self.bits ^= 1 << target

        return self

    def ccx(self, op: tuple):
        control1, control2, target = op
        self._check_qubits(control1, control2, target)

        if self.bit(control1) and self.bit(control2):
            self.bits ^= 1 << target

        return self

    def measure(self, qubit: int):
        self._check_qubits(qubit)
        return self.bit(qubit)

    def dispatch(self, op):
        fn = self.dispatcher.get(op[0], None)

        if fn is None:
            raise ValueError("the given gate is not supported by the basis backend")

        fn(op[1:])

    def __str__(self):
        return format(self.bits, f"0{self.n}b")