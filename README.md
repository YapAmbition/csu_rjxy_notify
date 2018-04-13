获得CSU软件学院通知的爬虫
===

###使用方法：

* 在mysql数据库中执行csu_rjxy_notify.sql中的sql(创建数据库)
* 在index.py中配置自己的mysql数据库
* 运行index.py

#### 2018-04-12
由于院网展示有置顶项,通知不是按顺序展示在院网的,所以不能按照原来的逻辑判断是否重复

#### 2018-04-13
需要在index.py开头添加#!/usr/bin/python,否则在使用crontab执行时并不会执行python脚本