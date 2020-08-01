#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: __init__.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import time
from flask import Flask, jsonify
from .core.config import CONFIGS
from .core.mysql import db
from .core.exceptions import PKUYouthException
from .blueprints.root import bpRoot
from .blueprints.wxbot import bpWxbot
from .blueprints.miniapp import bpMiniapp
from .blueprints.admin import bpAdmin

def create_app(config):

    app = Flask(__name__)

    cfg = CONFIGS[config]
    app.config.from_object(cfg)

    cfg.init_app(app)
    db.init_app(app)

    app.register_blueprint(bpRoot)
    app.register_blueprint(bpWxbot, url_prefix="/wxbot")
    app.register_blueprint(bpMiniapp, url_prefix="/miniapp")
    app.register_blueprint(bpAdmin, url_prefix="/admin")

    @app.errorhandler(PKUYouthException)
    def handle_pkuyouth_exception(e):
        r = jsonify(e.to_dict())
        r.status_code = e.status_code
        return r

    def strftime(timestamp, format):
        return time.strftime(format, time.localtime(timestamp))

    app.jinja_env.filters['strftime'] = strftime

    return app
