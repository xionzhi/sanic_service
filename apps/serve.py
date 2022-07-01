# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : serve.py
# Time       ：30/6/2022 3:59 PM
# Author     ：xionzhi
# version    ：python 3.9
# Description：
"""

import os
from typing import Union

from sanic import Blueprint, HTTPResponse, json, Sanic

from apps.admin.router import admin_bp
from core.base import BaseErrorHandler, ReturnData, ServeConfig, ServeContext
from core.base import BaseRequestHandler
from libs.log import logging


def get_env() -> str:
    """获取当前环境"""
    env = os.environ.get('PROJECT_ENV', 'dev')
    if env not in ('pro', 'dev'):
        return 'dev'

    return env


app = Sanic(
    "Catarc-Serve",
    error_handler=BaseErrorHandler(),
    request_class=BaseRequestHandler,
    config=ServeConfig(env=get_env()),
)


@app.listener('main_process_start')
async def main_process_start(app: Sanic, listener):
    """主进程启动前"""
    logging.info(f'start {app.name} successfully')
    routes_all = app.router.routes_all
    for r in routes_all.values():
        logging.debug(f'r: {r.path} {r.name} {r.methods} {r.regex}')
    pass


@app.listener('main_process_stop')
async def main_process_stop(app: Sanic, listener):
    """主进程停止后"""
    pass


@app.listener('before_server_start')
async def before_server_start(app: Sanic, loop):
    """子进程启动前"""
    serve_context = ServeContext(config=app.config, loop=loop)
    await serve_context.init_connection()
    app.ctx = serve_context
    pass


@app.listener('after_server_start')
async def after_server_start(app: Sanic, loop):
    """子进程启动后"""
    pass


@app.listener('before_server_stop')
async def before_server_stop(app: Sanic, loop):
    """子进程停止前"""
    await app.ctx.close_connection()
    pass


@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    """子进程停止后"""
    pass


@app.on_request
async def pre_request(request: BaseRequestHandler):
    """请求响应函数前"""
    logging.debug(
        f"summary_log: {request.method}:{request.path}:{request.parameter}\n")
    pass


@app.on_response
async def post_request(request: BaseRequestHandler, response: Union[
    HTTPResponse, ReturnData]) -> HTTPResponse:
    """请求响应函数后"""
    # logging.debug(f"{request.method} {request.path} {response.body}")
    if isinstance(response, ReturnData):
        duration = round(request.cost_time * 1000, 3)

        logging.debug(
            f'summary_log: {request.method}:{request.path}:'
            f'{response.dict_body["code"]}:{duration}ms\n')
        if duration >= 400:
            logging.error(
                f'duration: {request.method}:{request.path}:{duration}ms')
        return json(response.dict_body)

    return response


def create_app() -> Sanic:
    """创建app"""
    return register_bp(app=app)


def register_bp(app: Sanic):
    """注册蓝图到app"""
    v1_bps = Blueprint.group(
        admin_bp,
        url_prefix="/api",
        version=1)

    app.blueprint(v1_bps)
    return app
