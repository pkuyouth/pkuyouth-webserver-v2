#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: types.py
# Created Date: 2020-07-28
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import redis
from .pool import REDIS_CONNECTION_POOL


class RedisContainer(object):

    def __init__(self, name, connection_pool=REDIS_CONNECTION_POOL):
        self._name = name
        self._conn = redis.Redis(connection_pool=connection_pool)

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return "%s(%r)" % (
                    self.__class__.__name__,
                    self._name,
                )

    def __len__(self):
        raise NotImplementedError

    def all(self):
        raise NotImplementedError

    def __iter__(self):
        return iter(self.all())

    def empty(self):
        return len(self) == 0

    def clear(self):
        return self._conn.delete(self._name)

    def expires(self, time):
        return self._conn.expire(self._name, time)

    def ttl(self):
        return self._conn.ttl(self._name)


class RedisList(RedisContainer):

    def __len__(self):
        return self._conn.llen(self._name)

    def all(self):
        return self._conn.lrange(self._name, 0, -1)

    def __getitem__(self, pos):
        return self._conn.lindex(self._name, pos)

    def front(self):
        return self._conn.lindex(self._name, 0)

    def back(self):
        return self._conn.lindex(self._name, -1)

    def append(self, *values):
        return self._conn.rpush(self._name, *values)

    def pop(self):
        return self._conn.rpop(self._name)

    def appendleft(self, *values):
        return self._conn.lpush(self._name, *values)

    def popleft(self):
        return self._conn.lpop(self._name)
