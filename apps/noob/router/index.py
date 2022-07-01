#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 4:51 下午
# @Author  : Hanley
# @File    : server.py
# @Desc    :
from typing import Union

from sanic import Blueprint, HTTPResponse

from apps.noob.views import index
from core.base import BaseRequestHandler, ReturnData

index_bp = Blueprint(
    name="index",
)


@index_bp.middleware("request")
async def pre_request(request: BaseRequestHandler):
    """请求响应函数前"""
    # logging.debug(f"parameters: {request.parameter}")
    pass


@index_bp.middleware("response")
async def post_response(request: BaseRequestHandler, response: Union[HTTPResponse, ReturnData]):
    """请求响应函数后"""
    pass


index_bp.add_route(handler=index.Index.as_view(), uri="/heartbeat/detect")
