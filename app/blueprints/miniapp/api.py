#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: api.py
# Created Date: 2020-07-28
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import redis
from requests import Session
from requests.exceptions import HTTPError
from flask import current_app
from ...core.redis.pool import REDIS_CONNECTION_POOL
from ...core.utils import u
from ...core.const import MINIAPP_CONFIG
from ...core.exceptions import MiniappGetAccessTokenFailed, MiniappJscode2sessionFailed

APP_ID = MINIAPP_CONFIG['app_id']
APP_SECRET = MINIAPP_CONFIG['app_secret']
ACCESS_TOKEN_KEY = None

def _get_access_token():

    global ACCESS_TOKEN_KEY

    if ACCESS_TOKEN_KEY is None:
        ACCESS_TOKEN_KEY = current_app.config['CACHE_KEY_PREFIX'] + "miniapp_tk"

    s = Session()

    rds = redis.Redis(connection_pool=REDIS_CONNECTION_POOL)
    access_token = rds.get(ACCESS_TOKEN_KEY)

    if access_token is None:

        r = s.get(
            url="https://api.weixin.qq.com/cgi-bin/token",
            params={
                "grant_type": "client_credential",
                "appid": APP_ID,
                "secret": APP_SECRET,
            }
        )

        if not r.ok:
            raise MiniappGetAccessTokenFailed(
                    "Failed to get access_token, status_code %d" % r.status_code)

        rjson = r.json()
        errcode = rjson.get('errcode')

        if errcode is not None and errcode != 0:
            raise MiniappGetAccessTokenFailed(
                    "Failed to get access_token, errcode: %d" % errcode)

        access_token = rjson.get('access_token')
        expires_in = rjson.get('expires_in', 7200)

        if access_token is None:
            raise MiniappGetAccessTokenFailed(
                "Failed to get access_token, 'access_token' field is missing",
                payload=rjson
            )

        rds.setex(ACCESS_TOKEN_KEY, expires_in - 30, access_token)

    else:
        access_token = u(access_token)

    return access_token


def jscode2session(js_code):

    s = Session()

    r = s.get(
        url="https://api.weixin.qq.com/sns/jscode2session",
        params={
            "js_code": js_code,
            "grant_type": "authorization_code",
            "appid": APP_ID,
            "secret": APP_SECRET,
        }
    )

    if not r.ok:
        raise MiniappJscode2sessionFailed(
                "jscode2session failed, status_code: %d" % r.status_code)

    rjson = r.json()
    openid = rjson.get('openid')
    session_key = rjson.get('session_key')

    if openid is None:
        raise MiniappJscode2sessionFailed(
            "jscode2session failed, 'openid' field is missing",
            payload=rjson
        )

    if session_key is None:
        raise MiniappJscode2sessionFailed(
            "jscode2session failed, 'session_key' field is missing",
            payload=rjson
        )

    return (openid, session_key)


