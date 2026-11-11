from circuits import QuantumCircuit
from backends.statevector import StateVector
from backends.basis import Basis

class Result:
    def __init__(self,counts:dict):
        self.counts=counts

    def get_counts(self):
        return self.counts

class Job:
    def __init__(self,counts:dict):
        self.counts=counts

    def result(self):
        return Result(self.counts)

class Simulator:
    def __init__(self,method:str="auto"):
        self.backend=self._backend(method)

    def _backend(self,method):
        mapping={"automatic":"auto","auto":"auto","matrix_product_state":"basis","statevector":"statevector"}

        return mapping.get(method)


    def make_engine(self,circuit:QuantumCircuit,backend:str="auto",shots=1):
        if backend=="auto":
            allowed=["ccx","cx","x","measure"] 
            backend="basis" if all(op[0] in allowed for op in circuit.ops) else "statevector"

        if backend=="statevector":
            engine=StateVector(n=circuit.q_idx)
        elif backend=="basis":
            engine=Basis(circuit.q_idx)

        return engine

    def counts_key(self,circuit,classical):
        keys=[]
        for creg in circuit.cregs[::-1]:
            key="".join(str(classical[bit._idx]) for bit in creg[::-1])
            keys.append(key)

        return "".join(keys)  

    def run(self,circuit:QuantumCircuit,shots:int=1):
        counts={}

        for i in range(shots):
            engine=self.make_engine(circuit,self.backend,shots)

            classical=[0]*circuit.c_idx

            for op in circuit.ops:
                if op[0]!='measure':
                    engine.dispatch(op)
                else:
                    classical[op[2]]=engine.measure(op[1])

            key=self.counts_key(circuit,classical)

            counts[key]=counts.get(key,0)+1

        return Job(counts)