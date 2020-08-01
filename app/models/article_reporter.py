#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: article_reporter.py
# Created Date: 2020-07-28
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

from ..core.mysql import db

class ArticleReporter(db.Model):

    __bind_key__ = "main"
    __tablename__ = "article_reporter"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8",
    }

    aid       = db.Column(db.MYSQL_INTEGER, db.ForeignKey('article.aid'), primary_key=True)
    rid       = db.Column(db.MYSQL_INTEGER, db.ForeignKey('reporter.rid'), primary_key=True)
    is_leader = db.Column(db.MYSQL_TINYINT(1), nullable=False, server_default='0')

    def __init__(self, aid, rid, is_leader=False):
        self.aid = aid
        self.rid = rid
        self.is_leader = is_leader
