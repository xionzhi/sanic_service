#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/27 5:05 下午
# @Author  : Hanley
# @File    : commodity.py
# @Desc    :

from sanic.views import HTTPMethodView

from apps.noob.controller.index import Demo
from core.base import BaseRequestHandler, ReturnData
from core.wrapper import uri_check


class Index(HTTPMethodView):

    @uri_check()
    async def get(self, request: BaseRequestHandler) -> ReturnData:
        data = await Demo(request).multi_call()
        return ReturnData(data=data)

    async def post(self, request: BaseRequestHandler):
        return await self.get(request=request)
