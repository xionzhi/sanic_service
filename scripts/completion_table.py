#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/26 6:06 下午
# @Author  : Hanley
# @File    : completion_table.py
# @Desc    :
import os
import sys
import traceback

from model.mysql.base import BaseModel, mysql_client

proPath = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)))  # noqa
if proPath not in sys.path:
    sys.path.append(proPath)  # noqa
from model.mysql.common import *
from model.mysql.user import *
from libs.log import logging


def generate_subclass(sub_model: list, list_model: list) -> list:
    for item in sub_model:
        if item.__subclasses__():
            generate_subclass(item.__subclasses__(), list_model)
        if item.__name__ not in list_model and len(item.__subclasses__()) == 0:
            list_model.append(item)
    return list_model


def find_orm() -> list:
    sub_model = BaseModel.__subclasses__()
    list_model = generate_subclass(sub_model, [])
    list_model = [item for item in list_model if not item.table_exists()]
    return list_model


def insert_single_data(model, dataList, chunk_size=100):
    with mysql_client.allow_sync():
        with mysql_client.atomic():
            try:
                logging.debug(f"start insert data to {model}")
                for i in range(0, len(dataList), chunk_size):
                    logging.debug(f"data: {dataList[i: i + chunk_size]}")
                    model.insert_many(dataList[i: i + chunk_size]).execute()
            except BaseException:
                logging.error(traceback.format_exc())


def insert_multi_data(modelList, dataDict):
    for model in modelList:
        if model.select().count() > 0:
            logging.debug(f"{model.__name__} already had data, so continue")
            continue
        for key, value in dataDict.items():
            if model.__name__ == key:
                insert_single_data(model, value)


def complete_table():
    """
    补全mysql表
    :return:
    """
    miss_model = find_orm()
    with mysql_client.allow_sync():
        with mysql_client.atomic():
            logging.debug(
                f"Missing models: "
                f"{[model.__name__ for model in miss_model]}")
            if len(miss_model):
                for _t in miss_model:
                    logging.debug(f"start create tables {_t.__name__}")
                    _t.create_table()
                    logging.debug(f"end create tables {_t.__name__}")
    logging.debug("complete_table done")


if __name__ == '__main__':
    complete_table()
