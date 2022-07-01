#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/1/4:36 PM
# @Author  : Hanley
# @File    : merchat_order.py
# @Desc    :

from sanic import Blueprint

from apps.admin.views import merchant_order

merchant_bp = Blueprint(
    name="merchant",
)

merchant_bp.add_route(handler=merchant_order.CheckOutMerchantOrder.as_view(),
                      uri="/merchant_order/checkout")
