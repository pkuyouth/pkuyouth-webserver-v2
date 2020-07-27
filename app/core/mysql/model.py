#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: model.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import time
from flask_sqlalchemy.model import Model as _Model

class Model(_Model):

    def to_dict(self):
        return {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        }

    @staticmethod
    def now():
        return int(time.time())
