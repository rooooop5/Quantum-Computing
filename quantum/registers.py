class Qubit:
    def __init__(self):
        self._idx=None

class ClassicalBit:
    def __init__(self):
        self._idx=None

class Register:
    bit_type=None
    def __init__(self,size:int,name:str):
        self.name=name
        self.size=size
        self._bits=[self.bit_type() for _ in range(self.size)]

    def __len__(self):
        return self.size

    def __iter__(self):
        return iter(self._bits)

    def __getitem__(self, key):
        return self._bits[key]

    
class QuantumRegister(Register):
    bit_type=Qubit

class ClassicalRegister(Register):
    bit_type=ClassicalBit

