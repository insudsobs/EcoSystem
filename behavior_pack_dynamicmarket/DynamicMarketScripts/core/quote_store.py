# -*- coding: utf-8 -*-
"""报价存储。"""
from errors import QuoteNotFound


class QuoteStore(object):
    def __init__(self):
        self._quotes = {}  # quote_id -> quote

    def put(self, quote):
        self._quotes[quote["quote_id"]] = quote
        return quote

    def get(self, quote_id):
        return self._quotes.get(quote_id)

    def require(self, quote_id):
        quote = self._quotes.get(quote_id)
        if quote is None:
            raise QuoteNotFound("quote %r not found" % quote_id)
        return quote

    def remove(self, quote_id):
        return self._quotes.pop(quote_id, None)

    def prune_expired(self, now):
        """清理已过期报价。"""
        from quote import is_expired
        expired = [qid for qid, q in self._quotes.items() if is_expired(q, now)]
        for qid in expired:
            del self._quotes[qid]
        return len(expired)

    def snapshot(self):
        return [dict(q) for q in self._quotes.values()]

    @classmethod
    def from_snapshot(cls, quotes):
        obj = cls()
        for q in quotes:
            obj._quotes[q["quote_id"]] = q
        return obj
