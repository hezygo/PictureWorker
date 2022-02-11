#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File        :getWeChatPic.py
@Desc        :server
@Date        :2022-02-10 15:06
@Author      :LPigH
"""


from datetime import datetime, date
from doctest import UnexpectedException
from hashlib import md5
from time import sleep
import traceback
import requests
from bs4 import BeautifulSoup
import os
from loguru import logger
from random import random
from concurrent.futures import ThreadPoolExecutor, as_completed

TMP = "./tmp"
PICEXG = ".jpeg"
LOGDIR = 'log'
PICDIR = 'pic'


def InitLogger():
    f_locate = f'{os.path.join(TMP, LOGDIR)}/{date.isoformat(datetime.now())}.log'
    if not os.path.exists(f_locate):
        logger.add(
            f_locate,
            rotation="00:00",
            encoding="utf-8",
            retention="90 days"
        )


class InitRequest:

    def __init__(self) -> None:
        self.logger = logger

    def _respone(self, url, beText=True, slp=1):
        sleep(slp)
        resp = requests.get(url)
        if beText:
            return resp.text, url
        return resp, url

    def get_pic(self, text: str = None):
        if text:
            soup = BeautifulSoup(text, 'lxml')
        else:
            self.logger.warning(traceback.format_exc())
            raise UnexpectedException(
                "数据不存在", ValueError, traceback.format_exc())
        res = soup.find_all(attrs={"data-type": "jpeg"})
        for pic_item in res:
            if 'data-src' in pic_item.attrs:
                yield pic_item.attrs['data-src']

    @staticmethod
    def md5_(text):
        name_ = md5(text)
        name = name_.hexdigest()
        return '{}/{}/{}{}'.format(TMP, PICDIR, name, PICEXG), name

    def _save(self, content):
        path, name = self.md5_(content)
        if not os.path.exists(path):
            with open(path, "wb") as fw:
                fw.write(content)
        return name

    def _process_down(self, gp, workers: int = 10):
        rep = dict()
        futures = dict()

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(self._respone, src, False, random()): src for src in gp
            }
            while futures:
                for future in as_completed(futures):
                    try:
                        result, url = future.result()
                    except Exception as err:
                        self.logger.warning(err)
                    else:
                        file_pname = self._save(result.content)
                        rep[file_pname] = url
                        del futures[future]
        return rep


if __name__ == "__main__":
    ir = InitRequest()
    # ir._process_down(ir.get_pic())
