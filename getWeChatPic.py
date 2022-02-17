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
import re
from loguru import logger
from random import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from requests_html import AsyncHTMLSession
from config import settings
TMP = "./tmp"
LOGDIR = 'log'
PICDIR = 'pic'
PIC_EXTENSION = {'image/jpg': 'jpg', 'image/jpeg': 'jpeg',
                 'image/gif': 'gif', 'image/png': 'png'}
MD_HEAD = '''---
title: {title}
author: {author}
date: '{date}'
---\n'''

EXE_JS = '''
var speed=600;var sleep=function(time){return new Promise(function(resolve,reject){setTimeout(function(){resolve(true)},time)})};var getImgArr=function(){return document.querySelectorAll('img.rich_pages')};var flush=function(){let imgArr=getImgArr();imgArr.forEach(async function(img,index){await sleep(speed*index);img.scrollIntoView()})};var checkRealSrc=function(){let imgArr=getImgArr();let bool=true;imgArr.forEach(function(x){if(x.getAttribute('src').slice(0,4)!='http'){bool=false}});return bool};var waitAllLoading=async function(){let imgArr=getImgArr();flush();await sleep(speed*imgArr.length);if(!checkRealSrc()){waitAllLoading()}else{window.jojoImgAllLoading='Done'}};waitAllLoading();'''


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
        self.find_all = []
        self.pages_title = ''

    def _response(self, url, beText=True, slp=1):
        sleep(slp)
        resp = requests.get(url)
        if beText:
            return resp.text, url
        return resp, url

    async def _web_response(self, url):
        """
        使用浏览器驱动
        return: 只返回html
        """
        self.logger.info(settings.js_driver)
        browser = webdriver.PhantomJS(settings.js_driver)  # js驱动路径
        browser.get(url)
        sleep(3)
        def get_now():
            return datetime.timestamp(datetime.now())
        t_start =get_now()
        with open('/home/cm001/PictureWorker/picture.js','r',encoding='utf-8') as fr:
            js_str  = fr.read()
            browser.execute_script(js_str)
        while 'Not Done' :
            jojo = browser.execute_script('return window.jojoImgAllLoading')
            if jojo:
                break
        t_end = get_now() - t_start
        self.logger.info(f"use time sec {t_end}")
        return browser.page_source

    def _chorme_response(self, url):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.wait import WebDriverWait
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

        driver = webdriver.Chrome(
            chrome_options=chrome_options, executable_path=settings.chorme_driver)
        driver.get(url)
        with open('/home/cm001/PictureWorker/picture.js','r',encoding='utf-8') as fr:
            js_str  = fr.read()
            jojo = driver.execute_script(js_str)
            print(jojo)
        
        WebDriverWait(driver, 5)
        html = driver.page_source
        driver.quit()
        return html

    async def _request_html_response(self, url):
        # 异步加载html
        asession = AsyncHTMLSession()
        r = await asession.get(url)
        await r.html.arender(scrolldown=8, sleep=0.5)
        return r.text

    @staticmethod
    def _check_build(text: str):
        if text:
            return BeautifulSoup(text, 'lxml')
        else:
            raise UnexpectedException(
                "数据不存在", ValueError, traceback.format_exc())

    @staticmethod
    def strip_all(text: str):
        return text.lstrip().rstrip().replace("\n", "")

    @property
    def date_today(self):
        return date.isoformat(datetime.now())

    def get_title(self, text: str = None):
        soup = self._check_build(text)
        # title
        p_title = soup.find(
            attrs={"class": "rich_media_title", "id": "activity-name"})
        self.pages_title = self.strip_all(
            p_title.text) if p_title else f"{self.date_today}"
        # date
        pattern = re.compile(r'document.getElementById\("publish_time"\)')
        script = soup.find("script", text=pattern)
        p_dates = []
        if script:
            time_pattern = "\d{4}-\d{1,2}-\d{1,2}"
            p_dates = re.findall(time_pattern, script.string)
        p_date = p_dates[0] if p_dates else f"{self.date_today}"
        # author
        p_author = soup.find(attrs={"id": "js_name"})
        p_author = self.strip_all(p_author.text)if p_author else "littlepig"
        return MD_HEAD.format(title=self.pages_title, date=p_date, author=p_author)

    def get_pic(self, text: str = None, default_data_fmt='data-src'):
        soup = self._check_build(text)
        for _, typ in PIC_EXTENSION.items():

            res = soup.find_all('img', attrs={
                "data-type": typ
            })
            if res:
                self.find_all.extend(res)
        for pic_item in self.find_all:
            if default_data_fmt in pic_item.attrs:
                yield pic_item.attrs[default_data_fmt]

    def md5_(self, text: bytes, pic_ext: str):
        name_ = md5(text)
        name = name_.hexdigest()
        return '{}/{}/{}/{}{}'.format(TMP, PICDIR, self._set_pdir_evday, name, pic_ext), name

    def _save(self, content: bytes, pic_ext):
        path, name = self.md5_(content, pic_ext)
        if not os.path.exists(path):
            with open(path, "wb") as fw:
                fw.write(content)
        return name

    def _process_down(self, gp, workers: int = 10):
        rep = dict()
        futures = dict()

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(self._response, src, False, random()): src for src in gp
            }
            while futures:
                for future in as_completed(futures):
                    try:
                        result, url = future.result()
                    except Exception as err:
                        self.logger.warning(err)
                    else:
                        ct_type = PIC_EXTENSION.get(
                            result.headers['Content-Type'], None)
                        if ct_type:
                            file_pname = self._save(
                                result.content, f'.{ct_type}')
                            rep[file_pname] = url
                        else:
                            self.logger.warning(
                                f"Unkown Content-Type:{result.headers['Content-Type']}")
                        del futures[future]
        return rep

    @property
    def _set_pdir_evday(self):
        today = date.isoformat(datetime.now())
        f_dir = f'{os.path.join(TMP, PICDIR)}/{today}'
        if not os.path.exists(f_dir):
            os.mkdir(f_dir)
        return today


# if __name__ == "__main__":
    # ir = InitRequest()
    # text, _ = ir._response('https://mp.weixin.qq.com/s/B7o4OmJNZRuXsScX7wCl-A')
    # print(ir.get_title(text))
    # result = ir._process_down(ir.get_pic(text))
    # ir._process_down(ir.get_pic())
