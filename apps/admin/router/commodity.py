#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 4:51 下午
# @Author  : Hanley
# @File    : server.py
# @Desc    :

from sanic import Blueprint

from apps.admin.views import commodity

commodity_bp = Blueprint(
    name="commodity",
)

commodity_bp.add_route(handler=commodity.CheckOutCommodity.as_view(),
                       uri="/commodity/checkout")
