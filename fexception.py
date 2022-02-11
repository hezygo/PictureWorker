#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File        :fexception.py
@Desc        :http execption handle
@Date        :2022-02-11 12:27
@Author      :LPigH
"""

from fastapi import FastAPI
from loguru import logger
from json import JSONDecodeError

from fastapi import status
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError



async def request_validation_exception_handler(request, exc):
    data = {
        'msg': '参数异常',
        'code': 10422,
        'errorCode': status.HTTP_422_UNPROCESSABLE_ENTITY,
    }
    logger.exception(exc)
    return JSONResponse(data, status_code=status.HTTP_200_OK)


async def value_exception_handle(request, exc):
    data = {
        'msg': '字段异常',
        'code': 10101,
        'errorCode': status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    logger.exception(exc)
    return JSONResponse(data, status_code=status.HTTP_200_OK)


async def file_not_found_exception_handle(request, exc):
    data = {
        'msg': '找不到文件',
        'code': 10404,
        'errorCode': status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    logger.exception(exc)
    return JSONResponse(data, status_code=status.HTTP_200_OK)


async def base_exception_handle(request, exc):
    data = {
        'msg': '系统错误',
        'code': 10500,
        'errorCode': status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    logger.exception(exc)
    return JSONResponse(data, status_code=status.HTTP_200_OK)


async def validation_exception_handler(request, exc):
    data = {
        'msg': '模型校验异常',
        'code': 10102,
        'errorCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    logger.exception(exc)
    return JSONResponse(data, status_code=status.HTTP_200_OK)


async def attribute_exception_handler(request, exc):
    data = {
        'msg': '对象属性异常',
        'code': 10103,
        'errorCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    logger.exception(exc)
    return JSONResponse(data, status_code=status.HTTP_200_OK)


async def json_decode_exception_handler(request, exc):
    data = {
        'msg': 'JSON格式异常',
        'code': 10104,
        'errorCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    logger.exception(exc)
    return JSONResponse(data, status_code=status.HTTP_200_OK)


def exception_init(app: FastAPI):
    app.add_exception_handler(RequestValidationError,
                              request_validation_exception_handler)
    app.add_exception_handler(ValueError, value_exception_handle)
    app.add_exception_handler(
        FileNotFoundError, file_not_found_exception_handle)
    app.add_exception_handler(Exception, base_exception_handle)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(AttributeError, attribute_exception_handler)
    app.add_exception_handler(JSONDecodeError, json_decode_exception_handler)
