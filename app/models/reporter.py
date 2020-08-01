#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: reporter.py
# Created Date: 2020-07-28
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

from ..core.mysql import db

class Reporter(db.Model):

    __bind_key__ = "main"
    __tablename__ = "reporter"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8",
    }

    rid  = db.Column(db.MYSQL_INTEGER, primary_key=True, autoincrement='auto')
    name = db.Column(db.MYSQL_VARCHAR(128), nullable=False)

    ix_name = db.Index('ix_name', name, unique=True)

    def __init__(self, name):
        self.name = name
