#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: const.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import os
from ._internal import load_json_config, absp, mkdir, get_bool_env_var


PRODUCTION_SERVER = get_bool_env_var("PKUYOUTH_V2_PRODUCTION_SERVER", False)

if PRODUCTION_SERVER:
    CONFIG_DIR = os.environ["PKUYOUTH_V2_CONFIG_DIR"]
    CACHE_DIR  = os.environ["PKUYOUTH_V2_CACHE_DIR"]
else:
    CONFIG_DIR = absp("../../config/")
    CACHE_DIR  = absp("../../cache/")

mkdir(CACHE_DIR)


def _load_config(filename):
    return load_json_config(os.path.join(CONFIG_DIR, filename))

MYSQL_CONFIG   = _load_config("mysql.json")
REDIS_CONFIG   = _load_config("redis.json")
WXBOT_CONFIG   = _load_config("wxbot.json")
MINIAPP_CONFIG = _load_config("miniapp.json")
