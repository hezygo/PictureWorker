#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File        :utils_retry.py
@Desc        :重试工具的装饰器
@Date        :2022-02-24 15:44
@Author      :
"""


from functools import wraps
from random import random
from time import sleep

"""
    有一个通过网络获取数据的函数（可能会因为网络原因出现异常），
写一个装饰器让这个函数在出现指定异常时可以重试指定的次数，并在
每次重试之前随机延迟一段时间，最长延迟时间可以通过参数进行控制。
"""


def retry(*, retry_times=3, max_wait_secs=5, errors=(Exception, )):

    def decorate(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(retry_times):
                try:
                    return func(*args, **kwargs)
                except errors:
                    sleep(random() * max_wait_secs)
            return None

        return wrapper

    return decorate


class Retry(object):

    def __init__(self, *, retry_times=3, max_wait_secs=5, errors=(Exception, )):
        self.retry_times = retry_times
        self.max_wait_secs = max_wait_secs
        self.errors = errors

    def __call__(self, func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(self.retry_times):
                try:
                    return func(*args, **kwargs)
                except self.errors:
                    sleep(random() * self.max_wait_secs)
            return None

        return wrapper



@retry(retry_times=5)
def test_func():
    print(1)

@Retry(retry_times=4)
def test_obj():
    print('obj')