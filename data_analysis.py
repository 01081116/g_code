import pymysql
import pandas as pd

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    db='lstm_music_rec',
    charset='utf8'
)
cursor = conn.cursor()


def reset_table(table_name, columns):
    """清空并重置分析表结构"""
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    create_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
    cursor.execute(create_sql)


def analyze_part1():
    """分析维度1：歌手歌曲数量排行"""
    reset_table('part1', ['singer_name VARCHAR(255)', 'song_count INT'])

    sql = '''
        SELECT singer_name, COUNT(*) AS song_count 
        FROM songs 
        GROUP BY singer_name 
        ORDER BY song_count DESC
    '''
    cursor.execute(sql)
    cursor.executemany("INSERT INTO part1 VALUES (%s, %s)", cursor.fetchall())


def analyze_part2():
    """分析维度2：专辑歌曲数量分布"""
    reset_table('part2', ['album_name VARCHAR(255)', 'song_count INT'])

    sql = '''
        SELECT album_name, COUNT(*) AS song_count 
        FROM songs 
        GROUP BY album_name 
        ORDER BY song_count DESC
    '''
    cursor.execute(sql)
    cursor.executemany("INSERT INTO part2 VALUES (%s, %s)", cursor.fetchall())


def analyze_part3():
    """分析维度3：播放列表歌曲数量分布"""
    reset_table('part3', ['playlist_title VARCHAR(255)', 'song_count INT', 'play_count INT'])

    sql = '''
      SELECT p.playlist_title, COUNT(s.id) AS song_count, p.play_count 
FROM new_playlists p
INNER JOIN songs s ON p.gdid = s.playlist_id
GROUP BY p.playlist_title, p.play_count 
ORDER BY song_count DESC;
    '''
    cursor.execute(sql)
    cursor.executemany("INSERT INTO part3 VALUES (%s, %s, %s)", cursor.fetchall())


def analyze_part4():
    """分析维度4：播放量分布分析"""
    reset_table('part4', ['play_range VARCHAR(50)', 'playlist_count INT'])

    ranges = [
        ('0-10万', 0, 100000),
        ('10万-50万', 100000, 500000),
        ('50万-100万', 500000, 1000000),
        ('100万以上', 1000000, 999999999)
    ]

    insert_data = []
    for r in ranges:
        sql = f'''
            SELECT COUNT(*) 
            FROM new_playlists 
            WHERE play_count BETWEEN {r[1]} AND {r[2]}
        '''
        cursor.execute(sql)
        count = cursor.fetchone()[0]
        insert_data.append((r[0], count))

    cursor.executemany("INSERT INTO part4 VALUES (%s, %s)", insert_data)


def analyze_part5():
    """分析维度5：作者播放列表数量"""
    reset_table('part5', ['author VARCHAR(255)', 'playlist_count INT'])

    sql = '''
        SELECT 
            SUBSTRING_INDEX(author, '%', 1) AS clean_author,
            COUNT(*) AS playlist_count
        FROM new_playlists 
        GROUP BY clean_author 
        ORDER BY playlist_count DESC
    '''
    cursor.execute(sql)
    cursor.executemany("INSERT INTO part5 VALUES (%s, %s)", cursor.fetchall())


def analyze_part6():
    """分析维度6：歌曲流行度分布"""
    reset_table('part6', ['popularity_range VARCHAR(50)', 'song_count INT'])

    sql = '''
        SELECT 
            CASE
                WHEN popularity >= 90 THEN '90-100 (爆款)'
                WHEN popularity >= 70 THEN '70-89 (热门)'
                WHEN popularity >= 50 THEN '50-69 (流行)'
                ELSE '0-49 (普通)'
            END AS popularity_range,
            COUNT(*) AS song_count
        FROM songs
        GROUP BY popularity_range
        ORDER BY MIN(popularity) DESC
    '''
    cursor.execute(sql)
    cursor.executemany("INSERT INTO part6 VALUES (%s, %s)", cursor.fetchall())


def run_all_analysis():
    """执行全部分析"""
    analyze_part1()
    analyze_part2()
    analyze_part3()
    analyze_part4()
    analyze_part5()
    analyze_part6()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    run_all_analysis()
