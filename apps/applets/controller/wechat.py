# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : wechat.py
# Time       ：30/6/2022 5:26 PM
# Author     ：xionzhi
# version    ：python 3.9
# Description：
"""
import base64
import typing

from Crypto.Cipher import AES
from urllib.parse import urlencode, urljoin

import ujson

from config.constant import RedisKey
from libs.log import logging


class AppletController:
    def __init__(self, request):
        self.request = request

    @property
    def applet_conf(self):
        return self.request.app.config["WECHAT"]["APPLET"]

    async def cache_access_token(self) -> str:
        """
        access_token 缓存
        :return:
        """
        app_id = self.applet_conf.get('APPID')
        key = RedisKey.CATARC_ACCESS_TOKEN.format(f'{app_id}')
        access_token = await self.request.redis.get(key)

        if access_token:
            return access_token

        # 不存在access_token
        access_token_info = await self.get_access_token()
        if not access_token_info or not access_token_info.get('access_token'):
            logging.info(f'consult 获取access_token失败: {access_token_info}')
            return ''

        access_token = access_token_info['access_token']
        # set redis access_token
        await self.request.redis.set(key, access_token, expire=RedisKey.minute * 100)

        return access_token

    async def get_access_token(self) -> typing.Dict:
        """
        access_token 刷新
        :return:
        """
        params = {
            'appid': self.applet_conf.get('APPID'),
            'secret': self.applet_conf.get('SECRET'),
            'grant_type': 'client_credential'}
        url = f'https://api.weixin.qq.com/cgi-bin/token?{urlencode(params)}'
        resp = await self.request.client.fetch_json(method='GET', url=url)

        return resp

    async def get_wechat_session_data(self, wechat_code: str) -> typing.Dict:
        """
        解析小程序用户信息
        :param wechat_code:
        :return:
        """
        params = {
            'appid': self.applet_conf.get('APPID'),
            'secret': self.applet_conf.get('SECRET'),
            'js_code': wechat_code,
            'grant_type': 'authorization_code'}
        url = f'https://api.weixin.qq.com/sns/jscode2session?{urlencode(params)}'
        resp = await self.request.client.fetch_json(method='GET', url=url)

        return resp


class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)
        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)
        decrypted = ujson.loads(self._unpad(cipher.decrypt(encryptedData)))
        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')
        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]