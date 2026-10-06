# -*- coding: utf-8 -*-
"""周期调度器（不 import 网易）。

VERIFIED：OnScriptTickServer 1秒30次 tick（约，非精确）。
UNVERIFIED：真实 Unix 时间源（time 组件返回游戏帧时间）。

因此调度器以 elapsed timestamp 为准，tick 只做触发检查：每 tick_per_check
个 tick 用 Clock.now() 检查一次「now >= next_run」，避免服务器卡顿后把
一小时任务拖成两小时。以后 ServerSystem 的 OnScriptTickServer 只负责喂 tick，
不在回调里堆经济代码。
"""


class Netease2019Scheduler(object):
    def __init__(self, clock, tick_per_check=30):
        self._clock = clock
        self._tick_per_check = tick_per_check
        self._tick = 0
        self._tasks = {}   # name -> {"interval", "next_run", "callback"}

    def register(self, name, interval_seconds, callback):
        self._tasks[name] = {
            "interval": interval_seconds,
            "next_run": None,
            "callback": callback,
        }
        return name

    def every_second(self, name, callback):
        return self.register(name, 1, callback)

    def every_minute(self, name, callback):
        return self.register(name, 60, callback)

    def every_5min(self, name, callback):
        return self.register(name, 300, callback)

    def every_hour(self, name, callback):
        return self.register(name, 3600, callback)

    def unregister(self, name):
        self._tasks.pop(name, None)

    def tick(self):
        """每 OnScriptTickServer 调用一次。每 tick_per_check 次做一次检查。"""
        self._tick += 1
        if self._tick >= self._tick_per_check:
            self._tick = 0
            self.check(self._clock.now())

    def check(self, now):
        """用外部时间检查并执行到期任务。

        以 elapsed timestamp 为准：卡顿后长时间不调用，到期任务只执行一次，
        next_run 按 now + interval 推进，不会累积补偿多次。
        """
        for task in self._tasks.values():
            if task["next_run"] is None:
                task["next_run"] = now + task["interval"]
                continue
            if now >= task["next_run"]:
                task["callback"](now)
                task["next_run"] = now + task["interval"]

    def next_run(self, name):
        task = self._tasks.get(name)
        return task["next_run"] if task else None
