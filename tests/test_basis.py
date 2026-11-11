"""Unit tests for the Basis backend."""

import pytest

from backends.basis import Basis


def test_default_state():
    b = Basis(3)
    assert b.bits == 0
    assert str(b) == "000"


def test_initial_state():
    b = Basis(3, 0b101)
    assert str(b) == "101"

def test_x():
    b = Basis(2)
    b.x((0,))
    assert b.bits == 0b01


def test_cx_on():
    b = Basis(2, 0b01)
    b.cx((0, 1))
    assert b.bits == 0b11


def test_cx_off():
    b = Basis(2, 0b10)
    b.cx((0, 1))
    assert b.bits == 0b10


def test_ccx_on():
    b = Basis(3, 0b011)    
    b.ccx((0, 1, 2))
    assert b.bits == 0b111


def test_ccx_off():
    b = Basis(3, 0b010)       
    b.ccx((0, 1, 2))
    assert b.bits == 0b010


def test_measure_is_deterministic():
    b = Basis(2, 0b10)
    assert b.measure(1) == 1
    assert b.measure(0) == 0
    assert b.bits == 0b10  


def test_dispatch():
    b = Basis(3)
    b.dispatch(("x", 0))
    b.dispatch(("cx", 0, 1))
    b.dispatch(("ccx", 0, 1, 2))
    assert b.bits == 0b111


def test_chaining():
    b = Basis(2)
    assert b.x((0,)).cx((0, 1)) is b


def test_invalid_n():
    with pytest.raises(ValueError):
        Basis(0)

def test_out_of_range():
    with pytest.raises(IndexError):
        Basis(2).x((2,))


def test_duplicate_qubits():
    with pytest.raises(ValueError):
        Basis(2).cx((0, 0))
