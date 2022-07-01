# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : applet.py
# Time       ：1/7/2022 9:54 AM
# Author     ：xionzhi
# version    ：python 3.9
# Description：
"""

from datetime import datetime

from peewee import AutoField, CharField, DateTimeField, FloatField, \
    IntegerField, SmallIntegerField

from model.mysql.base import BaseModel, JsonField


class AppletUser(BaseModel):
    """微信用户表"""
    id = AutoField()
    open_id = CharField(max_length=64, unique=True, verbose_name='微信标示')
    avatar = CharField(max_length=256, verbose_name='微信头像')
    wechat_nick = CharField(max_length=256, unique=True, verbose_name='微信昵称')
    province = CharField(max_length=64, verbose_name='微信省份')
    city = CharField(max_length=64, verbose_name='微信城市')
    address = CharField(max_length=64, verbose_name='地址')
    company = CharField(max_length=64, verbose_name='公司')
    username = CharField(max_length=64, verbose_name='用户名')
    phone = CharField(max_length=64, verbose_name='手机号')
    password = CharField(max_length=64, help_text='密码')

    register_time = DateTimeField(default=datetime.now, verbose_name='注册时间')
    nickname = CharField(max_length=32, default='', verbose_name='昵称')
    status = SmallIntegerField(default=1, verbose_name='启用状态')

    class Meta:
        table_name = 'applet_user'
        indexes = (
            (('open_id', 'status'), True),
        )


class AppletFollow(BaseModel):
    """微信用户关注"""
    id = AutoField()
    open_id = CharField(max_length=64, verbose_name='微信用户id')
    merchant_id = IntegerField(index=True, verbose_name='关注商户id')

    following_time = DateTimeField(default=datetime.now, verbose_name='关注时间')
    status = SmallIntegerField(default=1, verbose_name='启用状态')

    class Meta:
        table_name = 'applet_follow'
        indexes = (
            (('open_id', 'merchant_id'), True),
        )


class AppletIntentBuy(BaseModel):
    """微信用户意向购买商品"""
    id = AutoField()
    intent_time = DateTimeField(default=datetime.now, verbose_name='意向购买时间')
    intent_amount = IntegerField(verbose_name='意向购买数量')

    # 零件信息
    commodity_id = IntegerField(index=True, verbose_name='商品id')
    # 买家id
    open_id = CharField(max_length=64, index=True, verbose_name='微信用户id')
    # 商户信息
    merchant_id = IntegerField(index=True, verbose_name='关注商户id')

    applet_read = SmallIntegerField(default=0, verbose_name='小程序新消息')
    merchant_read = SmallIntegerField(default=0, verbose_name='商户新消息')

    update_time = DateTimeField(default=datetime.now, verbose_name='更新时间')
    status = SmallIntegerField(default=1, verbose_name='启用状态')


class AppletIntentBuyMsg(BaseModel):
    """微信用户意向购买留言"""
    id = AutoField()
    intent_id = IntegerField(index=True, verbose_name='意向id')
    open_id = CharField(max_length=64, index=True, verbose_name='微信用户id')
    merchant_id = IntegerField(index=True, verbose_name='商户id')

    msg_type = CharField(max_length=64, verbose_name='消息id')
    msg_content = CharField(max_length=2048, verbose_name='消息内容')

    create_time = DateTimeField(default=datetime.now, verbose_name='更新时间')
    status = SmallIntegerField(default=1, verbose_name='启用状态')
