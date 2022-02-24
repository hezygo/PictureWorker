#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File        :util_singeton.py
@Desc        :单例装饰器
@Date        :2022-02-24 16:42
@Author      :from GitHub project CUP
"""

import threading


class Singleton(object): 
    """
    Make your class singeton
    example::
        from cup import decorators
        @decorators.Singleton
        class YourClass(object):
            def __init__(self):
            pass
    """
    def __init__(self, cls):
        self.__instance = None
        self.__cls = cls
        self._lock = threading.Lock()

    def __call__(self, *args, **kwargs):
        self._lock.acquire()
        if self.__instance is None:
            self.__instance = self.__cls(*args, **kwargs)
        self._lock.release()
        return self.__instance