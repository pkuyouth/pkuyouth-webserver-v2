#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: wxuser_article.py
# Created Date: 2020-07-28
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

from ..core.mysql import db

class WxUserArticle(db.Model):

    __bind_key__ = "main"
    __tablename__ = "wxuser_article"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8",
    }

    openid = db.Column(db.MYSQL_CHAR(28), db.ForeignKey('wxuser.openid'), primary_key=True)
    aid    = db.Column(db.MYSQL_INTEGER, db.ForeignKey('article.aid'), primary_key=True)
    ctime  = db.Column(db.BIGINT, nullable=False)
