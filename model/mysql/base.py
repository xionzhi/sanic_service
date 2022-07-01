#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/6/30/4:56 PM
# @Author  : Hanley
# @File    : base.py
# @Desc    :
from datetime import date, datetime

import ujson
from peewee import *

from libs.bolts import format_datetime, yaml_config
from utils.dbClient import AsyncPeewee

mysql_client = AsyncPeewee.init_db(yaml_config('MYSQL'))


class _BaseModel(Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _to_dict(self, display_fields, fmt_datetime=True):
        result = dict()
        for fields in display_fields:
            value = getattr(self, fields)
            if fmt_datetime and isinstance(
                    value, (datetime, date)):
                value = format_datetime(value)
            result.setdefault(fields, value)
        return result


class BaseModel(_BaseModel):
    class Meta:
        database = mysql_client


class JsonField(TextField):
    def db_value(self, value):
        return ujson.dumps(value, ensure_ascii=False)

    def python_value(self, value):
        if value:
            return ujson.loads(value)
