#!-*- coding:utf-8 -*-

import csu_spider
import time


for a6p in range(1, 71):
    url = csu_spider.get_page_url(csu_spider.a6t, a6p, csu_spider.a6c)
    response = csu_spider.request_page(url)
    html = csu_spider.decode_response(response)
    result = csu_spider.handle_html(html)
    print a6p, " : ", result
    time.sleep(0.5)


