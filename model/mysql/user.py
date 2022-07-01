#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/6/30/4:56 PM
# @Author  : Hanley
# @File    : user.py
# @Desc    :
from datetime import datetime

from peewee import AutoField, CharField, DateTimeField, FloatField, \
    IntegerField, SmallIntegerField

from model.mysql.base import BaseModel, JsonField

__all__ = [
    'AdminUser',
    'MerchantOrder',
]


class AdminUser(BaseModel):
    id = AutoField()
    username = CharField(max_length=16, unique=True, verbose_name='登录账号')
    password = CharField(max_length=64, help_text='密码')
    register_time = DateTimeField(default=datetime.now,
                                  verbose_name='注册时间')
    nickname = CharField(max_length=32, default='', verbose_name='昵称')
    avatar = CharField(max_length=128, default='', verbose_name='头像')
    status = SmallIntegerField(default=1, verbose_name='启用状态')

    class Meta:
        table_name = 'admin_user'
        indexes = (
            (('username', 'status'), True),
        )


class MerchantOrder(BaseModel):
    id = AutoField()
    order_id = CharField(unique=True, max_length=32, verbose_name='订单ID')
    merchant_id = IntegerField(index=True, verbose_name='商户ID')
    commodity_ids = CharField(max_length=32, index=True, verbose_name='套餐ID')
    pay_status = SmallIntegerField(default=1, verbose_name='支付状态')
    pay_amount = FloatField(default=0, verbose_name='支付金额')
    create_time = DateTimeField(default=datetime.now,
                                verbose_name='创建时间')
    pay_time = DateTimeField(null=True, verbose_name='支付时间')
    extra = JsonField(default='', verbose_name='额外信息')

    class Meta:
        table_name = 'merchant_order'
