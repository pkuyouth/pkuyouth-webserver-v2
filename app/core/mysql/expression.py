#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: expression.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy import literal

class FulltextMatch(ClauseElement):

    DEFAULT = ''
    BOOLEAN = 'IN BOOLEAN MODE'
    NATURAL = 'IN NATURAL LANGUAGE MODE'
    QUERY_EXPANSION = 'WITH QUERY EXPANSION'

    def __init__(self, index, against, mode=DEFAULT):
        self.index = index
        self.against = literal(against)
        self.mode = mode


@compiles(FulltextMatch)
def _match(element, compiler, **kwargs):
    return "MATCH (%s) AGAINST (%s %s)" % (
        ", ".join(compiler.process(c, **kwargs) for c in element.index.columns),
        compiler.process(element.against),
        element.mode,
    )
