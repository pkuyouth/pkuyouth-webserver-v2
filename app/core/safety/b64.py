#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: b64.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import base64
from ..utils import b, u


def base64_encode(s):
    return u(base64.b64encode(b(s)))

def base64_decode(s):
    return base64.b64decode(b(s))

def urlsafe_base64_encode(s):
    return u(base64.urlsafe_b64encode(b(s)))

def urlsafe_base64_decode(s):
    return base64.urlsafe_b64decode(b(s))
