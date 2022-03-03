# -*- encoding: utf-8 -*-
"""
@File        :exception.py
@Desc        :异常定义
@Date        :2022-03-03 10:41
"""

from typing import Any


class RemoteException(Exception):
    def __init__(self, value: Any):
        self.__value = value

    def __str__(self):
        return self.__value