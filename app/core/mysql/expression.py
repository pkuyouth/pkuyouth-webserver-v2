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
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy import literal


class fts_match(ColumnElement):

    DEFAULT = ''
    BOOLEAN = 'IN BOOLEAN MODE'
    NATURAL = 'IN NATURAL LANGUAGE MODE'
    QUERY_EXPANSION = 'WITH QUERY EXPANSION'

    def __init__(self, index, against, mode=DEFAULT):
        self.index = index
        self.against = against
        self.mode = mode


@compiles(fts_match)
def _fts_match(element, compiler, **kwargs):
    sql = "MATCH (%s) AGAINST (%s" % (
        ", ".join(compiler.process(c, **kwargs) for c in element.index.columns),
        compiler.process(literal(element.against), **kwargs)
    )

    if element.mode != fts_match.DEFAULT:
        sql += " %s" % element.mode

    return sql + ")"


class group_concat(ColumnElement):

    def __init__(self, expr, order_by=None, sep=None):
        self.expr = expr
        self.order_by = order_by
        self.sep = sep


@compiles(group_concat)
def _group_concat(element, compiler, **kwargs):
    sql = "GROUP_CONCAT(%s" % (
        compiler.process(element.expr, **kwargs)
    )

    if element.order_by is not None:
        sql += " ORDER BY %s" % compiler.process(element.order_by, **kwargs)

    if element.sep is not None:
        sql += " SEPARATOR %s" % compiler.process(literal(element.sep), **kwargs)

    return sql + ")"
