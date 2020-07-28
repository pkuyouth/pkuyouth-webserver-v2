#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------
# Project: PKUYouth Webserver v2
# File: text.py
# Created Date: 2020-07-27
# Author: Xinghong Zhong
# ---------------------------------------
# Copyright (c) 2020 PKUYouth


Q_INTRO = '''欢迎使用北青号内Q搜索！

$ 使用方法及示例:
(1) q [YYMM] 返回当月文章列表。
>>> q 1804

(2) q [YYMMDD] 返回当日文章。
>>> q 180308

(3) q [keywords] 关键词搜索，BOOLEAN 逻辑
>>> q 三角地
>>> q 跑步 打卡 (跑步 OR 打卡)
>>> q +石林 +十佳 (石林 AND 十佳)
>>> q +维权 -施工 (维权 AND (NOT 施工))

(4) q [index] 返回列表中的指定文章
>>> q 生日
    (1) xxxx
    (2) xxxx
    (3) xxxx
    ......
>>> q 1
    返回文章 (1)
>>> q 2
    返回文章 (2)

$ 小贴士:
(1) q 与 Q 等价，即 Q yymm 与 q yymm 均正确。
(2) q 后可无空格，即 q1804 与 q 1804 均正确。'''


WELCOME = '欢迎关注北大青年！点击下方菜单栏，可以查看不同栏目的文章精选哟~'


INVALID_DATE = "日期非法"


NO_ARTICLE_ON_THIS_DAY = "当日没有发文"


NO_ARTICLE_IN_THIS_MONTH = "当月没有发文"


NO_ARTICLE_MATCHED = "搜索结果为空"


INDEX_OUT_OF_RANGE = "文章索引超出范围"


COLUMNS_INTRO = '''点击栏目名称查看栏目精选！
<a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=6">调查</a> <a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=13">视界</a> <a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=5">特稿</a>
<a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=12">光阴</a> <a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=7">人物</a> <a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=11">姿势</a> <a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=10">机动</a>
<a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=2">摄影</a> <a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=3">言己</a> <a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=4">雕龙</a> <a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=9">又见</a> <a href="https://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzAzMDEyNg==&scene=18&hid=8">评论</a>'''


ABOUT_US = '''《北大青年》是共青团北京大学委员会机关报，创刊于1998年10月25日，由季羡林先生题写刊名。从纸质报刊到数字媒体，从传播信息到声发洞见，《北大青年》自诞生以来不断求新求变、聚焦燕园、环顾社会、记录伟大、尊重平凡，以北大精神关怀世界，以青年赤诚注解时代。

目前，《北大青年》由调查、特稿、姿势、人物、视界、光阴、摄影、机动、副刊等栏目组成，以“我们的关注，我们的声音，我们的责任”为己任，关注身边人、聚焦燕园事，通过不同视角透射校园今昔人事，呈现青年的种种声音。'''


JOIN_US = '''欢迎报名加入北大青年！

填写<a href="https://www.wjx.cn/m/26587672.aspx">2018年秋季招新问卷</a>，加入我们一起干！'''


MAINTAINING = '该功能尚在维护'

