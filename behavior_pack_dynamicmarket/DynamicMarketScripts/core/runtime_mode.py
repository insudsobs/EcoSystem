# -*- coding: utf-8 -*-
"""服务器启动模式（RuntimeMode）。

CORE_ONLY           纯核心（Mac tests），无网易 Runtime。
RUNTIME_READONLY    只读行情/系统价格查询/临时报价。
RUNTIME_DEVELOPMENT session-only 交易（DEVELOPMENT_ONLY），不持久长期账户。
RUNTIME_PRODUCTION  真实生产，要求 identity/inventory/storage 全部验证。
"""

CORE_ONLY = "CORE_ONLY"
RUNTIME_READONLY = "RUNTIME_READONLY"
RUNTIME_DEVELOPMENT = "RUNTIME_DEVELOPMENT"
RUNTIME_PRODUCTION = "RUNTIME_PRODUCTION"


def allowed_mode(readiness, identity_verified):
    """根据验证状态决定允许的最高模式。

    规则：
      - 生产就绪 + identity 验证 -> RUNTIME_PRODUCTION
      - identity 验证（但 inventory/storage 未全验证）-> RUNTIME_DEVELOPMENT
      - identity 未验证 -> 最多 RUNTIME_READONLY
    """
    if readiness.can_enable_real_money_trade() and identity_verified:
        return RUNTIME_PRODUCTION
    if identity_verified:
        return RUNTIME_DEVELOPMENT
    return RUNTIME_READONLY


def mode_rank(mode):
    """模式等级，用于比较。"""
    order = {CORE_ONLY: 0, RUNTIME_READONLY: 1,
             RUNTIME_DEVELOPMENT: 2, RUNTIME_PRODUCTION: 3}
    return order.get(mode, -1)
