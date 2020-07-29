#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: exceptions.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth


class PKUYouthException(Exception):

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code or self.__class__.status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['errmsg'] = self.message
        return rv

class RequestArgumentError(PKUYouthException):
    """ 请求参数错误 """

class WxbotAuthFailed(PKUYouthException):
    """ 微信服务器接入认证失败 """

class MiniappGetAccessTokenFailed(PKUYouthException):
    """ 获取微信 API 访问凭证失败 """

class MiniappJscode2sessionFailed(PKUYouthException):
    """ 未能成功通过微信服务器与小程序用户建立会话 """

class MiniappUnauthorized(PKUYouthException):
    """ 小程序用户认证失败 """
    status_code = 401

