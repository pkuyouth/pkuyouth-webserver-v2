#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: __init__.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import re
import time
import datetime
import calendar
from functools import wraps
from flask import Blueprint, request, abort, current_app
from itsdangerous import json
from ...models import db, Article
from ...core.redis.types import RedisList
from ...core.utils import xSHA1
from ...core.const import WXBOT_CONFIG
from ...core.exceptions import WxbotAuthFailed
from .message import receive, reply, text


bpWxbot = Blueprint('wxbot', __name__)

TOKEN = WXBOT_CONFIG["token"]
ALIST_PREFIX = None
ALIST_EXPIRES = 300
SEARCH_RESULT_COUNT = 10

EVENT_REPLY_MAP = {
    'list_columns': text.COLUMNS_INTRO,
    'about_us': text.ABOUT_US,
    'join_us': text.JOIN_US,
    'introduce_Q': text.Q_INTRO,
}


re_Q = re.compile(r'^q(.*?)$|q', re.I)
re_index = re.compile(r'^(\d{1,3})$')
re_date = re.compile(r'^(\d{2})(\d{2})(\d{2})$|^(\d{2})(\d{2})$')


def get_time_range(year, month, day=None):

    year += 2000

    if day is None:
        st = datetime.datetime(year, month, 1)
        span = calendar.monthrange(year, month)[1]
    else:
        st = datetime.datetime(year, month, day)
        span = 1

    ed = st + datetime.timedelta(span)

    return (int(st.timestamp()), int(ed.timestamp()))


def normalize_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        if isinstance(ret, reply.Message):
            ret = ret.xml
        return ret
    return wrapper


@bpWxbot.route('/', methods=["GET","POST"], strict_slashes=False)
@normalize_response
def root():

    global ALIST_PREFIX

    if ALIST_PREFIX is None:
        ALIST_PREFIX = current_app.config['CACHE_KEY_PREFIX'] + "alist_"

    if request.method == "GET":

        keys = ['timestamp','nonce','signature','echostr']
        fields = tuple(map(request.args.get, keys))

        if any( f is None for f in fields ):
            abort(404)

        timestamp, nonce, signature, echostr = fields

        raw = ''.join(sorted([TOKEN, timestamp, nonce]))

        if xSHA1(raw) != signature:
            raise WxbotAuthFailed("Verification Error !")

        return echostr

    elif request.method == "POST":

        keys = ['signature','nonce','openid','timestamp']

        if any( k not in request.args for k in keys ):
            abort(404)

        msg = receive.parse_message(request.stream.read())
        no_reply = 'success'

        if isinstance(msg, receive.Message):

            to_user = msg.FromUserName
            from_user = msg.ToUserName
            message_type = msg.MsgType

            if message_type == 'text':

                content = msg.Content.strip()
                if content == '[Unsupported Message]':
                    return no_reply

                ## syntax: Q [any]

                mat = re_Q.match(content)
                if mat is None:
                    return no_reply

                keyword = mat.group(1)
                keyword = keyword.strip() if keyword is not None else None

                if keyword is None or len(keyword) == 0:
                    return reply.TextMessage(to_user, from_user, text.Q_INTRO)

                ## syntax: Q [index]

                mat = re_index.match(keyword)

                if mat is not None:

                    ix = int(mat.group(1)) - 1

                    if ix < 0:
                        return reply.TextMessage(to_user, from_user,
                                                 text.INDEX_OUT_OF_RANGE)

                    alist = RedisList(ALIST_PREFIX + to_user)
                    article = alist[ix]

                    if article is None:
                        return reply.TextMessage(to_user, from_user,
                                                 text.INDEX_OUT_OF_RANGE)

                    alist.expires(ALIST_EXPIRES)
                    article = json.loads(article)

                    return reply.ArticleMessage(to_user, from_user, [article])

                ## syntax: Q [keywords]

                mat = re_date.match(keyword)

                if mat is None:

                    sbq = db.session.\
                        query(
                            Article.aid,
                            db.fts_match(
                                Article.ix_text,
                                keyword,
                                db.fts_match.BOOLEAN
                            ).label('score')
                        ).\
                        order_by(
                            db.desc('score'),
                            Article.masssend_time.desc(),
                            Article.idx.asc()
                        ).\
                        limit(SEARCH_RESULT_COUNT).\
                        subquery()

                    articles = db.session.\
                        query(
                            Article.title,
                            Article.digest,
                            Article.cover_url,
                            Article.content_url,
                        ).\
                        join(sbq, sbq.c.aid == Article.aid).\
                        order_by(
                            sbq.c.score.desc(),
                            Article.masssend_time.desc(),
                            Article.idx.asc()
                        ).\
                        all()

                    if len(articles) == 0:
                        return reply.TextMessage(to_user, from_user,
                                                 text.NO_ARTICLE_MATCHED)

                    alist = RedisList(ALIST_PREFIX + to_user)
                    alist.clear()

                    if len(articles) == 1:
                        return reply.ArticleMessage(to_user, from_user, articles)

                    content = '\n'.join("(%d) %s" % (ix + 1, a.title)
                                        for (ix, a) in enumerate(articles))

                    articles = [ json.dumps(a._asdict()) for a in articles ]
                    alist.append(*articles)
                    alist.expires(ALIST_EXPIRES)

                    return reply.TextMessage(to_user, from_user, content)

                ## syntax: Q[YYMMDD] / Q[YYMM]

                if mat.group(1) is not None:
                    year, month, day = map(int, mat.group(1, 2, 3))
                elif mat.group(4) is not None:
                    year, month = map(int, mat.group(4, 5))
                    day = None
                else:
                    return no_reply

                try:
                    st, ed = get_time_range(year, month, day)
                except ValueError as e:
                    return reply.TextMessage(to_user, from_user, text.INVALID_DATE)

                ## syntax: Q [YYMMDD]

                if mat.group(1) is not None:

                    sbq = db.session.\
                        query(Article.aid).\
                        filter(Article.masssend_time.between(st, ed)).\
                        order_by(
                            Article.masssend_time.desc(),
                            Article.idx.asc()
                        ).\
                        subquery()

                    articles = db.session.\
                        query(
                            Article.title,
                            Article.digest,
                            Article.cover_url,
                            Article.content_url
                        ).\
                        join(sbq, sbq.c.aid == Article.aid).\
                        order_by(
                            Article.masssend_time.desc(),
                            Article.idx.asc()
                        ).\
                        all()

                    if len(articles) == 0:
                        return reply.TextMessage(to_user, from_user,
                                                 text.NO_ARTICLE_ON_THIS_DAY)

                    alist = RedisList(ALIST_PREFIX + to_user)
                    alist.clear()

                    if len(articles) == 1:
                        return reply.ArticleMessage(to_user, from_user, articles)

                    content = '\n'.join("(%d) %s" % (ix + 1, a.title)
                                        for (ix, a) in enumerate(articles))

                    articles = [ json.dumps(a._asdict()) for a in articles ]
                    alist.append(*articles)
                    alist.expires(ALIST_EXPIRES)

                    return reply.TextMessage(to_user, from_user, content)

                ## syntax: Q [YYMM]

                else:

                    articles = db.session.\
                        query(
                            Article.title,
                            Article.masssend_time
                        ).\
                        filter(Article.masssend_time.between(st, ed)).\
                        order_by(
                            Article.masssend_time.desc(),
                            Article.idx.asc()
                        ).\
                        all()

                    if len(articles) == 0:
                        return reply.TextMessage(to_user, from_user,
                                                 text.NO_ARTICLE_IN_THIS_MONTH)

                    articles = [
                        (
                            time.strftime("%m-%d", time.localtime(a.masssend_time)),
                            a.title
                        )
                        for a in articles
                    ]

                    content = '\n'.join("%s %s" % a for a in articles)

                    return reply.TextMessage(to_user, from_user, content)

        elif isinstance(msg, receive.Event):

            to_user = msg.FromUserName
            from_user = msg.ToUserName
            event_type = msg.Event

            if event_type == 'subscribe':
                return reply.TextMessage(to_user, from_user, text.WELCOME)

            if event_type == 'CLICK':

                content = EVENT_REPLY_MAP.get(msg.EventKey)
                if content is None:
                    return no_reply

                return reply.TextMessage(to_user, from_user, content)

        return no_reply

    else:
        abort(405)
