#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: _internal.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import os
from werkzeug.datastructures import ImmutableDict
from itsdangerous import json

def _bool(s):
    s = s.lower()
    if s in ("1", "true"):
        return True
    if s in ("0", "false"):
        return False
    raise ValueError("Unexpected boolean value %r" % s)

def get_bool_env_var(key, default=None):
    val = os.getenv(key)
    return _bool(val) if val is not None else default

def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def absp(*path):
    return os.path.normpath(os.path.abspath(
            os.path.join(os.path.dirname(__file__), *path)))

def load_json_config(file):
    assert file.endswith(".json")
    assert os.path.exists(file), "%s profile is missing" % file
    with open(file, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    return ImmutableDict(data)
