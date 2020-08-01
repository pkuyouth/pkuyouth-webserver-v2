#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: __init__.py
# Created Date: 2020-07-31
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import re
import math
from pypinyin import lazy_pinyin
from flask import Blueprint, render_template
from ...models import db, Article, Reporter, ArticleReporter
from ...core.flask.parser import get_optional_int_field, get_int_field,\
    get_bool_field, get_str_field, get_optional_str_field
from ...core.exceptions import RequestArgumentError

bpAdmin = Blueprint('admin', __name__)

re_sep = re.compile(r',|，| |　|\s')

PAGE_SIZE = 50

COLUMNS = ["调查","雕龙","光阴","机动","评论","人物","视界","言己","姿势","摄影","现场",
           "又见","特稿","节日","未明","图说","征稿","招新","手记","副刊","对话","论衡",
           "休刊","纪念","聚焦燕园","休闲娱乐","社会舆论","校友往事","教育科技","排行榜",
           "生日","译天下","新年献词"]

COLUMNS.sort(key=lambda c: lazy_pinyin(c))
COLUMNS.append("其他")

def get_range(page, size):
    page = max(page, 1)
    return ((page - 1) * size, page * size)


@bpAdmin.route('/', methods=["GET"], strict_slashes=False)
@bpAdmin.route('/article', methods=["GET"])
def article_html():
    """
    Method   GET
    Args:
        - page   int

    """
    page = get_optional_int_field('page', default=1)

    article_count = db.session.\
            query(db.func.count(Article.aid)).\
            first()[0]

    max_page = math.ceil(article_count / PAGE_SIZE)

    st, ed = get_range(page, PAGE_SIZE)

    sbq = db.session.\
            query(Article.aid).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            slice(st, ed).\
            subquery()

    articles = db.session.\
            query(
                Article.aid,
                Article.title,
                Article.column,
                Article.masssend_time,
                Article.read_num,
                Article.like_num,
                Article.content_url,
                Article.hidden,
            ).\
            join(sbq, sbq.c.aid == Article.aid).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            all()

    return render_template('admin/article.html', page=page, max_page=max_page,
                            articles=articles)


@bpAdmin.route('/column', methods=["GET"])
def column_html():
    """
    Method   GET
    Args:
        - column   str
        - page     int

    """
    column = get_optional_str_field('column', limited=COLUMNS, default=COLUMNS[0])
    page = get_optional_int_field('page', default=1)

    if column == COLUMNS[-1]:
        sbq = db.session.\
            query(Article.aid).\
            filter(
                db.or_(
                    db.not_(Article.column.in_(COLUMNS)),
                    Article.column == COLUMNS[-1]
                )
            )
    else:
        sbq = db.session.\
            query(Article.aid).\
            filter(Article.column == column)

    article_count = sbq.count()

    max_page = math.ceil(article_count / PAGE_SIZE)

    st, ed = get_range(page, PAGE_SIZE)

    sbq = sbq.\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            slice(st, ed).\
            subquery()

    articles = db.session.\
            query(
                Article.aid,
                Article.title,
                Article.column,
                Article.masssend_time,
                Article.read_num,
                Article.like_num,
                Article.content_url,
                Article.hidden,
            ).\
            join(sbq, sbq.c.aid == Article.aid).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            all()

    return render_template('admin/column.html', page=page, max_page=max_page,
                            column=column, columns=COLUMNS, articles=articles)


@bpAdmin.route('/reporter', methods=["GET"])
def reporter_html():
    """
    Method   GET
    Args:
        - page   int

    """
    page = get_optional_int_field('page', default=1)

    article_count = db.session.\
            query(db.func.count(Article.aid)).\
            first()[0]

    max_page = math.ceil(article_count / PAGE_SIZE)

    st, ed = get_range(page, PAGE_SIZE)

    sbq1 = db.session.\
            query(Article.aid).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            slice(st, ed).\
            subquery()

    sbq2 = db.session.\
            query(
                ArticleReporter.aid,
                Reporter.name,
                ArticleReporter.is_leader,
            ).\
            join(Reporter, ArticleReporter.rid == Reporter.rid).\
            subquery()

    articles = db.session.\
            query(
                Article.aid,
                Article.title,
                Article.column,
                db.func.ifnull(
                    db.group_concat(
                        sbq2.c.name,
                        order_by=sbq2.c.is_leader.desc(),
                        sep=' '
                    ),
                    ''
                ).label('reporters'),
                Article.masssend_time,
                Article.read_num,
                Article.like_num,
                Article.content_url,
                Article.hidden,
            ).\
            join(sbq1, sbq1.c.aid == Article.aid).\
            outerjoin(sbq2, sbq2.c.aid == Article.aid).\
            group_by(Article.aid).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            all()

    return render_template('admin/reporter.html', page=page, max_page=max_page,
                            articles=articles)


@bpAdmin.route('/toggle_article_hidden', methods=["POST"])
def toggle_article_hidden():
    """
    Method   POST
    Form:
        - aid      int
        - hidden   bool

    """
    aid = get_int_field('aid')
    hidden = get_bool_field('hidden')

    a = Article.query.get(aid)

    if a is None:
        raise RequestArgumentError("Article %d is not found" % aid)

    if a.hidden != hidden:
        a.hidden = hidden
        db.session.commit()

    return {
        "errcode": 0
    }


@bpAdmin.route('/modify_article_column', methods=["POST"])
def modify_article_column():
    """
    Method   POST
    Form:
        - aid      int
        - column   str

    """
    aid = get_int_field('aid')
    column = get_str_field('column')

    a = Article.query.get(aid)

    if a is None:
        raise RequestArgumentError("Article %d is not found" % aid)

    if a.column != column:
        a.column = column
        db.session.commit()

    return {
        "errcode": 0
    }


@bpAdmin.route('/modify_article_reporters', methods=["POST"])
def modify_article_reporters():
    """
    Method   POST
    Form:
        - aid         int
        - reporters   str

    """
    aid = get_int_field('aid')
    reporters = get_str_field('reporters')

    a = Article.query.get(aid)

    if a is None:
        raise RequestArgumentError("Article %d is not found" % aid)

    new_names = []

    for name in re_sep.split(reporters):
        if len(name) == 0 or name in new_names:
            continue
        new_names.append(name)

    r_existed = db.session.\
            query(
                Reporter,
                ArticleReporter,
            ).\
            join(ArticleReporter).\
            filter(ArticleReporter.aid == aid).\
            all()

    r_rm = []
    r_ex = {}

    for r, ar in r_existed:
        if r.name not in new_names:
            db.session.delete(ar)
            r_rm.append(r.rid)
        else:
            r_ex[r.name] = ar

    for ix, name in enumerate(new_names):
        is_leader = (ix == 0)

        ar = r_ex.get(name)
        if ar is not None:
            if ar.is_leader != is_leader:
                ar.is_leader = is_leader
            continue

        r = Reporter.query.filter_by(name=name).first()
        if r is None:
            r = Reporter(name)
            db.session.add(r)
            db.session.flush()

        ar = ArticleReporter(aid, r.rid, is_leader=is_leader)
        db.session.add(ar)

    sbq = db.session.\
            query(ArticleReporter.aid).\
            filter(ArticleReporter.rid == Reporter.rid).\
            subquery()

    r_delete = Reporter.query.\
            filter(Reporter.rid.in_(r_rm)).\
            filter(db.not_(db.func.exists(sbq))).\
            all()

    for r in r_delete:
        db.session.delete(r)

    db.session.commit()

    return {
        "errcode": 0
    }
