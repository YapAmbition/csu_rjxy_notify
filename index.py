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
def store_informations_in_mysql(informations):
    """
    回调函数,将爬取到的信息存入mysql
    :param informations: [{'title': ,'url':, 'date':}]
    :return:
    """
    for information in informations:
        select_sql = "select count(*) from %s where url = \'%s\'" % (table_name, information['url'])
        cursor.execute(select_sql)
        is_repeat = cursor.fetchall()[0][0]
        if is_repeat > 0:  # 如果有重复则直接退出
            print '已经更新到最新'
            return True
        insert_sql = "insert into %s(`title`, `url`, `date`) values(\"%s\", \"%s\", \"%s\")" % (table_name, information['title'], information['url'], information['date'])
        try:
            cursor.execute(insert_sql)
            db.commit()
            print "insert success : %s" % information
        except:
            print "error, rollback: %s" % information
            db.rollback()
    return False


# 开始爬取通知
for page in range(1, 200):
    is_finish = csu_spider.spider_csu_rjxy_notify(1, page, callback=store_informations_in_mysql, delay=1)
    if is_finish:
        break

# 关闭数据库链接
db.close()