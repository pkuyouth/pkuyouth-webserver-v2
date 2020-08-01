#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: __init__.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql.types import CHAR, VARCHAR, TEXT, INTEGER,\
    TINYINT, BIGINT, DATETIME
from .model import Model
from .expression import fts_match, group_concat

db = SQLAlchemy(model_class=Model)

db.MYSQL_CHAR = CHAR
db.MYSQL_VARCHAR = VARCHAR
db.MYSQL_TEXT = TEXT
db.MYSQL_INTEGER = INTEGER
db.MYSQL_TINYINT = TINYINT
db.MYSQL_BIGINT = BIGINT
db.MYSQL_DATETIME = DATETIME

db.fts_match = fts_match
db.group_concat = group_concat
