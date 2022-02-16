#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File        :fRun.py
@Desc        :mian
@Date        :2022-02-11 12:28
@Author      :LPigH
"""

from fastapi import FastAPI
from fastApp import set_app

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from config import settings
fast_app = FastAPI(title=settings.title,version=settings.version)
set_app(fast_app)

origins = ["*"]

fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(fast_app, host=settings.server_host, port=9001)
