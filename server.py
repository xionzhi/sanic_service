# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : server.py.py
# Time       ：30/6/2022 3:55 PM
# Author     ：xionzhi
# version    ：python 3.9
# Description：
"""

from apps.serve import create_app
from libs.log import logging

app = create_app()

logging.info(f'config: \n\t{app.config.TEST_ENV}')
