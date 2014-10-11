#!/usr/bin/python
# -*- coding=utf-8 -*-

"""数据采集
"""

__author__ = ['"wuyadong" <wuyadong311521@gmail.com>']

import daily
import model


def fetch_before(date_str):
	zh = daily.ZhiHu()
	dao = model.Dao()
	try:
		# 获取最新的news_id列表
		latest_news = zh.get_before_news(date_str)
		news_ids = _extract_news_ids(latest_news)
		date_str = _extract_date_str(latest_news)

		# 找出数据库中没有的news_id列表
		not_exists_news_ids = []
		for news_id in news_ids:
			if not dao.exist(news_id):
				not_exists_news_ids.append(news_id)

		# 获取news, 并保存到数据库
		for news_id in not_exists_news_ids:
			news = zh.get_news(news_id)
			dao.insert(date_str, news)
	finally:
		dao.close()


def fetch_latest():
	zh = daily.ZhiHu()
	dao = model.Dao()

	try:
		# 获取最新的news_id列表
		latest_news = zh.get_latest_news()
		news_ids = _extract_news_ids(latest_news)
		date_str = _extract_date_str(latest_news)

		# 找出数据库中没有的news_id列表
		not_exists_news_ids = []
		for news_id in news_ids:
			if not dao.exist(news_id):
				not_exists_news_ids.append(news_id)

		# 获取news, 并保存到数据库
		for news_id in not_exists_news_ids:
			news = zh.get_news(news_id)
			dao.insert(date_str, news)
	finally:
		dao.close()


def _extract_news_ids(latest_news):
	"""提取出最新的news_ids

	:param latest_news:
	:return:
	"""
	news_ids = []

	stories = latest_news['stories']
	for story in stories:
		print story['id'], story['title']
		news_ids.append(story['id'])

	return news_ids


def _extract_date_str(latest_news):
	"""提取出最新的日期

	:param latest_news:
	:return:
	"""
	return latest_news['date']


if __name__ == "__main__":
	fetch_latest()