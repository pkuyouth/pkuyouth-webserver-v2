#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: receive.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth

from lxml import etree

def parse_message(xml):

    tree = etree.fromstring(xml)
    message_type = tree.find('MsgType').text

    if message_type == 'text':
           return TextMessage(tree)
    elif message_type == 'image':
        return ImageMessage(tree)
    elif message_type == 'event':
        event_type = tree.find('Event').text
        if event_type == 'subscribe':
            return FollowEvent(tree)
        elif event_type == 'unsubscribe':
            return UnFollowEvent(tree)
        elif event_type in ('CLICK',):
            return MeauEvent(tree)
        else:
            return xml
    else:
        return xml


class XMLMessage(object):

    keys = []

    def __init__(self, tree):
        self._tree = tree
        self.__dict__.update({
            k: self._tree.find(k).text for k in self.__class__.keys
        })

    @property
    def xml(self):
        return etree.tostring(self._tree, encoding='utf-8').decode('utf-8')

    def __str__(self):
        return self.xml


class Message(XMLMessage):

    keys = ['ToUserName','FromUserName','CreateTime','MsgType','MsgId']

class TextMessage(Message):

    keys = Message.keys + ['Content']

class ImageMessage(Message):

    keys = Message.keys + ['PicUrl','MediaId']

class Event(XMLMessage):

    keys = ['ToUserName','FromUserName','CreateTime','MsgType','Event','EventKey']

class FollowEvent(Event):

    pass

class UnFollowEvent(Event):

    pass

class MeauEvent(Event):

    pass
