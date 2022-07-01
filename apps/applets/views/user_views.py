# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : user_views.py
# Time       ：30/6/2022 5:17 PM
# Author     ：xionzhi
# version    ：python 3.9
# Description：
"""

import ujson
from datetime import datetime

from sanic.views import HTTPMethodView

from apps.applets.controller.wechat import AppletController, WXBizDataCrypt
from config.constant import RedisKey
from core.base import BaseRequestHandler, ReturnData
from core.wrapper import uri_check
from libs.bolts import now_str, str_now, str_to_datetime, datetime_now
from libs.log import logging


class AppletCodeToOpenIdView(HTTPMethodView):
    @uri_check()
    async def post(self, request: BaseRequestHandler):
        """
        小程序用户解析 code 解析 openid
        """
        code = request.parameter.get('code')

        applet = AppletController(request)
        wechat_session_data = await applet.get_wechat_session_data(code)
        openid = wechat_session_data.get('openid')

        # 设置用户信息缓存
        await request.redis.set(openid, ujson.dumps(wechat_session_data), expire=RedisKey.minute * 30)

        # 判断用户是否存在
        pass

        return ReturnData(data=dict(exist=True,
                                    openid=openid,
                                    user_id=''))


class AppletDeCodePhoneView(HTTPMethodView):
    @uri_check(login_check=False)
    async def post(self, request: BaseRequestHandler):
        """
        根据小程序发送open 解析用户手机号
        """
        openid = request.headers.get('openid')
        encrypted_data = request.parameter.get('detail', {}).get('encryptedData')
        iv = request.parameter.get('detail', {}).get('iv')

        if None in (openid, encrypted_data, iv):
            return ReturnData(code=0, msg='缺少必要参数')

        session_data = await request.redis.get(openid)
        session_data = ujson.loads(session_data or '{}')
        session_key = session_data.get('session_key')

        if not session_key:
            return ReturnData(code=0, msg='缺少必要参数')

        app_id = request.app.config["WECHAT"]["APPLET"]["APPID"]
        wbd = WXBizDataCrypt(app_id, session_key)
        wechat_data = wbd.decrypt(encrypted_data, iv)

        phone = wechat_data.get('phoneNumber')

        # 手机号查询用户信息
        pass

        return ReturnData(data=dict())
