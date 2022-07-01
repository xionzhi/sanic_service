#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/26 2:29 下午
# @Author  : Hanley
# @File    : return_code.py
# @Desc    :
CODE_0 = 0
CODE_1 = 1
CODE_101 = 101
CODE_500 = 500

ZH_MAP = {
    CODE_0: "",
    CODE_1: "成功返回",
    CODE_101: "参数错误",
    CODE_500: "服务器繁忙，请稍后再试",
}
EN_MAP = {
    CODE_0: "错误返回",
    CODE_1: "成功返回",
    CODE_101: "参数错误",
    CODE_500: "服务器繁忙，请稍后再试",
}
