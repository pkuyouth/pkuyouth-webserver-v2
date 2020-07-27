#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: config.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

from sqlalchemy.pool import QueuePool
from .const import MYSQL_CONFIG
from .redis.pool import REDIS_CONNECTION_POOL


def _mysql_url(suffix=None):
    url = "mysql+mysqldb://{user}:{password}@{host}:{port}/{database}"
    url = url.format(**MYSQL_CONFIG)
    if suffix is not None:
        url += "_%s" % suffix
    return url


class BaseConfig(object):

    ENV = "development"
    DEBUG = True
    TESTING = False

    JSON_SORT_KEYS = False
    JSON_AS_ASCII = True
    JSONIFY_PRETTYPRINT_REGULAR = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": QueuePool,
        "pool_size": 10,
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    CACHE_TYPE = "redis"
    CACHE_OPTIONS = {
        "connection_pool": REDIS_CONNECTION_POOL
    }

    CACHE_DEFAULT_TIMEOUT = 60 * 5
    CACHE_KEY_PREFIX = "pkyv2_"

    PKY_UNITTEST = False

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(BaseConfig):

    ENV = "development"
    DEBUG = True
    TESTING = False

    CACHE_KEY_PREFIX = "pkyv2_dev_"

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_BINDS = {
        "main": _mysql_url("dev"),
        "production": _mysql_url(),
    }


class TestingConfig(BaseConfig):

    ENV = "testing"
    DEBUG = True
    TESTING = True

    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    CACHE_KEY_PREFIX = "pkyv2_test_"

    SQLALCHEMY_BINDS = {
        "main": _mysql_url("test"),
        "production": _mysql_url("test")
    }


class ProductionConfig(BaseConfig):

    ENV = "production"
    DEBUG = False
    TESTING = False

    CACHE_KEY_PREFIX = "pkyv2_pro_"

    SQLALCHEMY_BINDS = {
        "main": _mysql_url(),
        "production": _mysql_url()
    }


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
