#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: wxuser.py
# Created Date: 2020-07-28
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

from ..core.mysql import db

class WxUser(db.Model):

    __bind_key__ = "main"
    __tablename__ = "wxuser"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8",
    }

    openid           = db.Column(db.MYSQL_CHAR(28), primary_key=True)
    auto_change_card = db.Column(db.MYSQL_TINYINT(1), nullable=False, server_default='0')
    use_small_card   = db.Column(db.MYSQL_TINYINT(1), nullable=False, server_default='1')
