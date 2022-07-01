#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/27 11:42 上午
# @Author  : Hanley
# @File    : commodity.py
# @Desc    :
import asyncio
import time
import traceback
from asyncio.exceptions import CancelledError

import ujson
from libs.log import logging
from pymongo import ReturnDocument

from config.constant import RedisKey
from core.base import BaseRequestHandler


class Demo:

    def __init__(self, request: BaseRequestHandler):
        self.request = request

    async def multi_call(self):
        result_dict, _code_list = {}, []
        result = {"code": 0, "data": {}, "msg": "成功返回"}
        detect_list = [self.mysql_demo, self.redis_demo, self.mongo_demo]
        for detect in detect_list:
            _result = await self.try_detect(detect)
            result_dict.setdefault(detect.__name__, _result)
            _code_list.append(_result.get("flag", 0))
        _code = 1 if all(_code_list) else 0
        result["code"] = _code
        result["data"] = result_dict
        return result

    async def try_detect(self, function):
        now = time.strftime("%Y-%m-%d %X")
        result = {
            "detection_time": now,
            "detection_type": function.__name__.split("_")[0],
            "flag": 0,
            "trace": ""
        }
        try:
            if asyncio.iscoroutinefunction(function):
                result["flag"] = await function()
            else:
                result["flag"] = function()
        except Exception as e:
            result["trace"] = e.__doc__
            logging.error(f"database error, {e}")
            logging.error(traceback.format_exc())
        return result

    async def mysql_demo(self):
        # mysql demo
        sql = f"SELECT * FROM `config` WHERE `id` = 2"
        mysql_result = await self.request.mysql.execute_sql(sql)
        mysql_result = [item for item in mysql_result]

        mysql_flag = 1 if mysql_result else 0
        return mysql_flag

    async def mongo_demo(self):
        # mongo demo
        mongo_result = await self.request.mongo.diablo.inquiry_order.find_one({})

        mongo_flag = 1 if mongo_result else 0
        return mongo_flag

    async def redis_demo(self):
        # redis demo
        redis_result = await self.request.redis.set('HeartbeatDetect:redis', 1)
        redis_flag = 1 if redis_result else 0
        return redis_flag

    async def fetch_demo(self):
        # fetch demo
        fetch_result = await self.request.client.fetch_json(
            method="GET",
            url="https://api.bilibili.com/x/web-frontend/data/collector")
        fetch_flag = 1 if fetch_result else 0
        return fetch_flag
