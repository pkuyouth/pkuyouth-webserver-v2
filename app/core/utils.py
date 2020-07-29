#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: utils.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

from ._internal import _bool

def b(s, encoding="utf-8"):
    """ str/int/float to bytes """
    if isinstance(s, bytes):
        return s
    if isinstance(s, (str, int ,float)):
        return str(s).encode(encoding)
    raise TypeError("unsupported type %s of %r" % (s.__class__.__name__, s))

def u(s, encoding="utf-8"):
    """ bytes/int/float to str """
    if isinstance(s, (str, int, float)):
        return str(s)
    if isinstance(s, bytes):
        return s.decode(encoding)
    raise TypeError("unsupported type %s of %r" % (s.__class__.__name__, s))

def bool_(s):
    """ str/int/float to bool """
    if isinstance(s, bool):
        return s
    if isinstance(s, str):
        return _bool(s)
    if isinstance(s, (int, float)):
        return bool(s)
    raise TypeError("unsupported type %s of %r" % (s.__class__.__name__, s))
