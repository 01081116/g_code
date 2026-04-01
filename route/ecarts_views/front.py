import csv
from datetime import datetime

import jieba
import pandas as pd
from flask import Blueprint, Flask, render_template, request, session, jsonify, flash, redirect, url_for, current_app
from models.admin_model import *
import math
import random

import pymysql
from crawl_model.wangyi import Wangyi
from models.music_category import Music_category, Category_muisc, Collect
from route.util import until
from yonghurec import do_lstm, Yonghurec

system = ''

front = Blueprint('front', __name__)

wy = Wangyi()
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    db='lstm_music_rec',
    charset='utf8'
)
cursor = conn.cursor()


# 登录页面
@front.route('/')
def login():
    return render_template("login.html")


@front.route('/dologin', methods=['POST'])
def dologin():
    username = request.form.get("username")
    password = request.form.get("password")

    # 使用参数化查询以避免SQL注入
    sql = f"SELECT * FROM user WHERE username = '{username}'"
    data = until.qurey(sql)

    if data and password == data[0][2]:  # 确保用户存在并且密码匹配
        session['uname'] = data[0][0]
        session['username'] = username

        # 设置闪存消息
        return jsonify({"status": True, "redirect": url_for('front.index')})  # 重定向到index页面
    else:
        return jsonify({"status": False})  # 登录失败


@front.route('/zhuce')
def zhuce():
    return render_template('zhuce.html')


@front.route('/dozhuce', methods=['POST'])
def dozhuce():
    username = request.form.get("username")
    password = request.form.get("password")
    phone = request.form.get("phone")  # 获取手机号
    email = request.form.get("email")  # 获取邮箱

    # 检查用户名是否已存在
    sql = f"SELECT username FROM user WHERE username ='{username}'"
    data = until.qurey(sql)

    if data:
        return jsonify({"status": False})  # 用户名已存在
    else:
        # 插入新用户信息
        sql = f"INSERT INTO user (username, password, phone, email) VALUES ('{username}','{password}','{phone}','{email}' )"
        until.insert(sql)
        return jsonify({"status": True})  # 注册成功


@front.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('front.login'))


@front.route('/changgeinfo')
def changgeinfo():
    uid = session.get('uname')
    sql = f"select * from user where id = {uid}"
    res = until.qurey(sql)
    print(res)
    return render_template('changeinfo.html', res=res)


@front.route('/updateinfo', methods=['POST'])
def updateinfo():
    uid = session.get('uname')  # 获取当前用户的 ID
    username = request.form.get('username')  # 获取表单中的用户名
    password = request.form.get('password')  # 获取表单中的密码
    phone = request.form.get('phone')  # 获取表单中的密码
    email = request.form.get('email')  # 获取表单中的密码

    # 更新用户信息
    sql = f"UPDATE user SET username = '{username}', password = '{password}',phone='{phone}',email='{email}' WHERE id = {uid}"
    until.insert(sql)

    return redirect(url_for('front.changgeinfo'))  # 重定向回修改页面


@front.route('/index')
def index():
    # 获取当前用户ID
    user_id = session['uname']
    print("当前用户ID:", user_id)

    # 根据用户推荐的歌曲（基于 rec 表的 score 字段）
    sql = f"""
    SELECT s.* 
    FROM songs s 
    JOIN rec r ON s.id = r.music_id 
    WHERE r.user_id = {user_id} 
    ORDER BY CAST(r.score AS DECIMAL) DESC 
    LIMIT 4
    """
    rec_data = list(until.qurey(sql))  # 将元组转换为列表
    print("推荐歌曲结果:", rec_data)

    # 如果推荐歌曲不足 4 条，补充随机歌曲
    if len(rec_data) < 4:
        sql_supplement = f"""
        SELECT * 
        FROM songs 
        WHERE id NOT IN (SELECT music_id FROM rec WHERE user_id = {user_id})
        ORDER BY RAND() 
        LIMIT {4 - len(rec_data)}
        """
        supplement_data = list(until.qurey(sql_supplement))
        rec_data.extend(supplement_data)  # 补充随机歌曲
        print("补充歌曲:", supplement_data)

    # 获取前4条数据----->流行指数
    sql02 = """
    SELECT id, song_name, singer_name, cover_url, COUNT(*) AS px 
    FROM songs 
    GROUP BY id, song_name, singer_name, cover_url 
    ORDER BY px DESC 
    LIMIT 4
    """
    datalist = list(until.qurey(sql02))
    new_data_list = [(data[0], data[1], data[2], data[3], index + 1) for index, data in enumerate(datalist)]

    # 获取第5条数据到第8条数据------>热歌
    sql03 = """
    SELECT id, song_name, singer_name, cover_url, popularity 
    FROM (
        SELECT id, song_name, singer_name, cover_url, popularity, COUNT(*) AS px 
        FROM songs 
        GROUP BY id, song_name, singer_name, cover_url, popularity 
        ORDER BY px DESC 
        LIMIT 12
    ) AS subquery 
    ORDER BY px DESC 
    LIMIT 4 OFFSET 4
    """
    datalist02 = list(until.qurey(sql03))
    new_data_list02 = [(data[0], data[1], data[2], data[3], data[4], index + 1) for index, data in enumerate(datalist02)]

    # 获取第9条数据到第12条数据----------->新歌
    sql04 = """
    SELECT id, song_name, singer_name, cover_url, popularity 
    FROM (
        SELECT id, song_name, singer_name, cover_url, popularity, COUNT(*) AS px 
        FROM songs 
        GROUP BY id, song_name, singer_name, cover_url, popularity 
        ORDER BY px DESC 
        LIMIT 16 OFFSET 8
    ) AS subquery 
    LIMIT 4
    """
    datalist03 = list(until.qurey(sql04))
    new_data_list03 = [(data[0], data[1], data[2], data[3], data[4], index + 1) for index, data in enumerate(datalist03)]

    # 获取第13条到第16条数据------->欧美歌曲
    sql05 = """
    SELECT id, song_name, singer_name, cover_url, popularity 
    FROM (
        SELECT id, song_name, singer_name, cover_url, popularity, COUNT(*) AS px 
        FROM songs 
        GROUP BY id, song_name, singer_name, cover_url, popularity 
        ORDER BY px DESC 
        LIMIT 16
    ) AS subquery 
    ORDER BY px DESC 
    LIMIT 4 OFFSET 12
    """
    datalist04 = list(until.qurey(sql05))
    new_data_list04 = [(data[0], data[1], data[2], data[3], data[4], index + 1) for index, data in enumerate(datalist04)]

    # 统计每个专辑出现的次数按照次数排序
    sql06 = """
    SELECT id, type, page, playlist_title, playlist_link, playlist_cover, play_count, author, gdid 
    FROM new_playlists 
    ORDER BY play_count DESC 
    LIMIT 12
    """
    datalist05 = list(until.qurey(sql06))

    return render_template('index.html', rec_data=rec_data, new_data_list=new_data_list,
                           new_data_list02=new_data_list02, new_data_list03=new_data_list03,
                           new_data_list04=new_data_list04, datalist05=datalist05)

def generate_rating_csv():
    sql = 'SELECT * FROM music_comment'
    data = until.qurey(sql)

    # 将数据写入 rating.csv
    with open('rating.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['userId', 'musicId', 'rating'])  # 写入表头
        for item in data:
            writer.writerow([item[1], item[2], float(item[5])])


@front.route('/rec', methods=['GET', 'POST'])
def rec():
    user_id = session.get('uname')
    sql = f"select id from music_comment where comment_res =3"
    res = until.qurey(sql)
    userbe = [i[0] for i in res]
    if len(userbe) == 0:
        return redirect('index')
    do_lstm()
    generate_rating_csv()
    yognhurec = Yonghurec()
    yognhurec.get_dataset('rating.csv')
    yognhurec.calc_user_sim()
    # 清空 rec 表
    sql1 = "delete from rec;"
    until.insert(sql1)
    yognhurec.evaluate()
    return redirect('index')


@front.route('/retry', methods=['POST'])
def retry():
    infos = 'None'
    song_id = request.json['id']
    print(song_id)
    url = wy.get_musicUrl(song_id)
    print(url)
    # if g.user:
    #     infos = history_add(song_id, 'None')
    lyrics = wy.get_lyric(song_id)
    return jsonify({'success': 200, 'url': url, 'infos': infos, 'lyrics': lyrics[0], 'tlyrics': lyrics[1]})


@front.route('/play', methods=['POST'])
def play():
    song_id = request.json['id']
    print(song_id)
    info = request.json['info']
    url = wy.get_musicUrl(song_id)
    print(url)
    lyrics = wy.get_lyric(song_id)
    print(lyrics)
    infos = 'None'
    # if g.user:
    #     infos = history_add(song_id, info)
    music = {
        'name': info['song'],
        'singer': info['singer'],
        'cover_url': info['cover'],
        'url': url,
        'lyrics': lyrics[0],
        'id': song_id,
        'tlyrics': lyrics[1]
    }
    return jsonify({'success': 200, 'song': music, 'infos': infos})


# 歌手排行
@front.route('/songer_list', methods=['GET', 'POST'])
def songer_list():
    user_id = session.get('uname')  # 获取用户ID（假设用户名作为ID）
    collected_songs = []

    # 获取用户收藏列表
    if user_id:
        retry_count = 3  # 设置重试次数
        for attempt in range(retry_count):
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT music_id FROM collect WHERE user_id=%s", (user_id,))
                    collected_songs = [row[0] for row in cursor.fetchall()]
                break  # 成功后退出循环
            except pymysql.err.OperationalError as e:
                if e.args[0] == 1412:
                    print(f"Attempt {attempt + 1} failed, retrying...")
                    continue  # 重试
                else:
                    raise  # 其他错误则抛出

    # 获取歌手列表
    with conn.cursor() as cursor:
        cursor.execute("SELECT DISTINCT singer_name FROM songs")
        artists = [row[0] for row in cursor.fetchall()]

        # 随机选择默认歌手
        default_artist = random.choice(artists) if artists else ''
        selected_artist = request.form.get('artist', default_artist)

        # 查询指定歌手的歌曲（带收藏状态）
        cursor.execute("""
            SELECT s.*, 
            CASE WHEN c.id IS NOT NULL THEN 1 ELSE 0 END as collected
            FROM songs s
            LEFT JOIN collect c ON s.id = c.music_id AND c.user_id=%s
            WHERE s.singer_name = %s 
            ORDER BY RAND() LIMIT 4
        """, (user_id, selected_artist))
        random_songs = cursor.fetchall()

        # 查询随机歌曲（带收藏状态）
        cursor.execute("""
            SELECT s.*,
            CASE WHEN c.id IS NOT NULL THEN 1 ELSE 0 END as collected
            FROM songs s
            LEFT JOIN collect c ON s.id = c.music_id AND c.user_id=%s
            ORDER BY RAND() LIMIT 8
        """, (user_id,))
        songs = cursor.fetchall()

    print(songs)
    return render_template(
        'songer_list.html',
        random_songs=random_songs,  # 推荐歌曲列表（带收藏状态）
        songs=songs,  # 随机歌曲列表（带收藏状态）
        this=default_artist,  # 默认歌手
        artists=artists,  # 所有歌手列表
        selected_artist=selected_artist,  # 当前选中歌手
        collected_songs=collected_songs,  # 用户收藏的歌曲ID列表
        user_logged_in='uname' in session  # 用户登录状态
    )


@front.route('/music_detail', methods=['GET'])
def music_detail():
    music_id = request.args.get('music_id')  # 从查询参数获取 music_id

    if not music_id:
        return redirect(url_for('front.index'))  # 如果没有 music_id，重定向到首页

    # 查询音乐详情
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM songs WHERE id = %s", (music_id,))
        music = cursor.fetchone()

    # 查询评论
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT mc.content, mc.create_time, u.username 
            FROM music_comment mc
            JOIN user u ON mc.user_id = u.id
            WHERE mc.music_id = %s
            ORDER BY mc.create_time DESC
        """, (music_id,))
        comments = cursor.fetchall()

    return render_template('music_detail.html', music=music, comments=comments, music_id=music_id)


def contains_sensitive_words(content):
    """
    检查评论内容是否包含敏感词
    :param content: 评论内容
    :return: True（包含敏感词）或 False（不包含敏感词）
    """
    # 获取所有启用的敏感词
    with conn.cursor() as cursor:
        cursor.execute("SELECT keyword FROM dict_table WHERE is_show = 1")
        sensitive_words = [row[0] for row in cursor.fetchall()]

    # 使用 jieba 分词
    words = jieba.lcut(content)
    print(words)
    # 检查是否包含敏感词
    for word in words:
        if word in sensitive_words:
            return True
    return False


@front.route('/submit_comment', methods=['POST'])
def submit_comment():
    user_id = session.get('uname')  # 获取用户ID
    music_id = request.form.get('music_id')  # 从表单获取 music_id
    content = request.form.get('content')  # 从表单获取评论内容

    if not user_id:
        return "请先登录", 401  # 未登录用户无法评论

    if not music_id or not content:
        return "音乐ID或评论内容不能为空", 400

    # 检查评论内容是否包含敏感词
    if contains_sensitive_words(content):
        return "评论包含敏感词，请修改后重新提交", 400

    # 插入评论
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO music_comment (user_id, music_id, content, create_time)
            VALUES (%s, %s, %s, %s)
        """, (user_id, music_id, content, datetime.now()))
        conn.commit()

    return "评论提交成功", 200  # 成功提交评论


@front.route('/collected', methods=['POST'])
def collected():
    song_id = request.json.get('id')

    user_id = session['uname']

    # 检查用户是否已经收藏
    cursor.execute("SELECT * FROM collect WHERE user_id = %s AND music_id = %s", (user_id, song_id))
    user_song = cursor.fetchone()

    if user_song:
        return jsonify({'success': 200, 'message': '你已经收藏了该歌曲，请勿重复收藏 '})

    # 创建用户收藏
    print(song_id)
    cursor.execute("INSERT INTO collect (music_id, user_id) VALUES (%s, %s)", (song_id, user_id))
    conn.commit()

    return jsonify({
        'success': 200,
        'message': '成功收藏',
        'new_state': 'collected'  # 返回最新状态
    })


@front.route('/uncollected', methods=['POST'])
def uncollected():
    song_id = request.json.get('id')
    user_id = session['uname']
    print(song_id)
    # 检查用户是否收藏了该歌曲
    cursor.execute("SELECT * FROM collect WHERE user_id = %s AND music_id = %s", (user_id, song_id))
    user_song = cursor.fetchone()

    if user_song:
        cursor.execute("DELETE FROM collect WHERE user_id = %s AND music_id = %s", (user_id, song_id))
        conn.commit()
        return jsonify({
            'success': 200,
            'message': '成功取消收藏',
            'new_state': 'uncollected'
        })
    else:
        return jsonify({'success': 200, 'message': '歌曲错误'})


@front.route('/check_collected')
def check_collected():
    if 'uname' not in session:
        return jsonify({'collected': False})

    song_id = request.args.get('id')
    user_id = session['uname']

    try:
        with conn.cursor() as cursor:  # 使用with语句确保正确管理游标
            cursor.execute("SELECT 1 FROM collect WHERE user_id = %s AND music_id = %s",
                           (user_id, song_id))
            result = cursor.fetchone()
            conn.commit()  # 显式提交事务
            return jsonify({'collected': result is not None})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'collected': False}), 500


# 专辑列表
@front.route('/playlist')
def playlist():
    limit = 12  # 改为12方便卡片布局
    page = int(request.args.get("page", 1))

    # 修改为查询new_playlists表
    count_sql = "SELECT COUNT(*) AS total FROM new_playlists;"
    cursor.execute(count_sql)
    total = int(cursor.fetchone()[0])

    total_pages = math.ceil(total / limit)
    page = min(max(page, 1), total_pages)
    start = (page - 1) * limit

    # 修改查询字段，按播放量排序
    sql = """SELECT playlist_title, playlist_cover, play_count, author, playlist_link 
           FROM new_playlists 
           ORDER BY play_count DESC 
           LIMIT %s, %s;"""
    cursor.execute(sql, (start, limit))
    datalist = cursor.fetchall()

    paginate = {
        'pages': total_pages,
        'page': page,
        'iter_pages': lambda: generate_pagination(page, total_pages)
    }
    return render_template("playlist.html", playlists=datalist, paginate=paginate)


# 可视化
@front.route('/ksh')
def ksh():
    # 所有分析维度数据查询
    charts_data = {}

    # 歌手歌曲数量排行（南丁格尔玫瑰图）
    cursor.execute('SELECT singer_name, song_count FROM part1 limit 10')
    charts_data['singer'] = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]

    # 专辑歌曲分布（堆叠柱状图）
    cursor.execute('SELECT album_name, song_count FROM part2 LIMIT 10')
    album_data = cursor.fetchall()
    charts_data['album_names'] = [row[0] for row in album_data]
    charts_data['album_counts'] = [row[1] for row in album_data]

    # 播放列表分析（散点图）
    cursor.execute('SELECT playlist_title, song_count, play_count FROM part3')
    play_data = cursor.fetchall()
    charts_data['play_list'] = [{
        'name': row[0],
        'value': [row[1], row[2], row[1] * 0.3]  # [歌曲数量, 播放量, 气泡大小]
    } for row in play_data]
    print(charts_data['play_list'])
    # 播放量分布（环形图）
    cursor.execute('SELECT play_range, playlist_count FROM part4')
    charts_data['play_range'] = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]

    # 作者分析（横向柱状图）
    cursor.execute('SELECT author, playlist_count FROM part5 LIMIT 10')
    author_data = cursor.fetchall()
    charts_data['authors'] = [row[0] for row in author_data]
    charts_data['author_counts'] = [row[1] for row in author_data]

    # 流行度分析（阶梯折线图）
    cursor.execute('SELECT popularity_range, song_count FROM part6')
    pop_data = cursor.fetchall()
    charts_data['pop_ranges'] = [row[0] for row in pop_data]
    charts_data['pop_counts'] = [row[1] for row in pop_data]

    df = pd.read_csv('data/plalist_clean.csv')
    df['播放量'] = pd.to_numeric(df['播放量'])
    # 按播放量降序排序，并取前十名
    top_playlists = df.nlargest(10, '播放量')[['歌单标题', '播放量']]
    play_list = top_playlists['歌单标题'].tolist()
    play_num_list = top_playlists['播放量'].tolist()
    charts_data['play_list1'] = play_list
    charts_data['play_num_list1'] = play_num_list
    wordcloud_dict = creatwc(df)
    charts_data['wordcloud_dict'] = wordcloud_dict
    return render_template('ksh.html', **charts_data)


def load_stopwords(file_path):
    """加载停用词"""
    with open(file_path, 'r', encoding='utf-8') as f:
        stopwords = set(f.read().strip().split('\n'))
    return stopwords


def creatwc(df_data):
    # 加载停用词
    stopwords = load_stopwords('data/stopwords.txt')
    # 想要去除的情感词
    unwanted_words = {'喜欢', '爱', '不错', '推荐'}  # 可以添加更多不平衡情感词

    # 词频统计
    word_count = {}
    for r, data in df_data.iterrows():
        words = jieba.cut(data['歌单标题'])
        for word in words:
            if word in stopwords or word in unwanted_words:
                continue
            if len(word) < 2:
                continue
            try:
                float(word)  # 检查是否为数值
                continue
            except ValueError:
                pass  # 如果不是数值则继续

            # 统计词频
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1

    # 排序和格式化结果
    wordclout_dict = sorted(word_count.items(), key=lambda d: d[1], reverse=True)
    wordclout_dict = [{"name": k[0], "value": k[1]} for k in wordclout_dict]
    return wordclout_dict


# 推荐音乐
@front.route('/recommend')
def recommend():
    user_id = session['uname']
    # sql=" SELECT music_name,music_singer FROM new_music  WHERE id IN (SELECT songid FROM rec  WHERE user_id='"+ str(user_id) +"')"
    # cursor.execute(sql)
    # data=cursor.fetchall()
    limit = 15
    page = int(request.args.get("page", 1))
    # 查询总记录数
    count_sql = "select count(*) from rec where user_id='" + str(user_id) + "';"
    cursor.execute(count_sql)
    total = cursor.fetchone()[0]
    print()
    # 计算总页数
    total_pages = (total + limit - 1) // limit
    # 确保页数不超过总页数
    page = min(page, total_pages)
    # 计算分页的起始位置
    start = (page - 1) * limit
    # 查询当前页数据
    # sql = "SELECT id,music_name, music_singer FROM new_music LIMIT %s, %s;"
    sql = "SELECT songid,music_name, music_singer FROM new_music WHERE songid IN (SELECT songid FROM rec WHERE user_id = %s)"
    cursor.execute(sql, user_id)
    datalist = cursor.fetchall()
    paginate = {
        'pages': total_pages,
        'page': page,
        'iter_pages': lambda: range(1, total_pages + 1)
    }
    # print(datalist)

    return render_template("search.html", films=datalist, paginate=paginate)


@front.route('/category_music', endpoint='category_music', methods=['GET'])
def category_music():
    uid = session.get('uname')  # 获取当前用户 ID
    category_id = request.args.get('category_id', default=0, type=int)  # 获取类别 ID，默认值为 0
    page = request.args.get('page', 1, type=int)  # 分页参数
    per_page = 10  # 每页显示的音乐数量

    # 查询所有音乐类别
    music_categories = Music_category.query.all()

    # 查询当前类别名称
    current_category = Music_category.query.get(category_id) if category_id > 0 else None

    # 查询当前类别下的音乐列表
    music_query = Category_muisc.query.filter_by(category_id=category_id) if category_id > 0 else Category_muisc.query
    paginate = music_query.paginate(page=page, per_page=per_page, error_out=False)

    # 查询当前用户的收藏状态
    collected_songs = []
    if uid:
        collected_songs = db.session.query(Collect.music_id).filter_by(user_id=uid).all()
        collected_songs = [song[0] for song in collected_songs]  # 提取音乐 ID 列表

    return render_template(
        'category_music.html',
        music_categories=music_categories,
        current_category=current_category,
        paginate=paginate,
        collected_songs=collected_songs,
        category_id=category_id  # 将 category_id 传递给模板
    )


# 后端代码（Flask路由）
@front.route('/search', methods=['GET', 'POST'])
def search():
    user_id = session['uname']
    search_wd = request.form.get('search_wd')

    if search_wd:
        search_pattern = f'%{search_wd}%'
        sql = """
            SELECT s.id, s.song_id, s.song_name, s.singer_name, 
                   s.album_name, s.cover_url, s.popularity, s.playlist_id,
                   CASE WHEN c.music_id IS NOT NULL THEN 1 ELSE 0 END as collected
            FROM songs s
            LEFT JOIN collect c ON s.id = c.music_id AND c.user_id = %s
            WHERE s.song_name LIKE %s OR s.singer_name LIKE %s
            ORDER BY s.popularity DESC
        """
        cursor.execute(sql, (user_id, search_pattern, search_pattern))
        datalist = cursor.fetchall()
        print(datalist)
        return render_template('search.html', datalist=datalist, search_wd=search_wd)

    return render_template('search.html')


# 收藏列表
@front.route('/collect_list')
def collect_list():
    user_id = session['uname']
    limit = 12  # 改为12使布局更灵活
    page = int(request.args.get("page", 1))

    # 联表查询获取完整歌曲信息
    sql = """
    SELECT s.id, s.song_id, s.song_name, s.singer_name, 
           s.album_name, s.cover_url, s.popularity,
           EXISTS(SELECT 1 FROM collect WHERE user_id=%s AND music_id=s.id) as collected
    FROM songs s
    WHERE s.id IN (SELECT music_id FROM collect WHERE user_id=%s)
    ORDER BY s.popularity DESC
    LIMIT %s OFFSET %s
    """
    offset = (page - 1) * limit
    cursor.execute(sql, (user_id, user_id, limit, offset))
    songs = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    # 分页计算
    count_sql = "SELECT COUNT(DISTINCT music_id) FROM collect WHERE user_id=%s"
    cursor.execute(count_sql, (user_id,))
    total = cursor.fetchone()[0]
    total_pages = (total + limit - 1) // limit
    print(songs)
    return render_template("collect_list.html",
                           songs=songs,
                           paginate={'page': page, 'total_pages': total_pages})


def generate_pagination(current_page, total_pages):
    pages = []
    # 始终显示第一页
    pages.append(1)

    # 前段处理
    if current_page - 2 > 2:
        pages.append(None)  # 用None表示省略号

    # 显示当前页前后两页
    for p in range(max(2, current_page - 2), min(total_pages, current_page + 3)):
        pages.append(p)

    # 后段处理
    if current_page + 2 < total_pages - 1:
        pages.append(None)

    # 始终显示最后一页
    if total_pages > 1:
        pages.append(total_pages)

    # 去重并排序
    seen = set()
    unique_pages = []
    for p in pages:
        if p not in seen:
            seen.add(p)
            unique_pages.append(p)

    return unique_pages
