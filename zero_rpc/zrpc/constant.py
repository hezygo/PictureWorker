# -*- encoding: utf-8 -*-
"""
@File        :constant.py
@Desc        :常量
@Date        :2022-03-03 10:18
@Author      :
"""

from datetime import timedelta

KEEP_ALIVE_TOPIC = "_keep_alive"
KEEP_ALIVE_INTERVAL = timedelta(seconds=3)
KEEP_ALIVE_TOLERANCE = timedelta(seconds=6)

EVENT_TIMER = "eTimer"