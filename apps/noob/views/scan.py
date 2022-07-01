#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 4:47 下午
# @Author  : Hanley
# @File    : server.py
# @Desc    :
import random

from sanic.views import HTTPMethodView

from core.base import BaseRequestHandler, ReturnData
from core.wrapper import uri_check


class Scan(HTTPMethodView):

    @uri_check()
    async def get(self, request: BaseRequestHandler) -> ReturnData:
        redis = await request.redis.ping()
        mongo = await request.mongo.audi.stdtools_part_num.find_one({}, {'_id': 0, 'pid': 1})

        return ReturnData(data={'redis': redis,
                                'mongo': mongo})

    @uri_check()
    def post(self, request: BaseRequestHandler) -> ReturnData:
        data = 2 << random.randint(1, 10)
        return ReturnData(data=data)
