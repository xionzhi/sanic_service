#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/6/30/5:13 PM
# @Author  : Hanley
# @File    : common.py
# @Desc    :
from datetime import datetime

from peewee import AutoField, CharField, DateTimeField, SmallIntegerField, \
    TextField

from model.mysql.base import BaseModel

__all__ = [
    'Commodity',
    'PlatformNotification',
    'PlatformInfo',
    'Banner',
]


class Commodity(BaseModel):
    id = AutoField()
    title = CharField(max_length=32, default='', verbose_name='套餐名称')
    content = TextField(default='', verbose_name='套餐内容富文本')
    status = SmallIntegerField(default=1, verbose_name='是否有效')
    create_time = DateTimeField(default=datetime.now,
                                verbose_name='上线时间')
    update_time = DateTimeField(null=True, verbose_name='更新时间')
    to_group = CharField(max_length=16, verbose_name='使用对象')

    class Meta:
        table_name = 'commodity'
        indexes = (
            (('to_group', 'status'), False),
        )


class PlatformNotification(BaseModel):
    id = AutoField()
    start_time = DateTimeField(default=datetime.now,
                               verbose_name='开始时间')
    end_time = DateTimeField(null=True, verbose_name='结束时间')
    content = TextField(default='', verbose_name='通知内容')
    status = SmallIntegerField(default=1, verbose_name='是否有效')

    class Meta:
        table_name = 'platform_notification'
        indexes = (
            (('start_time', 'end_time', 'status'), False),
        )


class PlatformInfo(BaseModel):
    id = AutoField()
    name = CharField(max_length=32, default='', verbose_name='平台名称')
    consumer_tel = CharField(max_length=32, default='', verbose_name='客服电话')
    description = TextField(default='', verbose_name='平台介绍')
    logo = CharField(max_length=128, default='', verbose_name='平台logo')
    source = CharField(max_length=16, default='', verbose_name='来源')
    status = SmallIntegerField(default=1, verbose_name='是否有效')

    class Meta:
        table_name = 'platform_info'
        indexes = (
            (('source', 'status'), False),
        )


class Banner(BaseModel):
    id = AutoField()
    status = SmallIntegerField(default=1, verbose_name='是否有效')
    img = CharField(max_length=128, default='', verbose_name='图片地址')
    title = CharField(max_length=32, default='', verbose_name='banner名称')
    redirect = CharField(max_length=128, default='', verbose_name='重定向地址')
    sequence = SmallIntegerField(default=1, verbose_name='排序')
    start_time = DateTimeField(default=datetime.now,
                               verbose_name='开始时间')
    end_time = DateTimeField(null=True, verbose_name='结束时间')

    class Meta:
        table_name = 'banner'
        indexes = (
            (('start_time', 'end_time', 'status'), False),
        )
