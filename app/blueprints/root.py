#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: root.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import time
from flask.blueprints import Blueprint

bpRoot = Blueprint('root', __name__)


@bpRoot.route('/', methods=["GET"])
def root():
    return "Hello World !"
