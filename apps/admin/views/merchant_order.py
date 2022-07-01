#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/1/4:29 PM
# @Author  : Hanley
# @File    : merchant_order.py
# @Desc    :
from sanic.views import HTTPMethodView

from apps.admin.controller.merchant_order import MerchantOrderController
from core.base import BaseRequestHandler, ReturnData, SuccessData
from core.wrapper import uri_check


class CheckOutMerchantOrder(HTTPMethodView):

    @uri_check()
    async def get(self, request: BaseRequestHandler) -> ReturnData:
        page = int(request.parameter['page'])
        size = int(request.parameter['size'])
        start_time = request.parameter.get('start_time')
        end_time = request.parameter.get('end_time')
        merchant_id = request.parameter.get('merchant_id')
        merchant_orders, total = await MerchantOrderController(request).mo_list(
            page, size, start_time=start_time, end_time=end_time,
            merchant_id=merchant_id)
        return SuccessData(data={
            'merchant_orders': merchant_orders,
            'page': page, 'size': size, 'total': total})

    @uri_check()
    async def post(self, request: BaseRequestHandler):
        merchant_id = request.parameter['merchant_id']
        commodity_ids = request.parameter['commodity_ids']
        pay_amount = request.parameter['pay_amount']
        deadline_time = request.parameter['deadline_time']
        await MerchantOrderController(request).mo_create(
            merchant_id, commodity_ids, pay_amount, deadline_time=deadline_time)
        return SuccessData()
