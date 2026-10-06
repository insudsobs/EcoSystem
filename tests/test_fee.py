# -*- coding: utf-8 -*-
from fee import FeeAccumulator


def test_fee_one_percent():
    assert FeeAccumulator(100).charge("a", 150) == 1
    assert FeeAccumulator(100).charge("a", 250) == 2
    assert FeeAccumulator(100).charge("a", 100) == 1


def test_fee_split_no_escape():
    # 拆单不能逃避手续费：50+50+50 应等于 150 单笔
    single = FeeAccumulator(100)
    single_total = single.charge("a", 150)

    split = FeeAccumulator(100)
    split_total = (split.charge("a", 50) +
                   split.charge("a", 50) +
                   split.charge("a", 50))

    assert single_total == split_total == 1


def test_net():
    f = FeeAccumulator(100)
    assert f.net("a", 150) == 149


def test_remainder_per_seller():
    # 余数按 seller 独立累积
    f = FeeAccumulator(100)
    f.charge("a", 50)  # 余数 5000
    f.charge("b", 50)  # 余数 5000，独立
    assert f.remainder("a") == 5000
    assert f.remainder("b") == 5000
