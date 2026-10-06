# -*- coding: utf-8 -*-
from production_readiness import ProductionReadiness
from runtime_mode import (allowed_mode, RUNTIME_READONLY, RUNTIME_DEVELOPMENT,
                          RUNTIME_PRODUCTION)


def _all_true():
    return ProductionReadiness(True, True, True, True, True, True, True)


def test_all_false_blocks():
    r = ProductionReadiness()
    assert r.can_enable_real_money_trade() is False
    assert len(r.blockers()) == 7


def test_all_true_allows():
    r = _all_true()
    assert r.can_enable_real_money_trade() is True
    assert r.blockers() == []


def test_missing_one_blocks():
    r = ProductionReadiness(True, True, True, True, True, True, False)
    assert r.can_enable_real_money_trade() is False
    assert r.blockers() == ["manifestVerified"]


def test_allowed_mode_production():
    assert allowed_mode(_all_true(), True) == RUNTIME_PRODUCTION


def test_allowed_mode_development():
    r = ProductionReadiness(identity_verified=True)  # inventory/storage 未验证
    assert allowed_mode(r, True) == RUNTIME_DEVELOPMENT


def test_allowed_mode_readonly():
    r = ProductionReadiness()
    assert allowed_mode(r, False) == RUNTIME_READONLY


def test_identity_not_verified_never_production():
    # 即使 readiness 全真，identity 未验证也不能 production
    assert allowed_mode(_all_true(), False) != RUNTIME_PRODUCTION
