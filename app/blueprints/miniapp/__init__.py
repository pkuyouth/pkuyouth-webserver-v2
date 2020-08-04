#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: __init__.py
# Created Date: 2020-07-28
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import time
import datetime
import calendar
from functools import wraps
from collections import OrderedDict
from pypinyin import lazy_pinyin
from flask import Blueprint, current_app, g, abort
from ...models import db, WxUser, Article, WxUserArticle, Reporter, ArticleReporter
from ...core.flask.parser import get_str_field, get_int_field, get_bool_field
from ...core.redis.types import RedisAutoExpiredMap
from ...core.utils import u, xMD5
from ...core.exceptions import MiniappUnauthorized, RequestArgumentError
from .api import jscode2session

bpMiniapp = Blueprint('miniapp', __name__)

utoken_map = None

UTOKEN_EXPIRES = 3600 * 12
PAGE_SIZE = 8

QINIU_IMAGE_PREFIX = "https://qiniu.rabbitzxh.top/pkuyouth"

APP_CONFIG = {
    "prefix": {
        "column": QINIU_IMAGE_PREFIX + "/column_cover/",
        "sm_cover": QINIU_IMAGE_PREFIX + "/sm_cover/",
        "bg_cover": QINIU_IMAGE_PREFIX + "/bg_cover/"
    },
    "app_info": {
        "name": "北大青年",
        "version": "2.0.0",
    }
}

INDEX_COL_DESC = [
    {
        "id": 0,
        "cover": QINIU_IMAGE_PREFIX + '/bg_cover/26508266021.jpeg',
        "title": '随便看看',
        "desc": '随意翻翻北青的文章',
        "path": '/pages/collection-random/collection-random',
    },
    {
        "id": 1,
        "cover": QINIU_IMAGE_PREFIX + '/bg_cover/26508283011.jpeg',
        "title": '热文排行',
        "desc": '看看那些阅读量最高的文章',
        "path": '/pages/collection-hot/collection-hot',
    },
    {
        "id": 2,
        "cover": QINIU_IMAGE_PREFIX + '/bg_cover/26508251861.jpeg',
        "title": '还有更多',
        "desc": '主编们正在努力整理 ...',
        "path": '',
    }
]

COLUMNS_LIST = OrderedDict({
    "调查": "只做好一件事——刨根问底",
    "人物": "今天载了位了不得的人物",
    "特稿": "不停留在表面",
    "视界": "一览众山小",
    "光阴": "不忘初心，继续前进",
    "姿势": "干货、湿货、杂货，老司机带你涨姿势",
    "言己": "说出你的故事",
    "又见": "如果在异乡，一个旅人",
    "雕龙": "操千曲而后晓声，观千剑而后识器",
    "评论": "条条大路，众生喧哗",
    "摄影": "我为了把你拍得更漂亮嘛～",
    "图说": "边走边看",
    "机动": "说走就走，想停就停；可以跑高速，亦可钻胡同",
    "现场": "一车载你直达热点",
    "对话": "听见你的声音",
    "纪念": "为了未来，收藏过去",
    "节日": "今天应该很高兴",
    "新年献词": "新时代，新青年",
    # "翻译": "null",
})

def init_utoken_map():

    global utoken_map

    if utoken_map is not None:
        return

    utoken_map = RedisAutoExpiredMap(
        namespace=current_app.config['CACHE_KEY_PREFIX'] + "miniapp_utk",
        expires=UTOKEN_EXPIRES,
    )

def generate_utoken(openid, session_key):
    return xMD5("%s:%s:%s" % (openid, session_key, int(time.time() * 1000)))

def get_range(page, size):
    page = max(page, 1)
    return ((page - 1) * size, page * size)


def verify_utoken(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        init_utoken_map()

        utoken = get_str_field('utoken')
        openid = utoken_map[utoken]

        if openid is None:
            raise MiniappUnauthorized("Invalid utoken")

        g.openid = u(openid)

        ret = func(*args, **kwargs)

        return ret
    return wrapper


@bpMiniapp.route('/', methods=["GET","POST"])
def root():
    abort(404)


@bpMiniapp.route('/login', methods=["POST"])
def login():
    """
    Method   POST
    JSON:
        - js_code              str
    Return:
        - errcode              int
        - utoken               str
        - setting              dict
          - auto_change_card     bool
          - use_small_card       bool
        - config               dict

    """
    init_utoken_map()

    js_code = get_str_field('js_code')
    openid, session_key = jscode2session(js_code)

    utoken = generate_utoken(openid, session_key)
    utoken_map[utoken] = openid

    user = WxUser.query.get(openid)

    if user is None:
        user = WxUser(openid)
        db.session.add(user)
        db.session.commit()

    return {
        "errcode": 0,
        "utoken": utoken,
        "setting": {
            "auto_change_card": user.auto_change_card,
            "use_small_card": user.use_small_card,
        },
        "config": APP_CONFIG,
    }


@bpMiniapp.route('/get_col_desc', methods=["GET"])
@verify_utoken
def get_col_desc():
    """
    Method   GET
    Args:
        - utoken     str
    Return:
        - errcode    int
        - col_desc   [dict]
          - id         int
          - cover      str
          - title      str
          - desc       str
          - path       str

    """
    return {
        "errcode": 0,
        "col_desc": INDEX_COL_DESC,
    }


@bpMiniapp.route('/get_col_random', methods=["GET"])
@verify_utoken
def get_col_random():
    """
    Method   GET
    Args:
        - utoken     str
    Return:
        - errcode    int
        - articles   [dict]

    """
    openid = g.openid

    sbq1 = db.session.\
            query(Article.aid).\
            filter(Article.hidden == 0).\
            order_by(db.func.rand()).\
            limit(PAGE_SIZE).\
            subquery()

    sbq2 = WxUserArticle.query.\
            filter(WxUserArticle.openid == openid).\
            subquery()

    articles = db.session.\
            query(
                Article.aid,
                Article.appmsgid,
                Article.idx,
                Article.sn,
                Article.title,
                Article.masssend_time,
                Article.cover_url,
                Article.read_num,
                Article.like_num,
                Article.hidden,
                sbq2.c.ctime.label('star_time'),
            ).\
            join(sbq1, sbq1.c.aid == Article.aid).\
            outerjoin(sbq2, sbq2.c.aid == Article.aid).\
            all()

    return {
        "errcode": 0,
        "articles": [ a._asdict() for a in articles ]
    }


@bpMiniapp.route('/get_latest_articles', methods=["GET"])
@verify_utoken
def get_latest_articles():
    """
    Method   GET
    Args:
        - utoken    str
    Return:
        - errcode   int
        - articles  [dict]

    """
    openid = g.openid

    sbq = db.session.\
            query(Article.aid).\
            filter(Article.hidden == 0).\
            order_by(Article.masssend_time.desc()).\
            limit(PAGE_SIZE).\
            subquery()

    articles = db.session.\
            query(
                Article.aid,
                Article.appmsgid,
                Article.idx,
                Article.sn,
                Article.title,
                Article.read_num,
                Article.like_num,
                Article.masssend_time,
                Article.cover_url
            ).\
            join(sbq, sbq.c.aid == Article.aid).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            all()

    return {
        "errcode": 0,
        "articles": [ a._asdict() for a in articles ]
    }


@bpMiniapp.route('/get_col_hot', methods=["GET"])
@verify_utoken
def get_col_hot():
    """
    Method   GET
    Args:
        - utoken    str
        - page      int
    Return:
        - errcode   int
        - articles  [dict]

    """
    openid = g.openid
    page = get_int_field('page')
    st, ed = get_range(page, PAGE_SIZE)

    sbq1 = db.session.\
            query(Article.aid).\
            filter(Article.hidden == 0).\
            order_by(
                Article.read_num.desc(),
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            slice(st, ed).\
            subquery()

    sbq2 = WxUserArticle.query.\
            filter(WxUserArticle.openid == openid).\
            subquery()

    articles = db.session.\
            query(
                Article.aid,
                Article.appmsgid,
                Article.idx,
                Article.sn,
                Article.title,
                Article.masssend_time,
                Article.cover_url,
                Article.read_num,
                Article.like_num,
                Article.hidden,
                sbq2.c.ctime.label('star_time'),
            ).\
            join(sbq1, sbq1.c.aid == Article.aid).\
            outerjoin(sbq2, sbq2.c.aid == Article.aid).\
            order_by(
                Article.read_num.desc(),
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            all()

    return {
        "errcode": 0,
        "articles": [ a._asdict() for a in articles ]
    }


@bpMiniapp.route('/get_column_list', methods=["GET"])
@verify_utoken
def get_column_list():
    """
    Method   GET
    Args:
        - utoken          str
    Return:
        - errcode         int
        - columns         [dict]
          - id              int
          - title           str
          - desc            str
          - cover           str
          - article_count   int

    """
    columns = list(COLUMNS_LIST.keys())

    rlist = db.session.\
            query(
                Article.column,
                db.func.count(Article.aid).label('count'),
            ).\
            filter(Article.hidden == 0).\
            filter(Article.column.in_(columns)).\
            group_by(Article.column).\
            all()

    counter = { r.column: r.count for r in rlist }

    return {
        "errcode": 0,
        "columns": [
            {
                "id": ix,
                "title": title,
                "desc": desc,
                "cover": "%s.jpg" % ''.join(lazy_pinyin(title)),
                "article_count": counter.get(title, 0),
            }
            for ix, (title, desc) in enumerate(COLUMNS_LIST.items())
        ],
    }


@bpMiniapp.route('/get_column_articles', methods=["GET"])
@verify_utoken
def get_column_articles():
    """
    Method   GET
    Args:
        - utoken    str
        - column    str
        - page      int    if page == 0, return all articles in this column
    Return:
        - errcode   int
        - articles  [dict]

    """
    openid = g.openid
    column = get_str_field('column', limited=COLUMNS_LIST)
    page = get_int_field('page')

    sbq1 = db.session.\
            query(Article.aid).\
            filter(Article.hidden == 0).\
            filter(Article.column == column).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            )

    if page != 0:
        st, ed = get_range(page, PAGE_SIZE)
        sbq1 = sbq1.slice(st, ed)

    sbq1 = sbq1.subquery()

    sbq2 = WxUserArticle.query.\
            filter(WxUserArticle.openid == openid).\
            subquery()

    articles = db.session.\
            query(
                Article.aid,
                Article.appmsgid,
                Article.idx,
                Article.sn,
                Article.title,
                Article.masssend_time,
                Article.cover_url,
                Article.read_num,
                Article.like_num,
                Article.hidden,
                sbq2.c.ctime.label('star_time'),
            ).\
            join(sbq1, sbq1.c.aid == Article.aid).\
            outerjoin(sbq2, sbq2.c.aid == Article.aid).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            all()

    return {
        "errcode": 0,
        "articles": [ a._asdict() for a in articles ]
    }


@bpMiniapp.route('/get_date_range', methods=["GET"])
@verify_utoken
def get_date_range():
    """
    Method   GET
    Args:
        - utoken   str

    """
    rlist = db.session.\
            query(
                db.func.min(Article.masssend_time),
                db.func.max(Article.masssend_time)
            ).\
            first()

    st, ed = map(lambda t: time.strftime("%Y-%m-%d", time.localtime(t)), rlist)

    return {
        "errcode": 0,
        "range": {
            "start": st,
            "end": ed,
        }
    }


@bpMiniapp.route('/search_reporters', methods=["GET"])
@verify_utoken
def search_reporters():
    """
    Method   GET
    Args:
        - utoken     str
        - keyword    str
    Return:
        - errcode    int
        - reporters  [dict]
          - name       str
          - articles   [int]

    """
    keyword = get_str_field("keyword")

    names = [ name.strip() for name in keyword.split() if len(name.strip()) > 0 ]

    sbq = db.session.\
            query(Article.aid).\
            filter(Article.hidden == 0).\
            subquery()

    reporters = db.session.\
            query(
                Reporter.name,
                db.func.count(sbq.c.aid).label('article_count'),
            ).\
            join(ArticleReporter, ArticleReporter.rid == Reporter.rid).\
            join(sbq, sbq.c.aid == ArticleReporter.aid).\
            filter(Reporter.name.in_(names)).\
            group_by(Reporter.rid).\
            order_by(db.desc('article_count')).\
            all()

    return {
        "errcode": 0,
        "reporters": [ r._asdict() for r in reporters ],
    }


@bpMiniapp.route('/get_reporter_articles', methods=["GET"])
@verify_utoken
def get_reporter_articles():
    """
    Method   GET
    Args:
        - utoken    str
        - name      str
        - page      int    if page == 0, return all articles in this column
    Return:
        - errcode   int
        - articles  [dict]

    """
    openid = g.openid
    name = get_str_field('name')
    page = get_int_field('page')

    sbq1 = db.session.\
            query(Article.aid).\
            join(ArticleReporter, ArticleReporter.aid == Article.aid).\
            join(Reporter, Reporter.rid == ArticleReporter.rid).\
            filter(Reporter.name == name).\
            filter(Article.hidden == 0).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            )

    if page != 0:
        st, ed = get_range(page, PAGE_SIZE)
        sbq1 = sbq1.slice(st, ed)

    sbq1 = sbq1.subquery()

    sbq2 = WxUserArticle.query.\
            filter(WxUserArticle.openid == openid).\
            subquery()

    articles = db.session.\
            query(
                Article.aid,
                Article.appmsgid,
                Article.idx,
                Article.sn,
                Article.title,
                Article.masssend_time,
                Article.cover_url,
                Article.read_num,
                Article.like_num,
                Article.hidden,
                sbq2.c.ctime.label('star_time'),
            ).\
            join(sbq1, sbq1.c.aid == Article.aid).\
            outerjoin(sbq2, sbq2.c.aid == Article.aid).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            all()

    return {
        "errcode": 0,
        "articles": [ a._asdict() for a in articles ],
    }


@bpMiniapp.route('/search_articles_by_date', methods=["GET"])
@verify_utoken
def search_articles_by_date():
    """
    Method   GET
    Args:
        - utoken    str
        - date      str
        - level     str   options: ('month','day')
    Return:
        - errcode   int
        - articles  [dict]

    """
    openid = g.openid
    date = get_str_field('date')
    level = get_str_field('level', limited=['month','day'])

    try:
        dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError as e:
        raise RequestArgumentError("Invalid date %s" % date)

    if level == 'month':
        st = datetime.datetime(dt.year, dt.month, 1)
        span = calendar.monthrange(dt.year, dt.month)[1]
    else:
        st = dt
        span = 1

    ed = st + datetime.timedelta(span)
    st, ed = map(lambda dt: int(dt.timestamp()), [st, ed])

    sbq1 = db.session.\
            query(Article.aid).\
            filter(Article.hidden == 0).\
            filter(Article.masssend_time.between(st, ed)).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            subquery()

    sbq2 = WxUserArticle.query.\
            filter(WxUserArticle.openid == openid).\
            subquery()

    articles = db.session.\
            query(
                Article.aid,
                Article.appmsgid,
                Article.idx,
                Article.sn,
                Article.title,
                Article.masssend_time,
                Article.cover_url,
                Article.read_num,
                Article.like_num,
                Article.hidden,
                sbq2.c.ctime.label('star_time'),
            ).\
            join(sbq1, sbq1.c.aid == Article.aid).\
            outerjoin(sbq2, sbq2.c.aid == Article.aid).\
            order_by(
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            all()

    return {
        "errcode": 0,
        "articles": [ a._asdict() for a in articles ],
    }


@bpMiniapp.route('/search_articles_by_keyword', methods=["GET"])
@verify_utoken
def search_articles_by_keyword():
    """
    Method   GET
    Args:
        - utoken    str
        - keyword   str
        - filter    str   options: ('all','favorite')/column/reporter
        - page      int
    Return:
        - errcode   int
        - articles  [dict]

    """
    openid = g.openid
    keyword = get_str_field('keyword')
    ft = get_str_field('filter')
    page = get_int_field('page')
    st, ed = get_range(page, PAGE_SIZE)

    sbq1 = db.session.\
            query(
                Article.aid,
                db.fts_match(
                    Article.ix_text,
                    keyword,
                    db.fts_match.BOOLEAN
                ).label('score')
            )

    if ft == 'all':
        pass

    elif ft == 'favorite':
        sbq1 = sbq1.\
            join(WxUserArticle).\
            filter(WxUserArticle.openid == openid)

    elif ft in COLUMNS_LIST:
        sbq1 = sbq1.\
            filter(Article.column == ft)

    else:
        sbq1 = sbq1.\
            join(ArticleReporter, ArticleReporter.aid == Article.aid).\
            join(Reporter, Reporter.rid == ArticleReporter.rid).\
            filter(Reporter.name == ft)

    sbq1 = sbq1.\
            filter(Article.hidden == 0).\
            order_by(
                db.desc('score'),
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            slice(st, ed).\
            subquery()

    sbq2 = WxUserArticle.query.\
            filter(WxUserArticle.openid == openid).\
            subquery()

    articles = db.session.\
            query(
                Article.aid,
                Article.appmsgid,
                Article.idx,
                Article.sn,
                Article.title,
                Article.masssend_time,
                Article.cover_url,
                Article.read_num,
                Article.like_num,
                Article.hidden,
                sbq2.c.ctime.label('star_time'),
            ).\
            join(sbq1, sbq1.c.aid == Article.aid).\
            outerjoin(sbq2, sbq2.c.aid == Article.aid).\
            order_by(
                sbq1.c.score.desc(),
                Article.masssend_time.desc(),
                Article.idx.asc(),
            ).\
            all()

    return {
        "errcode": 0,
        "articles": [ a._asdict() for a in articles ]
    }


@bpMiniapp.route('/get_starred_articles', methods=["GET"])
@verify_utoken
def get_starred_articles():
    """
    Method   GET
    Args:
        - utoken   str
        - page     int

    """
    openid = g.openid
    page = get_int_field('page')

    sbq = db.session.\
        query(
            Article.aid,
            WxUserArticle.ctime,
        ).\
        join(WxUserArticle).\
        filter(WxUserArticle.openid == openid).\
        filter(Article.hidden == 0).\
        order_by(WxUserArticle.ctime.desc())

    if page != 0:
        st, ed = get_range(page, PAGE_SIZE)
        sbq = sbq.slice(st, ed)

    sbq = sbq.subquery()

    articles = db.session.\
            query(
                Article.aid,
                Article.appmsgid,
                Article.idx,
                Article.sn,
                Article.title,
                Article.masssend_time,
                Article.cover_url,
                Article.read_num,
                Article.like_num,
                Article.hidden,
                sbq.c.ctime.label('star_time'),
            ).\
            join(sbq, sbq.c.aid == Article.aid).\
            order_by(db.desc('star_time')).\
            all()

    return {
        "errcode": 0,
        "articles": [ a._asdict() for a in articles ]
    }


@bpMiniapp.route('/star_article', methods=["POST"])
@verify_utoken
def star_article():
    """
    Method   POST
    JSON:
        - utoken   str
        - aid      int
        - action   str   options: ('star','unstar')
    Return:
        - errcode  int

    """
    openid = g.openid
    aid = get_int_field('aid')
    action = get_str_field('action', limited=['star','unstar'])

    ret = db.session.\
            query(Article.aid).\
            filter(Article.hidden == 0).\
            filter(Article.aid == aid).\
            first()

    if ret is None:
        raise RequestArgumentError("Article %d was not found" % aid)

    ua = WxUserArticle.query.\
            filter(WxUserArticle.aid == aid).\
            filter(WxUserArticle.openid == openid).\
            first()

    if action == 'star' and ua is None:
        ua = WxUserArticle(openid, aid)
        db.session.add(ua)
        db.session.commit()

    if action == 'unstar' and ua is not None:
        db.session.delete(ua)
        db.session.commit()

    return {
        "errcode": 0
    }


@bpMiniapp.route('/change_setting', methods=["POST"])
@verify_utoken
def change_setting():
    """
    Method   POST
    JSON:
        - utoken             str
        - key                str
        - value              bool
    Return:
        - errcode            int

    """
    openid = g.openid
    key = get_str_field('key')
    value = get_bool_field('value')

    user = WxUser.query.get(openid)

    if key == 'auto_change_card':
        user.auto_change_card = value
    elif key == 'use_small_card':
        user.use_small_card = value
    else:
        raise RequestArgumentError("Invalid setting key %s" % key)

    db.session.commit()

    return {
        "errcode": 0
    }
