#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 3:05 下午
# @Author  : Hanley
# @File    : base.py
# @Desc    :
import re
import traceback
from typing import Any, Dict

from aioredis import Redis
from motor.core import AgnosticDatabase
from pymongo import MongoClient
from sanic import Request, Sanic
from sanic.compat import Header
from sanic.config import Config
from sanic.handlers import ErrorHandler
from sanic.models.protocol_types import TransportProtocol

from config.constant import Constant, make_file_path
from config.return_code import CODE_0, CODE_1, ZH_MAP
from libs.bolts import format_decimal, generate_uuid, perf_time, str_now, \
    xml2dict, yaml_config
from libs.log import logging
from utils.dbClient import AsyncMongodb, AsyncPeewee, AsyncPeeweeManager, \
    AsyncRedis, SyncMongodb, SyncRedis
from utils.requestClient import AioClient


class ServeConfig(Config):
    """服务配置"""

    def __init__(self, env='dev', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_config__(env)

    def __init_config__(self, env):
        self.apply(self.parse_config_path(env))

    @staticmethod
    def parse_config_path(env):
        """获取环境配置"""
        config_file = 'pro.yaml' if env == 'pro' else 'dev.yaml'
        config = yaml_config(file_path=make_file_path(config_file))
        return config

    def apply(self, config):
        self.update(self._to_uppercase(config))

    def _to_uppercase(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        reveal: Dict[str, Any] = {}
        for key, value in obj.items():
            upper_key = key.upper()
            if isinstance(value, list):
                reveal[upper_key] = [
                    self._to_uppercase(item) for item in value
                ]
            elif isinstance(value, dict):
                reveal[upper_key] = self._to_uppercase(value)
            else:
                reveal[upper_key] = value
        return reveal


class ServeContext(object):
    """服务上下文"""
    __slots__ = (
        "config",
        "loop",
        "request_client",
        "mongo_client",
        "mysql_client",
        "redis_client",
        "sync_mongo_client",
        "sync_redis_client",
    )

    def __init__(self, config: dict, loop=None):
        self.config = dict(config)
        self.loop = loop

    async def init_connection(self):
        # 请求客户端
        request_client = AioClient()
        await request_client.init_session()
        self.request_client = request_client

        # mongo客户端
        self.mongo_client = AsyncMongodb(self.config['MONGO']).client

        # mysql客户端
        mysql_database = AsyncPeewee.init_db(self.config['MYSQL'])
        self.mysql_client = AsyncPeeweeManager(database=mysql_database,
                                               loop=self.loop)

        # redis客户端
        self.redis_client = await AsyncRedis(self.config['REDIS']).init_db()

        # 同步 mongo 连接
        self.sync_mongo_client = SyncMongodb(self.config['MONGO']).client

        # 同步 redis 连接
        self.sync_redis_client = SyncRedis(self.config['REDIS']).client

    async def close_connection(self):
        await self.request_client.close()
        self.redis_client.close()
        await self.redis_client.wait_closed()
        await self.mysql_client.close()


class BaseErrorHandler(ErrorHandler):
    """接口异常"""

    def default(self, request, exception):
        return super().default(request, exception)


class BaseRequestHandler(Request):
    """接口请求"""

    def __init__(self, url_bytes: bytes, headers: Header, version: str,
                 method: str, transport: TransportProtocol, app: Sanic,
                 head: bytes = b""):
        super(BaseRequestHandler, self).__init__(url_bytes, headers, version,
                                                 method, transport, app, head)
        self.ctx.request_time = str_now()
        self.ctx.start_time = perf_time()
        self.ctx.cost_time = None
        self.ctx.request_id = generate_uuid()

    @property
    def cost_time(self):
        if not self.ctx.cost_time:
            self.ctx.cost_time = perf_time() - self.ctx.start_time
        return self.ctx.cost_time

    @property
    def parameter(self) -> dict:
        if getattr(self.ctx, "parameter", {}):
            return self.ctx.parameter
        content_type = self.content_type
        parameter = dict()
        # 路由参数
        for key in self.args:
            parameter.setdefault(key, self.args.get(key))

        # 表单参数
        form_condition = all([
            any([re.match(Constant.form_data, content_type),
                 re.match(Constant.urlencoded_pattern, content_type)]),
            self.form
        ])
        if form_condition:
            for key in self.form:
                parameter.setdefault(key, self.form.get(key))

        # body参数
        if self.body:
            try:
                if re.match(Constant.json_pattern, content_type):
                    parameter.update(self.json)
                elif re.match(Constant.xml, content_type):
                    parameter.update(xml2dict(self.body.decode()))
                elif re.match(Constant.text, content_type):
                    parameter.update(text=self.body.decode())
                else:
                    logging.warning(f'unknown content type: {content_type}')
            except Exception as e:
                logging.warning(traceback.format_exc())
                logging.warning(e)
        setattr(self.ctx, "parameter", parameter)
        return parameter

    @property
    def log(self):
        return logging

    @property
    def serve_ctx(self) -> ServeContext:
        return self.app.ctx

    @property
    def config(self):
        return self.serve_ctx.config

    @property
    def client(self) -> AioClient:
        return self.serve_ctx.request_client

    @property
    def mongo(self) -> AgnosticDatabase:
        return self.serve_ctx.mongo_client

    @property
    def sync_mongo(self) -> MongoClient:
        return self.serve_ctx.sync_mongo_client

    @property
    def mysql(self) -> AsyncPeeweeManager:
        return self.serve_ctx.mysql_client

    @property
    def redis(self) -> Redis:
        return self.serve_ctx.redis_client

    @property
    def sync_redis(self) -> Redis:
        return self.serve_ctx.sync_redis_client


class ReturnData:
    """接口返回"""
    __slots__ = (
        "_body",
        "code",
        "msg",
        "data",
        "kwargs",
        "trace",
        "request_id",
    )

    def __init__(self, code=CODE_1, data=None, msg=None,
                 decimal=False, trace: str = "", request_id: str = "",
                 **kwargs):
        if data is None:
            data = {}
        self._body = None
        self.code = code
        self.msg = msg if msg is not None else ZH_MAP.get(code, "")
        self.data = format_decimal(data) if decimal else data
        self.kwargs = kwargs
        self.trace = trace
        self.request_id = request_id

    @property
    def dict_body(self) -> Dict:
        if self._body:
            return self._body
        body = dict(
            code=self.code,
            msg=self.msg,
            data=self.data,
            trace=self.trace,
            request_id=self.request_id,
        )
        if self.kwargs:
            body.update(self.kwargs)
        self._body = body
        return self._body


class SuccessData(ReturnData):
    def __init__(self, code=CODE_1, **kwargs):
        super().__init__(code=code, **kwargs)


class FailureData(ReturnData):
    def __init__(self, code=CODE_0, **kwargs):
        super().__init__(code=code, **kwargs)
