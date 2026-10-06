# -*- coding: utf-8 -*-
"""DynamicMarket 核心异常体系。

纯 Python，不依赖网易 API。金额/库存/价格全部为整数，异常用于守卫
货币守恒、库存非负、订单状态机等不变量。
"""


class DynamicMarketError(Exception):
    """所有经济系统异常的基类。可携带稳定 error code。"""

    def __init__(self, message="", code=None):
        super(DynamicMarketError, self).__init__(message)
        self.code = code


class InvariantViolation(DynamicMarketError):
    """不变量被破坏（如 MoneySupply 为负、库存为负）。"""
    pass


class IdentityNotVerified(DynamicMarketError):
    """身份持久性未验证，禁止需要长期账户的真实交易。"""
    pass


class InsufficientFunds(DynamicMarketError):
    """余额不足。"""
    pass


class InsufficientStock(DynamicMarketError):
    """物品库存不足。"""
    pass


class InsufficientEscrow(DynamicMarketError):
    """托管物品不足。"""
    pass


class OrderNotFound(DynamicMarketError):
    """订单不存在。"""
    pass


class OrderNotOpen(DynamicMarketError):
    """订单状态不允许当前操作（已成交/已取消/已过期）。"""
    pass


class OrderExpired(DynamicMarketError):
    """订单已过期。"""
    pass


class QuoteNotFound(DynamicMarketError):
    """报价不存在。"""
    pass


class QuoteExpired(DynamicMarketError):
    """报价已过期。"""
    pass


class QuoteStale(DynamicMarketError):
    """报价对应的市场版本已变化，价格需要重报。"""
    pass


class InvalidQuantity(DynamicMarketError):
    """数量非法（非正数等）。"""
    pass


class InvalidPrice(DynamicMarketError):
    """价格非法（负数等）。"""
    pass


class ItemNotReceivable(DynamicMarketError):
    """物品无法进入目标（背包满/空间不足）。"""
    pass


class ClaimNotFound(DynamicMarketError):
    """领取条目不存在。"""
    pass


class StorageError(DynamicMarketError):
    """持久化存储异常基类。"""
    pass


class StorageCorrupted(StorageError):
    """存储数据校验失败（checksum 不匹配）。"""
    pass


class SchemaVersionError(StorageError):
    """存储 schemaVersion 不受支持或迁移失败。"""
    pass
