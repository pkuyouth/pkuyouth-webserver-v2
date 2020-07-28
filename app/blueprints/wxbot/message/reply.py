#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: reply.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

import time
from lxml import etree

def _build_xml(root, d):
    for k, v in d.items():
        e = etree.SubElement(root, k)
        if isinstance(v, (str, int, float)):
            e.text = etree.CDATA(str(v))
        elif isinstance(v, tuple):
            v, use_CDATA = v
            e.text = etree.CDATA(str(v)) if use_CDATA else str(v)
        elif isinstance(v, list):
            for child_d in v:
                _build_xml(e, child_d)
        elif isinstance(v, dict):
            child_d = v
            _build_xml(e, child_d)
        else:
            raise TypeError('unsupported type %s of value %r' %
                            (v.__class__.__name__, v))


class Message(object):

    message_type = None

    def __init__(self, to_user, from_user):
        self._tree = etree.Element('xml')
        self._update({
            'ToUserName': to_user,
            'FromUserName': from_user,
            'CreateTime': (int(time.time()), False),
            'MsgType': self.__class__.message_type,
        })

    @property
    def xml(self):
        return etree.tostring(self._tree, encoding='utf-8').decode('utf-8')

    def __str__(self):
        return self.xml

    def _update(self, d):
        _build_xml(self._tree, d)


class TextMessage(Message):

    message_type = 'text'

    def __init__(self, to_user, from_user, content):
        super().__init__(to_user, from_user)
        self._update({'Content': content})


class ArticleMessage(Message):

    message_type = 'news'

    def __init__(self, to_user, from_user, articles):
        super().__init__(to_user, from_user)
        self._update({
            'ArticleCount': ( len(articles), False ),
            'Articles': [
                {
                    'item': {
                        'Title': a.title if hasattr(a, 'title') else a['title'],
                        'Description': a.digest if hasattr(a, 'digest') else a['digest'],
                        'PicUrl': a.cover_url if hasattr(a, 'cover_url') else a['cover_url'],
                        'Url': a.content_url if hasattr(a, 'content_url') else a['content_url'],
                    }
                }
                for a in articles
            ]
        })
