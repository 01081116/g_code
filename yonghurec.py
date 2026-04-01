# coding = utf-8

# 基于用户的协同过滤推荐算法实现
import csv
import random

import joblib
import numpy as np
import pandas as pd
import pymysql
import math
from operator import itemgetter

from build_model.predict import predict
import warnings

from route.util import until

warnings.filterwarnings("ignore")


class Yonghurec():
    def __init__(self):
        self.n_sim_user = 5
        self.n_rec_music = 4
        self.trainSet = {}
        self.testSet = {}
        self.user_sim_matrix = {}
        self.music_count = 0

    # 读文件，返回文件的每一行
    def load_file(self, filename):
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i == 0:  # 去掉文件第一行的title
                    continue
                yield line.strip('\r\n')
        print('Load %s success!' % filename)

    # 计算用户之间的相似度
    def calc_user_sim(self):
        # 构建“商品-用户”倒排索引
        music_user = {}
        for user, musics in self.trainSet.items():
            for music in musics:
                if music not in music_user:
                    music_user[music] = set()
                music_user[music].add(user)
        self.music_count = len(music_user)
        for music, users in music_user.items():
            for u in users:
                for v in users:
                    if u == v:
                        continue
                    self.user_sim_matrix.setdefault(u, {})
                    self.user_sim_matrix[u].setdefault(v, 0)
                    self.user_sim_matrix[u][v] += 1
        for u, related_users in self.user_sim_matrix.items():
            for v, count in related_users.items():
                self.user_sim_matrix[u][v] = count / math.sqrt(len(self.trainSet[u]) * len(self.trainSet[v]))

    # 读文件得到“用户-商品”数据
    def get_dataset(self, filename, pivot=0.75):
        trainSet_len = 0
        testSet_len = 0
        for line in self.load_file(filename):
            user, music, rating = line.split(',')
            self.trainSet.setdefault(user, {})
            self.trainSet[user][music] = rating
            trainSet_len += 1

    # 针对目标用户U，找到其最相似的K个用户，产生N个推荐
    def recommend(self, user):
        K = self.n_sim_user
        N = self.n_rec_music
        rank = {}
        watched_musics = self.trainSet[user]
        for v, wuv in sorted(self.user_sim_matrix[user].items(), key=itemgetter(1), reverse=True)[0:K]:
            for music in self.trainSet[v]:
                if music in watched_musics:
                    continue
                rank.setdefault(music, 0)
                rank[music] += wuv
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]

    def evaluate(self):
        print("Evaluation start ...")
        N = self.n_rec_music
        # 准确率和召回率
        hit = 0
        rec_count = 0
        test_count = 0
        # 覆盖率
        all_rec_musics = set()

        # # 清空 rec 表
        # sql1 = "truncate table rec;"
        # until.insert(sql1)

        # 插入推荐结果
        for i, user in enumerate(self.trainSet):
            test_musics = self.testSet.get(user, {})
            rec_musics = self.recommend(user)
            print(user, rec_musics)

            # 逐条插入推荐结果
            for item in rec_musics:
                music_id, score = item
                sql = f"insert into rec(user_id, music_id, score) values ({user}, {music_id}, {score})"
                until.insert(sql)

            # 计算指标
            for music, w in rec_musics:
                if music in test_musics:
                    hit += 1
                all_rec_musics.add(music)
            rec_count += N
            test_count += len(test_musics)

        # # 计算并打印评估指标
        # precision = hit / (1.0 * rec_count)
        # recall = hit / (1.0 * test_count)
        # coverage = len(all_rec_musics) / (1.0 * self.music_count)
        # print(f"Precision: {precision}, Recall: {recall}, Coverage: {coverage}")


def do_lstm():
    """对数据库中comment_res=3的评论进行情感分析"""
    # 连接到数据库
    con, cur = until.coon()

    # 查询待分析的评论（comment_res=3表示未分析）
    sql = "SELECT * FROM music_comment WHERE comment_res=3"
    df = pd.read_sql(sql, con)
    
    if df.empty:
        print("没有待分析的评论")
        return
    
    print(f"共有 {len(df)} 条评论待分析")

    # 对每条评论进行情感分析
    for index, row in df.iterrows():
        sentiment, score = predict(row['content'])
        # score范围是0-1，正面接近1，负面接近0
        print(f"评论: {row['content'][:20]}... -> 情感: {'正面' if sentiment == 1 else '负面'}, 得分: {score:.4f}")
        
        # 更新数据库中的情感得分
        sql_update = f"UPDATE music_comment SET comment_res = {score} WHERE id = {row['id']};"
        until.insert(sql_update)
    
    print("情感分析完成")



if __name__ == '__main__':
    do_lstm()
    db = pymysql.connect(host='localhost', user='root', password='123456', database='lstm_music_rec',
                         charset='utf8')
    cursor = db.cursor()
    # 使用 execute()  方法执行 SQL 查询
    sql = "select * from music_comment"
    data = until.qurey(sql)

    with open('rating.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['userId', 'musicId', 'rating'])
        for item in data:
            writer.writerow([item[1], item[2], float(item[5])])
    rating_file = 'rating.csv'

    cursor.close()
    db.close()
    yognhurec = Yonghurec()
    yognhurec.get_dataset(rating_file)
    yognhurec.calc_user_sim()
    yognhurec.evaluate()
