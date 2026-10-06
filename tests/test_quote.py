# -*- coding: utf-8 -*-
import pytest
from models import new_quote
from quote import is_expired, is_stale, validate
from errors import QuoteExpired, QuoteStale


def test_is_expired():
    q = new_quote(1, "iron", "BUY", 10, 100, 5, 0, 30)
    assert is_expired(q, 29) is False
    assert is_expired(q, 30) is True


def test_never_expires():
    q = new_quote(1, "iron", "BUY", 10, 100, 5, 0, 0)
    assert is_expired(q, 999999) is False


def test_is_stale():
    q = new_quote(1, "iron", "BUY", 10, 100, 5, 0, 30)
    assert is_stale(q, 5) is False
    assert is_stale(q, 6) is True


def test_validate_ok():
    q = new_quote(1, "iron", "BUY", 10, 100, 5, 0, 30)
    assert validate(q, 10, 5) is q


def test_validate_expired():
    q = new_quote(1, "iron", "BUY", 10, 100, 5, 0, 30)
    with pytest.raises(QuoteExpired):
        validate(q, 30, 5)


def test_validate_stale():
    q = new_quote(1, "iron", "BUY", 10, 100, 5, 0, 30)
    with pytest.raises(QuoteStale):
        validate(q, 10, 6)
