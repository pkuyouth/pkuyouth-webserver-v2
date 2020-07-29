#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: article.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

from ..core.mysql import db

class Article(db.Model):

    __bind_key__ = "main"
    __tablename__ = "article"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8",
    }

    aid           = db.Column(db.MYSQL_INTEGER, primary_key=True, autoincrement='auto')
    appmsgid      = db.Column(db.MYSQL_CHAR(10), nullable=False)
    idx           = db.Column(db.MYSQL_TINYINT(1), nullable=False)
    sn            = db.Column(db.MYSQL_TEXT, nullable=False)
    title         = db.Column(db.MYSQL_TEXT(charset='utf8mb4'), nullable=False)
    digest        = db.Column(db.MYSQL_TEXT(charset='utf8mb4'), nullable=True)
    content       = db.Column(db.MYSQL_TEXT(charset='utf8mb4'), nullable=True)
    column        = db.Column(db.MYSQL_VARCHAR(128), nullable=True, server_default='')
    cover_url     = db.Column(db.MYSQL_TEXT, nullable=False)
    content_url   = db.Column(db.MYSQL_TEXT, nullable=False)
    like_num      = db.Column(db.MYSQL_INTEGER, nullable=False)
    read_num      = db.Column(db.MYSQL_INTEGER, nullable=False)
    masssend_time = db.Column(db.MYSQL_BIGINT, nullable=False)
    hidden        = db.Column(db.MYSQL_TINYINT(1), nullable=False, server_default='0')

    ix_msgid      = db.Index('ix_msgid', appmsgid, idx, unique=True)
    ix_column     = db.Index('ix_column', column)
    ix_time       = db.Index('ix_time', masssend_time)
    ix_hidden     = db.Index('ix_hidden', hidden)
    ix_read_num   = db.Index('ix_read_num', read_num)
    ix_text       = db.Index('ix_text', title, digest, content,
                             mysql_prefix='FULLTEXT', mysql_with_parser='ngram')

