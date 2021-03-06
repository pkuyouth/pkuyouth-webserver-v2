#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: manage.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import sys
import unittest
from IPython import start_ipython
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import request, g
from flask_script import Manager
from flask_script.commands import ShowUrls
from flask_sqlalchemy.model import DefaultMeta
from app import create_app, db
from app import models
from app.core.config import CONFIGS

manager = Manager()
manager.add_command('urls', ShowUrls())


@manager.command
def shell():
    """ run IPython shell """

    from app.blueprints.miniapp import init_utoken_map
    init_utoken_map()

    from app.blueprints.miniapp import utoken_map

    ctx = {
        "app": manager.app,
        "request": request,
        "g": g,
        "db": db,
        "utoken_map": utoken_map,
    }

    ctx.update({
        k: v
        for k, v in vars(models).items()
        if not k.startswith("_") and isinstance(v, DefaultMeta)
    })

    start_ipython(argv=sys.argv[2:], user_ns=ctx)


@manager.option("-h", "--host", dest="host", default="127.0.0.1")
@manager.option("-p", "--port", dest="port", default=7072)
@manager.option("--no-proxy-fix", dest="no_proxy_fix", action="store_true", default=False)
def runserver(host, port, no_proxy_fix):
    """ run development server """
    app = manager.app
    if not no_proxy_fix:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
    run_simple(host, port, app, use_reloader=True, use_debugger=True)


@manager.command
def test():
    """ run unittests """
    tests = unittest.TestLoader().discover("test/unit/")
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':

    if len(sys.argv) >= 2 and sys.argv[1] in CONFIGS:
        env = sys.argv.pop(1)
    else:
        env = "development"

    manager.app = create_app(env)
    manager.run()
