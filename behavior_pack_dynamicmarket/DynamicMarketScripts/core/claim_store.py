# -*- coding: utf-8 -*-
"""领取（Claim）存储。

买家成交后物品进入 Claim（账本记录），随后通过 claim 领取到背包。
成交与发放分离，避免成交时背包满导致复杂回滚。
"""
from models import new_claim, CLAIM_PENDING, CLAIM_CLAIMED
from errors import ClaimNotFound


class ClaimStore(object):
    def __init__(self, id_generator):
        self._id_gen = id_generator
        self._claims = {}  # claim_id -> claim

    def add(self, player, item_id, quantity, unit_price, created_at):
        claim = new_claim(self._id_gen.next(), player, item_id, quantity,
                          unit_price, created_at)
        self._claims[claim["claim_id"]] = claim
        return claim

    def get(self, claim_id):
        return self._claims.get(claim_id)

    def require(self, claim_id):
        claim = self._claims.get(claim_id)
        if claim is None:
            raise ClaimNotFound("claim %r not found" % claim_id)
        return claim

    def pending(self, player):
        return [c for c in self._claims.values()
                if c["player"] == player and c["status"] == CLAIM_PENDING]

    def mark_claimed(self, claim_id):
        claim = self.require(claim_id)
        claim["status"] = CLAIM_CLAIMED
        return claim

    def pending_quantity(self, player, item_id):
        total = 0
        for c in self._claims.values():
            if c["player"] == player and c["item_id"] == item_id \
                    and c["status"] == CLAIM_PENDING:
                total += c["quantity"]
        return total

    def snapshot(self):
        return [dict(c) for c in self._claims.values()]

    @classmethod
    def from_snapshot(cls, claims, id_generator):
        obj = cls(id_generator)
        obj._claims = {}
        for c in claims:
            obj._claims[c["claim_id"]] = dict(c)
        max_id = max([c["claim_id"] for c in claims] or [0])
        obj._id_gen.ensure_above(max_id)
        return obj
