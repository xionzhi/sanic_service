#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/27 5:05 下午
# @Author  : Hanley
# @File    : commodity.py
# @Desc    :

from sanic.views import HTTPMethodView

from apps.admin.controller.commodity import CommodityController
from core.base import BaseRequestHandler, ReturnData, SuccessData
from core.wrapper import uri_check


class CheckOutCommodity(HTTPMethodView):

    @uri_check()
    async def get(self, request: BaseRequestHandler) -> ReturnData:
        commodities = await CommodityController(request).commodity_list(
            to_group='admin')
        return SuccessData(data={'commodities': commodities})

    @uri_check()
    async def put(self, request: BaseRequestHandler):
        commodity_id = request.parameter['commodity_id']
        content = request.parameter['content']
        await CommodityController(request).commodity_modify(
            commodity_id, content=content)
        return SuccessData()
