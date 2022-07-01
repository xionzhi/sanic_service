#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/1/1:38 PM
# @Author  : Hanley
# @File    : merchant_order.py
# @Desc    :
import datetime
from typing import Text, Tuple

from apps.admin.controller.commodity import CommodityController
from core.base import BaseRequestHandler
from libs.bolts import format_datetime, generate_id
from model.mysql.user import MerchantOrder


class MerchantOrderController:

    def __init__(self, request: BaseRequestHandler):
        self.request = request
        self.commodity_ctl = CommodityController(request)

    @classmethod
    def generate_order_id(cls) -> Text:
        return generate_id(prefix='MO')

    async def mo_create(self, merchant_id: int, commodity_ids: Text,
                        pay_amount: float, **kwargs):
        """
        创建商户订单
        :param merchant_id:
        :param commodity_ids:
        :param pay_amount:
        :param kwargs:
        :return:
        """
        extra = dict()
        # 冗余开通类型
        extra['recharge_type'] = 'deferred_renewal'
        # 冗余套餐标题
        purchasing_title = []
        for commodity_id in commodity_ids.split(','):
            commodity_cache = await self.commodity_ctl.commodity_get_cache(
                commodity_id)
            if commodity_cache.get('title', ''):
                purchasing_title.append(commodity_cache['title'])
        extra['purchasing_title'] = ",".join(purchasing_title)
        # 到期时间
        if kwargs.get('deadline_time'):
            extra['deadline_time'] = kwargs['deadline_time']

        _insert = {
            'order_id': self.generate_order_id(),
            'merchant_id': merchant_id,
            'commodity_ids': commodity_ids,
            'pay_status': 1,
            'pay_amount': pay_amount,
            'extra': extra
        }

        async with self.request.mysql.atomic():
            count_sql = MerchantOrder.select(MerchantOrder.id).where(
                MerchantOrder.merchant_id == merchant_id)
            if not await self.request.mysql.count(count_sql):
                _insert['extra']['recharge_type'] = 'first_charge'

            await self.request.mysql.execute(
                MerchantOrder.insert(**_insert))
        return

    async def mo_list(self, page=1, size=10, **kwargs) -> Tuple:
        """
        商户订单列表
        :param page:
        :param size:
        :param kwargs:
        :return:
        """
        _display = (
            MerchantOrder.order_id,
            MerchantOrder.merchant_id,
            MerchantOrder.commodity_ids,
            MerchantOrder.pay_amount,
            MerchantOrder.create_time,
            MerchantOrder.extra,
        )
        sql = MerchantOrder.select(*_display)
        if kwargs.get('start_time'):
            _start_time = datetime.datetime.strptime(
                kwargs['start_time'], '%Y-%m-%d')
            sql = sql.where(MerchantOrder.create_time >= _start_time)
        if kwargs.get('end_time'):
            _end_time = datetime.datetime.strptime(
                kwargs['end_time'], '%Y-%m-%d')
            sql = sql.where(MerchantOrder.create_time <= _end_time)
        if kwargs.get('merchant_id'):
            sql = sql.where(MerchantOrder.merchant_id == kwargs['merchant_id'])
        total = await self.request.mysql.count(sql, clear_limit=True)
        if page and size:
            sql = sql.paginate(int(page), int(size))

        data = []
        for item in await self.request.mysql.execute(sql):
            item: MerchantOrder
            _data = {
                'order_id': item.order_id,
                # TODO 获取商户信息
                'merchant_info': {
                    'merchant_id': item.merchant_id,
                },
                'commodity_ids': item.commodity_ids,
                'pay_amount': item.pay_amount,
                'create_time': format_datetime(item.create_time),
                'extra': item.extra
            }
            data.append(_data)
        return data, total
