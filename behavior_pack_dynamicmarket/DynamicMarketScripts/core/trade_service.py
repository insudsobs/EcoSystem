# -*- coding: utf-8 -*-
"""交易服务：所有经济操作的事务编排。

buy 采用两阶段（plan -> commit）保证原子性：plan 只读试算，校验报价
有效性、余额与流动性；commit 只在 plan 通过后应用变更，因此要么全成，
要么全不执行。玩家买单按「最低价优先」动态穿越系统市场与玩家卖单，
同价优先玩家订单。
"""
import config as _cfg
from models import (new_sell_order, new_quote, SIDE_BUY, SIDE_SELL,
                    SOURCE_SYSTEM, SOURCE_PLAYER_ORDER, SYSTEM_SELLER,
                    ORDER_OPEN, CLAIM_PENDING)
from errors import (InvalidQuantity, InvalidPrice, InsufficientFunds,
                    InsufficientStock, OrderNotFound, QuoteNotFound,
                    QuoteStale, ClaimNotFound, InvariantViolation,
                    IdentityNotVerified)
from error_code import SYSTEM_BUYBACK_CLOSED, INSUFFICIENT_LIQUIDITY
import sell_order as _so
from quote import validate as validate_quote


class TradeService(object):
    def __init__(self, market, orderbook, escrow, claim_store, monetary,
                 wallet, inventory, fee_acc, fill_ledger, history, quote_store,
                 order_ids, quote_ids, clock, price_engine, registry):
        self.market = market
        self.orderbook = orderbook
        self.escrow = escrow
        self.claim_store = claim_store
        self.monetary = monetary
        self.wallet = wallet
        self.inventory = inventory
        self.fee_acc = fee_acc
        self.fill_ledger = fill_ledger
        self.history = history
        self.quote_store = quote_store
        self.order_ids = order_ids
        self.quote_ids = quote_ids
        self.clock = clock
        self.price_engine = price_engine
        self._registry = registry

    def _now(self, now):
        return now if now is not None else self.clock.now()

    @staticmethod
    def _check_account(account_id):
        """防御性守卫：长期资产操作不允许 account_id 为 None。"""
        if account_id is None:
            raise IdentityNotVerified("account_id must not be None")

    # ------------------------------------------------------------------
    # 报价
    # ------------------------------------------------------------------
    def quote_item(self, item_id, quantity, side, now=None):
        """生成无副作用报价。锁定参考价与 marketVersion。"""
        now = self._now(now)
        if quantity <= 0:
            raise InvalidQuantity("quote quantity must be positive: %r" % quantity)
        if side == SIDE_BUY:
            price = self.market.system_ask(item_id)
        elif side == SIDE_SELL:
            price = self.market.system_bid(item_id)
        else:
            raise InvalidQuantity("unknown side: %r" % side)
        quote = new_quote(self.quote_ids.next(), item_id, side, quantity, price,
                          self.market.version(), now,
                          now + _cfg.QUOTE_TTL_SECONDS)
        self.quote_store.put(quote)
        return quote

    # ------------------------------------------------------------------
    # 挂单 / 取消 / 过期
    # ------------------------------------------------------------------
    def place_sell_order(self, account_id, item_id, amount, unit_price,
                         expires_at=0, now=None):
        """玩家挂卖单：物品从背包移入 escrow。"""
        self._check_account(account_id)
        now = self._now(now)
        if amount <= 0:
            raise InvalidQuantity("order amount must be positive: %r" % amount)
        if unit_price <= 0:
            raise InvalidPrice("unit price must be positive: %r" % unit_price)
        self.inventory.remove_item(account_id, item_id, amount)
        order = new_sell_order(self.order_ids.next(), account_id, item_id, amount,
                               unit_price, now, expires_at)
        self.escrow.deposit(order)
        self.orderbook.add(order)
        self.market.bump_version()
        return order

    def cancel_order(self, account_id, order_id, now=None):
        """取消卖单：托管物品退回卖家背包。"""
        self._check_account(account_id)
        now = self._now(now)
        order = self.orderbook.get(order_id)
        _so.require_open(order)
        if order["seller"] != account_id:
            raise OrderNotFound("order %r does not belong to %r" % (order_id, account_id))
        _so.mark_cancelled(order)
        entry = self.escrow.release(order_id)
        self.inventory.add_item(account_id, entry["item_id"], entry["remaining"])
        self.market.bump_version()
        return order

    def expire_orders(self, now=None):
        """过期处理：到期订单的托管物品退回卖家背包。"""
        now = self._now(now)
        expired = []
        for order in self.orderbook.open_orders_all():
            if order["expires_at"] != 0 and now >= order["expires_at"]:
                _so.mark_expired(order)
                entry = self.escrow.release(order["order_id"])
                self.inventory.add_item(order["seller"], entry["item_id"],
                                        entry["remaining"])
                expired.append(order)
        if expired:
            self.market.bump_version()
        return expired

    # ------------------------------------------------------------------
    # 卖给系统
    # ------------------------------------------------------------------
    def sell_to_system(self, account_id, item_id, quantity, now=None):
        """玩家卖给系统：系统发行货币，库存增加。

        系统收购到 maxStock 为止：库存已满则拒绝，超量部分不收购。
        """
        self._check_account(account_id)
        now = self._now(now)
        if quantity <= 0:
            raise InvalidQuantity("sell quantity must be positive: %r" % quantity)
        current = self.market.system_stock(item_id)
        room = self._registry.max_stock(item_id) - current
        if room <= 0:
            raise InsufficientStock("system no longer buys %r (max stock reached)"
                                    % item_id, code=SYSTEM_BUYBACK_CLOSED)
        accepted = min(quantity, room)
        bid = self.market.system_bid(item_id)
        gross = accepted * bid
        self.inventory.remove_item(account_id, item_id, accepted)
        self.wallet.credit(account_id, gross)
        self.monetary.issue(gross)
        self.market.increase_stock(item_id, accepted)
        self.fill_ledger.record(item_id, SYSTEM_SELLER, account_id, SOURCE_SYSTEM, 0,
                                accepted, bid, gross, 0, SIDE_SELL, now)
        self.history.record_trade(item_id, bid, accepted, SIDE_SELL, now)
        self._snapshot_history(item_id, now)
        self.market.bump_version()
        return gross

    # ------------------------------------------------------------------
    # 买入（动态撮合）
    # ------------------------------------------------------------------
    def buy(self, account_id, item_id, quantity, quote_id, now=None):
        """玩家买入：按最低价优先动态穿越系统/玩家单。物品进入 Claim。"""
        self._check_account(account_id)
        now = self._now(now)
        if quantity <= 0:
            raise InvalidQuantity("buy quantity must be positive: %r" % quantity)
        quote = self.quote_store.require(quote_id)
        if quote["item_id"] != item_id:
            raise QuoteStale("quote item %r != %r" % (quote["item_id"], item_id))
        if quote["side"] != SIDE_BUY:
            raise QuoteStale("quote side %r != BUY" % quote["side"])
        if quote["quantity"] != quantity:
            raise QuoteStale("quote quantity %r != requested %r, replacement required"
                             % (quote["quantity"], quantity))
        validate_quote(quote, now, self.market.version())

        plan = self._plan_buy(account_id, item_id, quantity)
        fills = self._commit_buy(account_id, item_id, plan, now)
        return fills

    def _plan_buy(self, account_id, item_id, quantity):
        """试算撮合，不改状态。返回 plan 步骤列表。"""
        remaining = quantity
        total_cost = 0
        plan = []

        sim_stock = self.market.system_stock(item_id)
        open_orders = self.orderbook.open_orders(item_id)
        sim_remaining = {}
        for o in open_orders:
            sim_remaining[o["order_id"]] = o["remaining"]
        idx = 0
        p0 = self._registry.p0(item_id)
        t = self._registry.target_stock(item_id)

        while remaining > 0:
            ask = self.price_engine.ask(p0, t, sim_stock)

            best_oid = None
            best_price = None
            while idx < len(open_orders):
                o = open_orders[idx]
                if sim_remaining.get(o["order_id"], 0) > 0:
                    best_oid = o["order_id"]
                    best_price = o["unit_price"]
                    break
                idx += 1

            if best_price is not None and (sim_stock == 0 or best_price <= ask):
                source = SOURCE_PLAYER_ORDER
                price = best_price
                available = sim_remaining[best_oid]
                order_id = best_oid
            elif sim_stock > 0:
                source = SOURCE_SYSTEM
                price = ask
                # 每次仅成交 1 单位，重算 ask：系统价随库存下降而上涨，
                # 大单才能正确产生 SYSTEM->PLAYER_ORDER->SYSTEM 动态穿越。
                available = 1
                order_id = 0
            else:
                break

            take = min(remaining, available)
            gross = take * price
            total_cost += gross
            self._append_plan(plan, source, order_id, price, take, gross)
            remaining -= take
            if source == SOURCE_SYSTEM:
                sim_stock -= take
            else:
                sim_remaining[order_id] -= take
                if sim_remaining[order_id] == 0:
                    idx += 1

        if remaining > 0:
            raise InsufficientStock(
                "liquidity exhausted: cannot fill %r more of %r" % (remaining, item_id),
                code=INSUFFICIENT_LIQUIDITY)
        if self.wallet.balance(account_id) < total_cost:
            raise InsufficientFunds(
                "account_id %r balance %r < required %r"
                % (account_id, self.wallet.balance(account_id), total_cost))
        return plan

    @staticmethod
    def _append_plan(plan, source, order_id, price, quantity, gross):
        """合并连续同源同价的成交段，避免系统每次 1 单位导致 plan/fill 膨胀。"""
        if plan:
            last = plan[-1]
            if (last["source"] == source and last["order_id"] == order_id
                    and last["price"] == price):
                last["quantity"] += quantity
                last["gross"] += gross
                return
        plan.append({
            "source": source,
            "order_id": order_id,
            "price": price,
            "quantity": quantity,
            "gross": gross,
        })

    def _commit_buy(self, account_id, item_id, plan, now):
        """按 plan 应用成交。"""
        fills = []
        for step in plan:
            source = step["source"]
            order_id = step["order_id"]
            price = step["price"]
            quantity = step["quantity"]
            gross = step["gross"]

            self.wallet.debit(account_id, gross)
            if source == SOURCE_SYSTEM:
                self.monetary.destroy(gross)
                self.market.decrease_stock(item_id, quantity)
                self.claim_store.add(account_id, item_id, quantity, price, now)
                fills.append(self.fill_ledger.record(
                    item_id, account_id, SYSTEM_SELLER, SOURCE_SYSTEM, 0,
                    quantity, price, gross, 0, SIDE_BUY, now))
            else:
                seller, _item = self.escrow.consume(order_id, quantity)
                order = self.orderbook.get(order_id)
                _so.reduce_remaining(order, quantity)
                fee = self.fee_acc.charge(seller, gross)
                self.wallet.credit(seller, gross - fee)
                self.monetary.destroy(fee)
                self.claim_store.add(account_id, item_id, quantity, price, now)
                fills.append(self.fill_ledger.record(
                    item_id, account_id, seller, SOURCE_PLAYER_ORDER, order_id,
                    quantity, price, gross, fee, SIDE_BUY, now))
            self.history.record_trade(item_id, price, quantity, SIDE_BUY, now)

        self._snapshot_history(item_id, now)
        self.market.bump_version()
        return fills

    # ------------------------------------------------------------------
    # 领取
    # ------------------------------------------------------------------
    def claim(self, account_id, claim_id, now=None):
        """领取成交物品到背包；背包满则抛 ItemNotReceivable，物品留在 Claim。"""
        self._check_account(account_id)
        claim = self.claim_store.require(claim_id)
        if claim["player"] != account_id:
            raise ClaimNotFound("claim %r does not belong to %r" % (claim_id, account_id))
        if claim["status"] != CLAIM_PENDING:
            raise ClaimNotFound("claim %r already claimed" % claim_id)
        self.inventory.add_item(account_id, claim["item_id"], claim["quantity"])
        self.claim_store.mark_claimed(claim_id)
        return claim

    # ------------------------------------------------------------------
    # 保供补货
    # ------------------------------------------------------------------
    def restock(self, now=None):
        """基础保供慢速补货：仅 8 种，S < 30%T 时补 1%T，封顶 T。"""
        now = self._now(now)
        restocked = []
        for item_id in self._registry.supply_ids():
            t = self._registry.target_stock(item_id)
            s = self.market.system_stock(item_id)
            threshold = t * _cfg.SUPPLY_RESTOCK_THRESHOLD_PCT // 100
            if s < threshold:
                add = t // 100
                if add < 1:
                    add = 1
                if s + add > t:
                    add = t - s
                self.market.increase_stock(item_id, add)
                restocked.append((item_id, add))
        if restocked:
            self.market.bump_version()
        return restocked

    # ------------------------------------------------------------------
    # 内部：行情快照
    # ------------------------------------------------------------------
    def _snapshot_history(self, item_id, now):
        self.history.set_snapshot(
            item_id,
            self.market.system_theoretical(item_id),
            self.market.mid_price(item_id),
            self.market.system_stock(item_id),
            self.escrow.total_stock(item_id),
            now)
