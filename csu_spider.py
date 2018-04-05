#! -*- coding:utf-8 -*-
import urllib2
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
# 记录文件名 csv文件易扩展，文件格式 [标题,链接,日期]
record_file_name = "information.csv"
# 记录错误的文件名
error_file_name = "error_log.csv"


def get_page_url(total_page, current_page, item_per_page):
    """
    拼接带访问网页的url
    :param total_page: 总页数
    :param current_page: 当前页数
    :param item_per_page: 每页的新闻条数
    :return: 通过参数拼接出的网页的url
    """
    return "http://software.csu.edu.cn/ejlby.jsp?a6t=%s&a6p=%s&a6c=%s&urltype=tree.TreeTempUrl&wbtreeid=1072" % (total_page, current_page, item_per_page)


def request_page(url):
    """
    请求url并获得返回response
    :param url: 待访问url
    :return: 请求url获得的response对象
    """
    request = urllib2.Request(url, headers=header)
    return urllib2.urlopen(request)


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
    :return:
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
        information['title'] = str(item_a[0].get('title'))
        information['url'] = str(item_a[0].get('href'))
        information['date'] = str(item.select('.timestyle18130')[0].string.strip())
        informations.append(information)
    try:
        record_file = open(record_file_name, 'a')
        for information in informations:
            item = "%s,%s%s,%s\n" % (information['title'], csu_host, information['url'], information['date'])
            record_file.write(item)
    except IOError:
        error_info = "%s, 文件写入错误: informations:[%s]\n" % (int(time.time()), ';'.join(informations))
        error_file = open(error_file_name, 'a')
        error_file.write(error_info)
        error_file.close()
        return error_info
    finally:
        record_file.close()
    return "ok"


