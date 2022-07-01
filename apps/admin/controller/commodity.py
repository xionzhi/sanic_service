#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/27 11:42 上午
# @Author  : Hanley
# @File    : commodity.py
# @Desc    :
from typing import Dict, Text

import ujson

from config.constant import RedisKey
from core.base import BaseRequestHandler
from model.mysql.common import Commodity


class CommodityController:

    def __init__(self, request: BaseRequestHandler):
        self.request = request

    async def commodity_modify(self, commodity_id: int, **kwargs):
        """
        更新套餐内容
        :param commodity_id:
        :param kwargs:
        :return:
        """
        _update = dict()
        if kwargs.get('content'):
            _update.update(content=kwargs['content'])
        if kwargs:
            async with self.request.mysql.atomic():
                sql = Commodity.update(**_update).where(
                    Commodity.id == commodity_id)
                await self.request.mysql.execute(sql)

            await self.request.redis.delete(RedisKey.COMMODITY_CACHE_HASH)
        return

    async def commodity_set_cache(self, commodity: Dict):
        """
        设置套餐缓存
        :param commodity:
        :return:
        """
        self.request.log.debug(f'commodity: {commodity}')
        cache_key = RedisKey.COMMODITY_CACHE_HASH
        if not await self.request.redis.exists(cache_key):
            await self.request.redis.hmset_dict(cache_key, commodity)
        return

    async def commodity_get_cache(self, commodity_id=None) -> Dict:
        """
        获取套餐缓存
        :param commodity_id:
        :return:
        """
        cache_key = RedisKey.COMMODITY_CACHE_HASH
        if commodity_id is not None:
            cache_data = await self.request.redis.hget(cache_key, commodity_id)
            if not cache_data:
                return {}
            cache_data = ujson.loads(cache_data)
        else:
            cache_data = await self.request.redis.hgetall(cache_key)
            if not cache_data:
                return {}
            cache_data = {int(k): ujson.loads(v) for k, v in cache_data.items()}
        return cache_data

    async def commodity_list(self, to_group: Text, **kwargs):
        """
        查询套餐
        :param to_group:
        :param kwargs:
        :return:
        """
        cache_data = await self.commodity_get_cache()
        if cache_data:
            return list(cache_data.values())

        _fields = (
            Commodity.id,
            Commodity.title,
            Commodity.content,
        )
        sql = Commodity.select(*_fields).where(
            (Commodity.to_group == to_group) &
            (Commodity.status == 1))
        if kwargs.get('where'):
            sql = sql.where(kwargs['where'])
        data = []
        cache_data = dict()
        for item in await self.request.mysql.execute(sql):
            item: Commodity
            _data = {
                'commodity_id': item.id,
                'title': item.title,
                'content': item.content,
            }
            data.append(_data)
            cache_data[item.id] = ujson.dumps(_data)
        await self.commodity_set_cache(cache_data)
        return data
