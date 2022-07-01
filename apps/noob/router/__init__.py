#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/27 10:02 上午
# @Author  : Hanley
# @File    : __init__.py.py
# @Desc    :
from sanic import Blueprint

from apps.noob.router.index import index_bp
from apps.noob.router.scan import scan_bp

noob_bp = Blueprint.group(index_bp, scan_bp, url_prefix="/noob")
