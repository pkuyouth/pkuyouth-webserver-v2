#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: pool.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import redis
from ..const import REDIS_CONFIG

REDIS_CONNECTION_POOL = redis.ConnectionPool(**REDIS_CONFIG)
