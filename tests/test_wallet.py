# -*- coding: utf-8 -*-
import pytest
from wallet import MemoryWallet
from errors import InsufficientFunds, InvalidQuantity


def test_balance_defaults_zero():
    w = MemoryWallet()
    assert w.balance("alice") == 0


def test_credit_and_debit():
    w = MemoryWallet()
    w.credit("alice", 100)
    w.debit("alice", 40)
    assert w.balance("alice") == 60


def test_debit_insufficient_raises():
    w = MemoryWallet()
    w.credit("alice", 10)
    with pytest.raises(InsufficientFunds):
        w.debit("alice", 11)


def test_credit_negative_raises():
    w = MemoryWallet()
    with pytest.raises(InvalidQuantity):
        w.credit("alice", -1)


def test_credit_zero_is_noop():
    w = MemoryWallet()
    w.credit("alice", 100)
    w.credit("alice", 0)  # no-op
    assert w.balance("alice") == 100


def test_total_balance():
    w = MemoryWallet()
    w.credit("a", 100)
    w.credit("b", 200)
    assert w.total_balance() == 300


def test_snapshot_round_trip():
    w = MemoryWallet()
    w.credit("a", 50)
    w.credit("b", 75)
    w2 = MemoryWallet.from_snapshot(w.snapshot())
    assert w2.balance("a") == 50
    assert w2.balance("b") == 75
    assert w2.total_balance() == 125
