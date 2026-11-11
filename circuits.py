from registers import QuantumRegister,ClassicalRegister,Qubit,Register,ClassicalBit

class QuantumCircuit:

    def __init__(self,*registers):
        self.qregs=[]
        self.cregs=[]
        self.ops=[]
        self.q_idx=0
        self.c_idx=0
        for reg in registers:
            self.add_register(reg)

    def add_register(self,*registers:tuple[Register]):
        for reg in (registers):
            if isinstance(reg,QuantumRegister):
                self.qregs.append(reg)
                for qbit in reg:
                    qbit._idx=self.q_idx
                    self.q_idx+=1

            if isinstance(reg,ClassicalRegister):
                self.cregs.append(reg)
                for cbit in reg:
                    cbit._idx=self.c_idx
                    self.c_idx+=1

    def x(self,qbit:Qubit):
        self.ops.append(('x',qbit._idx))
        return self

    def ccx(self,control1:Qubit,control2:Qubit,qbit:Qubit):
        self.ops.append(('ccx',control1._idx,control2._idx,qbit._idx))
        return self

    def cx(self,control:Qubit,qbit:Qubit):
        self.ops.append(('cx',control._idx,qbit._idx))
        return self

    def measure(self,qbit:Qubit,clbit:ClassicalBit,):
        self.ops.append(('measure',qbit._idx,clbit._idx,))
        return self
