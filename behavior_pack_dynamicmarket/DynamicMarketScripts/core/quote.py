# -*- coding: utf-8 -*-
"""报价（Quote）辅助：TTL 与市场版本校验。

报价是无副作用的询价结果，锁定价格/数量/市场版本。confirm 时若已过期
或市场版本变化，则要求重新报价（replacement）。
"""
from errors import QuoteExpired, QuoteStale


def is_expired(quote, now):
    """TTL 过期判断。expires_at == 0 表示永不过期。"""
    if quote["expires_at"] == 0:
        return False
    return now >= quote["expires_at"]


def is_stale(quote, current_market_version):
    """市场版本是否已变化（变化则报价失效）。"""
    return quote["market_version"] != current_market_version


def validate(quote, now, current_market_version):
    """校验报价有效性，通过返回 quote，失败抛异常。"""
    if is_expired(quote, now):
        raise QuoteExpired("quote %r expired at %r (now=%r)"
                           % (quote["quote_id"], quote["expires_at"], now))
    if is_stale(quote, current_market_version):
        raise QuoteStale("quote %r stale (version %r != %r)"
                         % (quote["quote_id"], quote["market_version"],
                            current_market_version))
    return quote
