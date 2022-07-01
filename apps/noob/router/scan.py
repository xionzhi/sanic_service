#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/27 5:06 下午
# @Author  : Hanley
# @File    : scan.py
# @Desc    :
from typing import Union

from sanic import Blueprint, HTTPResponse

from apps.noob.views import scan
from core.base import BaseRequestHandler, ReturnData

scan_bp = Blueprint(
    name="scan",
)


@scan_bp.middleware("request")
async def pre_request(request: BaseRequestHandler):
    """请求响应函数前"""
    # logging.debug(f"parameters: {request.parameter}")
    pass


@scan_bp.middleware("response")
async def post_response(request: BaseRequestHandler, response: Union[HTTPResponse, ReturnData]):
    """请求响应函数后"""
    pass


scan_bp.add_route(handler=scan.Scan.as_view(), uri="/scan")
