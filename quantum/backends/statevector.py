import numpy as np

class StateVector:
    X=np.array([[0,1],[1,0]],dtype=complex)
    Y=np.array([[0,-1j],[1j,0]],dtype=complex)
    Z=np.array([[1,0],[0,-1]],dtype=complex)
    H=(np.array([[1,1],[1,-1]],dtype=complex))/np.sqrt(2)
    S=np.array([[1,0],[0,1j]],dtype=complex)
    P0 = np.array([[1, 0], [0, 0]], dtype=complex)
    P1 = np.array([[0, 0], [0, 1]], dtype=complex) 
    I=np.eye(2,dtype=complex)
    rng=np.random.default_rng()

    def __init__(self,n:int,initial_state:list[complex] | None = None):
        # the no. of qubits
        self.n=n
        self.dispatcher={'x':self.x,'y':self.y,'z':self.z,'h':self.h,'cnot':self.cnot,'ccx':self.ccx,'cz':self.cz,'cx':self.cnot}

        # if no initial state is given, the initial state is taken to 
        # be one for qubit 0 and 0 for others
        if initial_state is None:
            self._state=np.zeros(2**n,dtype=complex)
            self._state[0]=1
            

        else:
            # making sure the provided state is valid
            # no. of states must be 2**n
            if len(initial_state) != 2**n:
                raise ValueError(f"there must be {2**n} states")

            sum_of_sqs=np.sum(np.abs(initial_state)**2)

            # the probabilities of the states should add upto one
            if not np.isclose(sum_of_sqs,1):
                raise ValueError("sum of amplitudes not close to 1")

            self._state=np.array(initial_state,dtype=complex)

    def probabilities(self):
        return np.abs(self._state)**2

    def _operator(self,gates:dict[int,np.ndarray]):

        op=np.eye(1)

        for q in range(self.n-1,-1,-1):
            op=np.kron(op,gates.get(q,StateVector.I))

        return op

    def x(self,op):
        target=op[0]
        op=self._operator({target:StateVector.X})

        self._state=op @ self._state

        return self

    def y(self,op):
        target=op[0]
        op=self._operator({target:StateVector.Y})

        self._state=op @ self._state

        return self

    def z(self,op:tuple):
        target=op[0]
        op=self._operator({target:StateVector.Z})

        self._state=op @ self._state

        return self

    def h(self,op:tuple):
        target=op[0]
        op=self._operator({target:StateVector.H})

        self._state=op @ self._state

        return self

    def s(self,op:tuple):
        target=op[0]
        op=self._operator({target:StateVector.S})

        self._state=op @ self._state

        return self

    def _controlled_matrix(self,U:np.ndarray,control:int,target:int):
        if not np.shape(U)==(2,2):
            raise ValueError(f"{U} should be a 2x2 matrix")

        if not (0 <= control <= self.n):
            raise IndexError("control qubit out of range")

        if not (0 <= target <= self.n):
            raise IndexError("target qubit out of range")

        control_zero_operator=self._operator({control:self.P0})
        control_one_operator=self._operator({control:self.P1,target:U})

        return control_zero_operator+control_one_operator

    def cnot(self,op:tuple):
        control,target=op
        op=self._controlled_matrix(StateVector.X,control,target)

        self._state= op @ self._state

        return self

    def ch(self,op:tuple):
        control,target=op
        op=self._controlled_matrix(StateVector.H,control,target)

        self._state= op @ self._state

        return self

    def cz(self,op:tuple):
        control,target=op
        op=self._controlled_matrix(StateVector.Z,control,target)

        self._state= op @ self._state

        return self

    def _check_qubits(self,*qubits):
        for q in qubits:
            if not (0 <= q < self.n):
                raise IndexError(f"{q} is out of range for range {self.n}")

        if len(set(qubits))!=len(qubits):
            raise ValueError("qubits must be distinct")

    def multi_controlled(self,U:np.ndarray,controls:list[int],target:int):
        if not np.shape(U)==(2,2):
            raise ValueError(f"{U} should be a 2x2 matrix")

        controls=list(controls)

        self._check_qubits(*(controls+[target]))

        all_one=self._operator({})

        for c in controls:
            all_one=all_one @ self._operator({c:StateVector.P1})

        identity=self._operator({})

        op=identity-all_one+all_one @ self._operator({target:U})

        self._state=op @ self._state

        return self

    def toffoli(self,control1:int,control2:int,target:int):
        return self.multi_controlled(StateVector.X,[control1,control2],target)

    def ccx(self,op):
        control1,control2,target=op
        # alias for toffoli
        return self.toffoli(control1,control2,target)

    def _probabilities_and_indices(self,qubit:int,outcome:int):
        if not (0<=qubit<=self.n):
            raise IndexError(f"{qubit} is out of range for range {self.n}")

        if outcome not in (0,1):
            raise ValueError(f"outcome not in (0,1)")
        
        idx=np.arange(2**self.n)

        outcome_idx=[i for i in idx if ((i>>qubit)&1)==outcome]

        probability=0

        for i in outcome_idx:
            probability+=np.abs(self._state[i])**2

        return probability,outcome_idx

    def outcome_probability(self,qubit:int,outcome:int):
        outcome_prob,_=self._probabilities_and_indices(qubit,outcome)

        return outcome_prob

    def measure(self,qubit:int):
        p0,idx0=self._probabilities_and_indices(qubit,outcome=0)
        p1,idx1=self._probabilities_and_indices(qubit,outcome=1)

        measured_bit=StateVector.rng.choice([0,1],p=[p0,p1])

        keep=idx0 if measured_bit==0 else idx1

        new=np.zeros(2**self.n,dtype=complex)

        for i in keep:
            new[i]=self._state[i]

        normalisation_constant=np.sqrt(1/(np.sum(np.abs(new**2))))

        new=normalisation_constant*new

        self._state=new

        return measured_bit

    def dispatch(self,op):
        fn=self.dispatcher.get(op[0],None)

        if fn is None:
            raise ValueError("the given gate does is not supported")
        
        fn(op[1:])