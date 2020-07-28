#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: parser.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

from flask import request
from ..exceptions import RequestArgumentError
from ..utils import bool_


def get_field(type_, key, limited=None, regex=None, data=None, nullable=False, default=None):
    """
    解析参数，并校验参数值的合理性
    ----------------------------
    Input
        - type_       callable              类型转换函数 string -> T
        - key         str/tupel/list/set    表单 key 可以传入多个，标识键名有多种可能
        - limited     tuple/list/set        表单 value 的合理值范围
        - regex       re.compile            编译好的正则表达式实例，用于检查 value 的格式
        - data        dict                  指定解析的数据源，否则根据 request.method 判断数据源
        - nullable    bool                  若设为 True ，则当 key 不存在于表单中时，会返回 None
        - default     object                如果 nullable 则返回这个默认值

    """
    if data is not None:
        _data = data
    elif request.method == "GET":
        _data = request.args
    elif request.is_json:
        _data = request.json
    elif request.method == "POST":
        _data = request.form
    else:
        _data = request.values()

    if isinstance(key, str):
        value = _data.get(key)
    elif isinstance(key, (tuple, list, set)):
        for k in key:
            if k in _data:
                value = _data[k]
                break
        else:
            value = None
    else:
        raise TypeError("Unexcepted type %s of %r" % (type(key), key))

    if value is None:
        if nullable:
            return default
        raise RequestArgumentError("A required field is missing.")

    try:
        value = type_(value)
    except ValueError:
        if value == '' and nullable:
            return None
        raise RequestArgumentError("Field type error.")

    if limited is not None and value not in limited:
        raise RequestArgumentError("Unexpected field value.")

    if regex is not None and regex.match(value) is None:
        raise RequestArgumentError("Incorrect value format.")

    return value


def get_str_field(key, limited=None, regex=None, data=None):
    return get_field(str, key, limited=limited, regex=regex, data=data, nullable=False)

def get_optional_str_field(key, limited=None, regex=None, data=None, default=None):
    return get_field(str, key, limited=limited, regex=regex, data=data, nullable=True, default=default)

def get_int_field(key, limited=None, data=None):
    return get_field(int, key, limited=limited, data=data, nullable=False)

def get_optional_int_field(key, limited=None, data=None, default=None):
    return get_field(int, key, limited=limited, data=data, nullable=True, default=default)

def get_float_field(key, limited=None, data=None):
    return get_field(float, key, limited=limited, data=data, nullable=False)

def get_optional_float_field(key, limited=None, data=None, default=None):
    return get_field(float, key, limited=limited, data=data, nullable=True, default=default)

def get_boolean_field(key, data=None):
    return get_field(bool_, key, data=data, nullable=False)

def get_optional_boolean_field(key, data=None, default=None):
    return get_field(bool_, key, data=data, nullable=True, default=default)
