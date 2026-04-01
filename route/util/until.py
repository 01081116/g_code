import pymysql
import pandas as pd
import numpy as np
from config import Config

def coon():
    con = pymysql.connect(host=Config.HOST, port=Config.PORT, user=Config.USER, password=Config.PASSWORD, db=Config.DATABASE,
                          charset=Config.CHARSET)  # 连接数据库
    cur = con.cursor()
    return con, cur


def close():
    con, cur = coon()  # 关闭数据库
    cur.close()
    con.close()


def qurey(sql):
    con, cur = coon()  # 查询数据库
    cur.execute(sql)
    res = cur.fetchall()
    close()
    return res


def insert(sql):
    con, cur = coon()  # 删除、修改数据库表
    cur.execute(sql)
    con.commit()
    close()


def data(name):
    sql = 'select * from rec order by rating desc'
    res = qurey(sql)
    b = []
    d = []
    for i in res:
        if name == i[1]:
            b.append(i[2])
    for i in b:
        sql = 'select `id`,`title`,`img_url` from mynew where `id` = ' + i + ''
        c = qurey(sql)
        d.append(c)
    return d

