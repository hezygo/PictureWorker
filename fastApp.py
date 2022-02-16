#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File        :fastApp.py
@Desc        :api
@Date        :2022-02-11 12:27
@Author      :LPigH
"""


from doctest import UnexpectedException
from hashlib import md5
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Field

from getWeChatPic import InitRequest, InitLogger
from fastapi import APIRouter, Query
from fException import exception_init


class BaseResponse(BaseModel):
    code: int = Field(200, description='状态码')
    msg: str = Field('', description='返回信息')


class PicResponse(BaseResponse):
    data: dict = Field({}, description='路径')


app = APIRouter(
    prefix="/WeChatPic",
    tags=["WeChat"]
)


@app.get('/getPic',
         response_model=PicResponse,
         description='获取WeChat图片或者链接',
         name='获取WeChat图片'
         )
async def get_general_train_task(
        WcPageUrl: str = Query('', description='微信公众号文章链接'),
        IsWcPicDown: bool = Query(False, description='是否下载图片')
):
    ir = InitRequest()
    if WcPageUrl:
        text, _ = ir._respone(WcPageUrl)
    else:
        text = None
    result = dict()
    if IsWcPicDown:
        result = ir._process_down(ir.get_pic(text))
    else:
        gp = ir.get_pic(text)
        result = { util_md5(item): item for item in gp}
    return PicResponse(msg="成功", data=result)

def util_md5(text):
    pre =  md5(bytes(text,'utf-8'))
    return pre.hexdigest()

def set_app(application: FastAPI):
    InitLogger()
    api = APIRouter(prefix="/api")
    api.include_router(app)
    application.include_router(api)
    exception_init(application)
