#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/24 4:49 下午
# @Author  : Hanley
# @File    : wrapper.py
# @Desc    :
import asyncio
import traceback
from copy import deepcopy
from functools import wraps

from jsonschema import Draft4Validator, ValidationError

from config.constant import Constant
from config.return_code import CODE_0, CODE_101, CODE_1, CODE_500
from core.base import ReturnData, BaseRequestHandler
from libs.bolts import str_now
from libs.log import logging


def parameter_valid(schema, parameter):
    try:
        Draft4Validator(schema=schema).validate(parameter)
        return True
    except ValidationError as e:
        logging.warning("{}: {}".format(CODE_101, e.message))
        return False


def send_message(request: BaseRequestHandler, response: ReturnData.dict_body):
    env = request.serve_ctx.config.get("ENV", "").upper()
    try:
        if env == "PRO" and request.path not in Constant.NO_RECORD_URI:
            _return_data = deepcopy(response)
            if isinstance(_return_data, dict):
                _return_data.pop("data", "")
            else:
                _return_data = dict(code=CODE_1, data=_return_data, msg="", trace="")
            message_info, log_info = {}, {}
            collection = str_now("%Y%m")
            log_info["channel"] = "diablo"
            log_info["headers"] = dict(request.headers.items())
            log_info["routing"] = request.parameter.get("routing", "")
            log_info["method"] = request.method
            log_info["path"] = request.path
            log_info["parameter"] = request.parameter
            log_info["start_time"] = request.ctx.request_time
            log_info["return_data"] = _return_data
            log_info["cost_time"] = round(request.cost_time * 1000, 3)
            log_info["trace"] = _return_data["trace"]
            log_info['request_id'] = request.ctx.request_id
            message_info["collection"] = collection
            message_info["log_info"] = log_info
    except Exception as e:
        request.log.error(traceback.format_exc())
        request.log.error(f"send log to kafka error, {e}")


async def group_check(request: BaseRequestHandler, schema, login_check):
    # 参数校验
    if schema:
        if not parameter_valid(schema, request.parameter):
            return CODE_101
    return CODE_0


def uri_check(schema=None, login_check: bool = False):
    def validate(func):
        @wraps(func)
        async def async_wrapper(self, request: BaseRequestHandler, *args, **kwargs) -> ReturnData:
            try:
                check_code = await group_check(request, schema, login_check)
                if check_code == CODE_0:
                    if not asyncio.iscoroutinefunction(func):
                        return_data = func(self, request, *args, **kwargs)
                    else:
                        return_data = await func(self, request, *args, **kwargs)
                else:
                    return_data = ReturnData(check_code)
            except Exception as e:
                logging.error(e)
                logging.error(traceback.format_exc())
                return_data = ReturnData(CODE_500, trace=traceback.format_exc())
            # send_message(request, return_data.dict_body)

            if request.serve_ctx.config.get("ENV", "").upper() == "PRO":
                return_data.trace = None
            return return_data

        return async_wrapper

    return validate
