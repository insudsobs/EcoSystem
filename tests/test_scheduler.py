# -*- coding: utf-8 -*-
from scheduler import Netease2019Scheduler
from clock import ManualClock


def test_task_runs_when_due():
    clock = ManualClock(0)
    sched = Netease2019Scheduler(clock, tick_per_check=30)
    calls = []
    sched.every_minute("t", lambda now: calls.append(now))
    sched.check(0)      # 首次设置 next_run = 60
    assert calls == []
    sched.check(59)     # 未到期
    assert calls == []
    sched.check(60)     # 到期
    assert calls == [60]


def test_every_second():
    clock = ManualClock(0)
    sched = Netease2019Scheduler(clock, tick_per_check=30)
    calls = []
    sched.every_second("t", lambda now: calls.append(now))
    sched.check(0)
    sched.check(1)
    assert calls == [1]


def test_tick_drift_no_compensation():
    # 卡顿 2 小时后，到期任务只执行一次，不累积补偿
    clock = ManualClock(0)
    sched = Netease2019Scheduler(clock, tick_per_check=30)
    calls = []
    sched.every_hour("t", lambda now: calls.append(now))
    sched.check(0)       # next_run = 3600
    sched.check(7200)    # 卡顿 2 小时
    assert calls == [7200]      # 只执行一次
    assert sched.next_run("t") == 10800


def test_tick_triggers_check_every_n():
    clock = ManualClock(0)
    sched = Netease2019Scheduler(clock, tick_per_check=3)
    calls = []
    sched.every_second("t", lambda now: calls.append(now))
    sched.tick()
    sched.tick()
    assert calls == []       # 前 2 个 tick 不检查
    sched.tick()
    assert calls == []       # 第 3 个 tick 检查，但 now=0 未到期


def test_unregister():
    clock = ManualClock(0)
    sched = Netease2019Scheduler(clock)
    calls = []
    sched.every_second("t", lambda now: calls.append(now))
    sched.unregister("t")
    sched.check(0)
    sched.check(10)
    assert calls == []
