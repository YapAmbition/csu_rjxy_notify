#!-*- coding:utf-8 -*-

import csu_spider
import MySQLdb

host = "localhost"
username = "root"
password = "954552106"
database = "csu_rjxy_notify"
table_name = "informations"

# 打开数据库，设置字符集，创建数据表
db = MySQLdb.connect(host, username, password, database, use_unicode=True, charset="utf8")
cursor = db.cursor()
create_table_sql = """
CREATE TABLE IF NOT EXISTS `%s` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '通知id',
  `title` varchar(255) DEFAULT NULL COMMENT '标题',
  `url` varchar(255) DEFAULT NULL COMMENT '文章url',
  `date` date DEFAULT NULL COMMENT '文章日期',
  `is_new` int(11) DEFAULT '1' COMMENT '是否是新的通知,只有是新的通知才会被扫描到,1表示新的通知,0表示旧的通知',
  PRIMARY KEY (`id`),
  KEY `index_is_new` (`is_new`) USING BTREE COMMENT '通常会用is_new字段查询通知'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""" % table_name
cursor.execute(create_table_sql)


# 将数据存入mysql的回调函数
def store_informations_in_mysql(informations, black_list=[]):
    """
    先获取黑名单,爬虫扫描时不需要扫描黑名单的东西
    回调函数,将爬取到的信息存入mysql
    :param informations: [{'title': ,'url':, 'date':}]
    :param black_list: 黑名单: ['xxx', 'xxx']
    :return:
    """
    for information in informations:
        if str(information['url']) in black_list: continue  # 如果要爬取的url在黑名单中,则不爬取
        select_sql = """select count(*) from %s where url = "%s" """ % (table_name.replace("'", "\\\'").replace('"', '\\\"'), information['url'].replace("'", "\\\'").replace('"', '\\\"'))
        cursor.execute(select_sql)
        is_repeat = cursor.fetchall()[0][0]
        if is_repeat > 0:  # 如果有重复则直接退出
            continue
        insert_sql = """insert into %s(`title`, `url`, `date`) values("%s", "%s", "%s")""" % (table_name.replace("'", "\\\'").replace('"', '\\\"'), information['title'].replace("'", "\\\'").replace('"', '\\\"'), information['url'].replace("'", "\\\'").replace('"', '\\\"'), information['date'].replace("'", "\\\'").replace('"', '\\\"'))
        try:
            cursor.execute(insert_sql)
            db.commit()
            print "insert success : %s" % information
        except Exception, e:
            print "except Exception: %s" % str(e)
            print "error, rollback: %s" % information
            db.rollback()


# 开始爬取通知
# 读取黑名单文件
blacklist = open('blacklist', 'r')
black_items = blacklist.readlines()
for i in range(0, len(black_items)): black_items[i] = black_items[i].strip()

total_page = csu_spider.spider_csu_rjxy_total_page()
for page in range(1, total_page + 1): csu_spider.spider_csu_rjxy_notify(1, page, callback=store_informations_in_mysql, delay=1, black_list=black_items)

# 关闭数据库链接
db.close()
# 关闭黑名单文件
blacklist.close()

