#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/27 10:02 上午
# @Author  : Hanley
# @File    : __init__.py.py
# @Desc    :
from sanic import Blueprint

from apps.admin.router.commodity import commodity_bp
from apps.admin.router.merchat_order import merchant_bp

admin_bp = Blueprint.group(commodity_bp, merchant_bp, url_prefix="/admin")
