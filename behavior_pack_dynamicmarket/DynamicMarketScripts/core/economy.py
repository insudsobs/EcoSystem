# -*- coding: utf-8 -*-
"""经济系统聚合根：组装全部核心组件，提供交易入口与序列化。

纯 Python，零网易依赖。测试用默认构造即可；Runtime 层用 snapshot/restore
配合网易 extraData 持久化。
"""
import config as _cfg
from errors import InvariantViolation
from ids import IdGenerator
from clock import ManualClock
from price_engine import PriceEngine
from monetary import MoneySupply
from wallet import MemoryWallet
from inventory import MemoryInventory
from market import Market
from orderbook import OrderBook
from escrow import Escrow
from fill_store import MemoryFillStore
from claim_store import ClaimStore
from fee import FeeAccumulator
from history import History
from quote_store import QuoteStore
from trade_service import TradeService
import item_registry

# 国库账户（初始货币注入/后续国家税收用）
TREASURY_ACCOUNT = "__treasury__"


class Economy(object):
    def __init__(self, clock=None, price_engine=None, initial_money=0):
        self.clock = clock if clock is not None else ManualClock(0)
        self.price_engine = price_engine if price_engine is not None \
            else PriceEngine(_cfg.SPREAD_BPS, _cfg.DEFAULT_MAX_STOCK_FACTOR)

        self.order_ids = IdGenerator(1)
        self.quote_ids = IdGenerator(1)
        self.fill_ids = IdGenerator(1)
        self.claim_ids = IdGenerator(1)

        self.registry = item_registry.build_default_registry(
            _cfg.DEFAULT_MAX_STOCK_FACTOR)
        self.market = Market(self.price_engine, self.registry)
        self.market.reset_all_to_target()

        self.monetary = MoneySupply(initial=initial_money)
        self.wallet = MemoryWallet()
        if initial_money > 0:
            # 初始货币注入国库账户，保持 wallet 总余额 == MoneySupply.total()
            self.wallet.credit(TREASURY_ACCOUNT, initial_money)
        self.inventory = MemoryInventory()
        self.orderbook = OrderBook()
        self.escrow = Escrow()
        self.fee_acc = FeeAccumulator(_cfg.FEE_BPS)
        self.fill_ledger = MemoryFillStore(self.fill_ids)
        self.claim_store = ClaimStore(self.claim_ids)
        self.history = History(_cfg.HISTORY_PERIOD_SECONDS)
        self.quote_store = QuoteStore()

        self.trade = TradeService(
            self.market, self.orderbook, self.escrow, self.claim_store,
            self.monetary, self.wallet, self.inventory, self.fee_acc,
            self.fill_ledger, self.history, self.quote_store,
            self.order_ids, self.quote_ids, self.clock, self.price_engine,
            self.registry)

    # ---- 便捷委托 ----
    def quote_item(self, item_id, quantity, side, now=None):
        return self.trade.quote_item(item_id, quantity, side, now)

    def place_sell_order(self, account_id, item_id, amount, unit_price,
                         expires_at=0, now=None):
        return self.trade.place_sell_order(account_id, item_id, amount, unit_price,
                                           expires_at, now)

    def cancel_order(self, account_id, order_id, now=None):
        return self.trade.cancel_order(account_id, order_id, now)

    def sell_to_system(self, account_id, item_id, quantity, now=None):
        return self.trade.sell_to_system(account_id, item_id, quantity, now)

    def buy(self, account_id, item_id, quantity, quote_id, now=None):
        return self.trade.buy(account_id, item_id, quantity, quote_id, now)

    def expire_orders(self, now=None):
        return self.trade.expire_orders(now)

    def claim(self, account_id, claim_id, now=None):
        return self.trade.claim(account_id, claim_id, now)

    def restock(self, now=None):
        return self.trade.restock(now)

    # ---- 不变量 ----
    def assert_invariants(self):
        """校验货币守恒与库存非负。"""
        self.monetary.assert_invariant()
        wallet_total = self.wallet.total_balance()
        money_total = self.monetary.total()
        if wallet_total != money_total:
            raise InvariantViolation(
                "wallet total %r != money supply %r" % (wallet_total, money_total))
        for item_id, s in self.market.snapshot().items():
            if s < 0:
                raise InvariantViolation("negative system stock for %r: %r"
                                         % (item_id, s))

    # ---- 序列化 ----
    def snapshot(self):
        """返回 MarketState（纯 dict）。quotes 为 EPHEMERAL，不保存。"""
        stock = {}
        for item_id, s in self.market.snapshot().items():
            stock[item_id] = {"stock": s, "configVersion": _cfg.CONFIG_VERSION}
        return {
            "configVersion": _cfg.CONFIG_VERSION,
            "money": {
                "supply": self.monetary.snapshot(),
                "wallets": self.wallet.snapshot(),
            },
            "market": {
                "version": self.market.version(),
                "stock": stock,
            },
            "orders": self.orderbook.snapshot(),
            "escrow": self.escrow.snapshot(),
            "claims": self.claim_store.snapshot(),
            "fees": self.fee_acc.snapshot(),
            "fills": self.fill_ledger.snapshot(),
            "history": self.history.snapshot(),
            "inventory": self.inventory.snapshot(),
            "nextIds": {
                "order": self.order_ids.current(),
                "quote": self.quote_ids.current(),
                "fill": self.fill_ids.current(),
                "claim": self.claim_ids.current(),
            },
        }

    def restore(self, data):
        """从 MarketState 恢复全部状态。

        配置变化只改规则参数，不重置真实库存；仅对配置中新增的商品
        初始化到 target_stock。
        """
        money = data["money"]
        self.monetary = MoneySupply.from_snapshot(money["supply"])
        self.wallet = MemoryWallet.from_snapshot(money["wallets"])

        market = data["market"]
        stock = {}
        for item_id, entry in market["stock"].items():
            # entry 为 {"stock": int, "configVersion": int} 或兼容旧格式 int
            if isinstance(entry, dict):
                stock[item_id] = entry["stock"]
            else:
                stock[item_id] = entry
        # 新增商品（旧状态无库存记录）才初始化
        for item_id in self.registry.all_ids():
            if item_id not in stock:
                stock[item_id] = self.registry.target_stock(item_id)
        self.market = Market.from_snapshot(stock, self.price_engine,
                                           self.registry, market["version"])

        self.orderbook = OrderBook.from_snapshot(data["orders"])
        self.escrow = Escrow.from_snapshot(data["escrow"])
        self.claim_store = ClaimStore.from_snapshot(data["claims"], self.claim_ids)
        self.fill_ledger = MemoryFillStore.from_snapshot(data["fills"], self.fill_ids)
        self.fee_acc = FeeAccumulator.from_snapshot(data["fees"], _cfg.FEE_BPS)
        # quotes 为 EPHEMERAL，不恢复，重置
        self.quote_store = QuoteStore()
        # history 为 DERIVED：缺省时从 fills 重建
        history_data = data.get("history")
        if history_data:
            self.history = History.from_snapshot(history_data,
                                                 _cfg.HISTORY_PERIOD_SECONDS)
        else:
            self.history = History(_cfg.HISTORY_PERIOD_SECONDS)
            self.history.rebuild_from(self.fill_ledger.all())
        self.inventory = MemoryInventory.from_snapshot(data["inventory"])

        next_ids = data["nextIds"]
        self.order_ids.ensure_above(next_ids["order"] - 1)
        self.quote_ids.ensure_above(next_ids["quote"] - 1)
        self.fill_ids.ensure_above(next_ids["fill"] - 1)
        self.claim_ids.ensure_above(next_ids["claim"] - 1)

        self.trade = TradeService(
            self.market, self.orderbook, self.escrow, self.claim_store,
            self.monetary, self.wallet, self.inventory, self.fee_acc,
            self.fill_ledger, self.history, self.quote_store,
            self.order_ids, self.quote_ids, self.clock, self.price_engine,
            self.registry)

    # ---- 存储桥接 ----
    def save_to(self, storage):
        """序列化并写入 storage。"""
        import state_codec
        storage.save(state_codec.encode(self.snapshot(), saved_at=self.clock.now()))

    def load_from(self, storage):
        """从 storage 读取并恢复。返回是否成功加载。"""
        import state_codec
        blob = storage.load()
        if blob is None:
            return False
        data = state_codec.decode(blob)
        self.restore(data)
        return True
