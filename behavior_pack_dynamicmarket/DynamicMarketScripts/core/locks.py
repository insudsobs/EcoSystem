# -*- coding: utf-8 -*-
"""轻量锁/事务边界标记。

网易 Mod 脚本为单线程，此处锁用于防御性重入保护与未来 Runtime 层
事务边界标记，不引入真实并发语义。
"""
from errors import InvariantViolation


class SimpleLock(object):
    """不可重入的简单锁。"""

    def __init__(self):
        self._locked = False

    def acquire(self):
        if self._locked:
            raise InvariantViolation("lock already held (reentrant acquire)")
        self._locked = True

    def release(self):
        self._locked = False

    def locked(self):
        return self._locked

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False
