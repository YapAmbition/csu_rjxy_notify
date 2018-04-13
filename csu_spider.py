#! -*- coding:utf-8 -*-
#!/usr/bin/python
import urllib2
import re
from bs4 import BeautifulSoup
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# a6t => 总页数 (非强依赖)
# a6p => 当前页数 (强依赖)
# a6c => 每页有几条 (强依赖)
a6t = 70
a6p = 1
a6c = 10

# 待爬取网页host
csu_host = "http://software.csu.edu.cn/"
# 浏览器代理
header = {"User-Agent": "Mozzila/5.0(compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;"}


def get_page_url(total_page, current_page, item_per_page):
    """
    拼接带访问网页的url
    :param total_page: 总页数
    :param current_page: 当前页数
    :param item_per_page: 每页的新闻条数
    :return: 通过参数拼接出的网页的url
    """
    return "http://software.csu.edu.cn/ejlby.jsp?a6t=%s&a6p=%s&a6c=%s&urltype=tree.TreeTempUrl&wbtreeid=1072" % (total_page, current_page, item_per_page)


def request_page(url, retry=0):
    """
    请求url并获得返回response
    :param url: 待访问url
    :return: 请求url获得的response对象
    """
    if retry >= 3: return None
    request = urllib2.Request(url, headers=header)
    try:
        response = urllib2.urlopen(request)
        return response
    except Exception, e:
        print "open url error:[%s]" % str(e)
        request_page(url, retry+1)


def decode_response(response):
    """
    将请求url返回的response解析为html
    :param response: 请求url返回的response
    :return: html string
    """
    return response.read()


def handle_html(html):
    """
    从html中获得通知信息
    :param html: html string
    :return: [{'title': ,'url':, 'date':}]
    """
    soup = BeautifulSoup(html, "lxml")
    root_table = soup.select('.winstyle18130')[0]
    item_list = root_table.select('tr')
    informations = []
    for item in item_list:
        item_a = item.select('a')
        if len(item_a) == 0:  # 还有一个分割线得去掉
            continue
        item_date = item.select('.timestyle18130')
        if len(item_date) == 0:  # 最后一行页码得去掉
            continue
        information = dict()
        information['title'] = str(item_a[0].get('title')).decode("utf-8")
        information['url'] = (csu_host + str(item_a[0].get('href'))).decode("utf-8")
        information['date'] = str(item.select('.timestyle18130')[0].string.strip()).decode("utf-8")
        informations.append(information)
    return informations


def spider_csu_rjxy_total_page():
    """
    通过正则表达式获得总页数
    :return:
    """
    url = get_page_url(1, 1, 10)
    response = request_page(url)
    if response is None: return 100
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    root_table = soup.select('.winstyle18130')[0]
    page_table = root_table.select("tr")[-1]
    a_list = page_table.select("a")
    href_str = a_list[0]['href']
    re_list = re.findall(r".*a6t=(\d*)&*", href_str)
    if len(re_list) > 0: return int(re_list[0])
    return 100


def spider_csu_rjxy_notify(total_page, current_page, count_per_page=10, callback=None, delay=0.5, black_list=[]):
    """
    爬取某页通知
    :param total_page: 总页数，不需要准确，传1即可
    :param current_page: 当前页数，需要准确
    :param count_per_page: 每页有几条，默认10条
    :param callback: 爬取一页后的回调函数
    :param delay: 爬虫延时时间，默认为0.5秒，如果不延时会导致ip被封
    :param black_list 黑名单,如果爬取的url被包含在黑名单中则不爬取
    :return:
    """
    url = get_page_url(total_page, current_page, count_per_page)
    response = request_page(url)
    if response is None: return None
    html = decode_response(response)
    result = handle_html(html)
    if callback is not None: result = callback(result, black_list)
    time.sleep(delay)
    return result
