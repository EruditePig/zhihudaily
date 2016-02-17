#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = ['"wuyadong" <wuyadong311521@gmail.com>']

import logging
import base64
import config
from base.handler import BaseHandler
from utils.date_util import today_str
from crawl import zhihu
from crawl import fetch


class OperationHandler(BaseHandler):
    """后台操作的接口
    """

    def is_authenticated(self):
        auth_header = self.request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith("Basic"):
            return False

        auth_decoded = base64.decodestring(auth_header[6:])
        username, password = auth_decoded.split(":", 2)
        if username == config.username and password == config.password:
            return True

        return False

    def get(self, *args, **kwargs):
        # auth
        if not self.is_authenticated():
            self.set_status(401)
            self.set_header('WWW-Authenticate', "Basic realm=Restricted")
            self.finish()
        else:
            path = self.request.path
            try:
                if path == "/operation/fetch":
                    fetch_zhihu_daiy(self.request.arguments)
                elif path == "/operation/index":
                    index_zhihu_daily(self.request.arguments)
                else:
                    self.set_status(404)
                    self.write('{"code": 404, "msg": "no operation"}')
            except Exception as e:
                import traceback
                stack = traceback.format_exc()
                logging.error("operation error:%s\n%s" % (e, stack))
                self.set_status(500)
                self.write('{"code": 500, "msg": "%s"}' % str(e))
            else:
                self.set_status(200)
                self.write('{"code": 200, "msg": "success"}')


def fetch_zhihu_daiy(params):
    """下载最新的新闻（包括图片），并保存
    """
    zh = zhihu.ZhiHu()

    if 'date' not in params:
        latest_news = zh.get_latest_news()
    else:
        date_str = params['date'][0]
        latest_news = zh.get_before_news(date_str)

    # 获取最新的news_id列表
    latest_news_ids = fetch.extract_news_ids(latest_news)
    date_str = fetch.extract_date_str(latest_news)

    # 找出数据库中没有的news_id列表
    not_exists_news_ids = fetch.not_exists_news_ids(date_str, latest_news_ids)

    # 获取news和下载图片
    not_exists_news_ids.reverse()
    wait_for_store_news_list = fetch.fetch_news_list(not_exists_news_ids)

    # 保存图片
    wait_for_store_news_list = fetch.store_images(wait_for_store_news_list, date_str)

    # 保存news到数据库中
    fetch.store_news_list(wait_for_store_news_list)


def index_zhihu_daily(params):
    """建立索引
    """
    if 'date' not in params:
        date_str = today_str()
    else:
        date_str = params['date'][0]
    news_list = fetch.get_news_list(date_str)
    if news_list:
        fetch.index_news_list(news_list)