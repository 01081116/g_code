import random
from datetime import datetime
import pymysql

# 用户与音乐的相关性范围
user_music_range = {
   1: (1, 200),
    2: (201, 400),
    4: (401, 600),
    5: (601, 800),
    6: (801, 1000),
}

# 评论模板
comment_templates = [
    "这首歌太棒了！",
    "非常喜欢这个旋律！",
    "歌词写得很好！",
    "听了让人心情愉悦！",
    "推荐给大家！"
]

# 生成评论数据
def generate_comments():
    comments = []
    shared_music = set()  # 用于存储被多个用户评论的音乐

    # 生成共享音乐（每个共享音乐被 2-3 个用户评论）
    for _ in range(20):  # 生成 10 首共享音乐
        music_id = random.randint(1, 1000)
        shared_music.add(music_id)

    # 为每个用户生成评论
    for user_id, music_range in user_music_range.items():
        # 生成 5 条评论在用户的相关范围内
        for _ in range(5):
            music_id = random.randint(music_range[0], music_range[1])
            content = random.choice(comment_templates)
            create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            comment_res = 3
            comments.append((user_id, music_id, content, create_time, comment_res))

        # 生成 5 条评论在共享音乐中
        for music_id in random.sample(shared_music, 5):
            content = random.choice(comment_templates)
            create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            comment_res = 3
            comments.append((user_id, music_id, content, create_time, comment_res))

    return comments

# 将评论数据写入 MySQL 数据库
def write_to_mysql(comments):
    # 数据库连接配置
    db_config = {
        'host': 'localhost',  # 数据库地址
        'user': 'root',       # 数据库用户名
        'password': '123456', # 数据库密码
        'database': 'lstm_music_rec',  # 数据库名称
        'charset': 'utf8mb4'
    }

    # 连接数据库
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    try:
        # 插入评论数据
        sql = '''
        INSERT INTO music_comment (user_id, music_id, content, create_time, comment_res)
        VALUES (%s, %s, %s, %s, %s)
        '''
        cursor.executemany(sql, comments)
        connection.commit()
        print("数据插入成功！")
    except Exception as e:
        print(f"数据插入失败: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

# 生成 50 条评论数据
comments = generate_comments()

# 将数据写入 MySQL 数据库
write_to_mysql(comments)
