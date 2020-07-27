#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: digest.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import hashlib
import hmac
from ..utils import b, u


def bMD5(s):
    return hashlib.md5(b(s)).digest()

def bSHA1(s):
    return hashlib.sha1(b(s)).digest()

def bSHA256(s):
    return hashlib.sha256(b(s)).digest()

def xMD5(s):
    return hashlib.md5(b(s)).hexdigest()

def xSHA1(s):
    return hashlib.sha1(b(s)).hexdigest()

def xSHA256(s):
    return hashlib.sha256(b(s)).hexdigest()

def bHMAC_MD5(k, s):
    return hmac.new(b(k), b(s), hashlib.md5).digest()

def bHMAC_SHA1(k, s):
    return hmac.new(b(k), b(s), hashlib.sha1).digest()

def bHMAC_SHA256(k, s):
    return hmac.new(b(k), b(s), hashlib.sha256).digest()

def xHMAC_MD5(k, s):
    return hmac.new(b(k), b(s), hashlib.md5).hexdigest()

def xHMAC_SHA1(k, s):
    return hmac.new(b(k), b(s), hashlib.sha1).hexdigest()

def xHMAC_SHA256(k, s):
    return hmac.new(b(k), b(s), hashlib.sha256).hexdigest()
