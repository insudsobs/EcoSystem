# -*- coding: utf-8 -*-
import pytest
from monetary import MoneySupply
from errors import InvariantViolation


def test_initial_total():
    m = MoneySupply(initial=1000)
    assert m.total() == 1000


def test_issue_increases_total():
    m = MoneySupply(initial=0)
    m.issue(500)
    assert m.total() == 500


def test_destroy_decreases_total():
    m = MoneySupply(initial=1000)
    m.destroy(400)
    assert m.total() == 600


def test_destroy_more_than_total_raises():
    m = MoneySupply(initial=100)
    with pytest.raises(InvariantViolation):
        m.destroy(101)


def test_issue_negative_raises():
    m = MoneySupply()
    with pytest.raises(InvariantViolation):
        m.issue(-1)


def test_destroy_zero_is_noop():
    m = MoneySupply(initial=100)
    m.destroy(0)  # no-op
    assert m.total() == 100


def test_destroy_negative_raises():
    m = MoneySupply(initial=100)
    with pytest.raises(InvariantViolation):
        m.destroy(-1)


def test_assert_invariant_negative_raises():
    m = MoneySupply(initial=0)
    # 直接破坏不变量（绕过 destroy 检查）
    m.destroyed = 10
    with pytest.raises(InvariantViolation):
        m.assert_invariant()


def test_snapshot_round_trip():
    m = MoneySupply(initial=100)
    m.issue(50)
    m.destroy(20)
    m2 = MoneySupply.from_snapshot(m.snapshot())
    assert m2.total() == m.total() == 130
