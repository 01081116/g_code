import pandas as pd
from sqlalchemy import create_engine, text

def import_songs_to_db(csv_file, db_url, table_name):
    """
    将CSV文件中的歌曲数据导入到指定的数据库表中。

    :param csv_file: CSV文件的路径
    :param db_url: 数据库连接字符串
    :param table_name: 数据库表名
    """
    # 建立数据库连接
    engine = create_engine(db_url)

    # 读取CSV文件
    df = pd.read_csv(csv_file)

    # 重命名列
    df.columns = ['title', 'song_id', 'playlist']

    # 将DataFrame写入数据库
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)

    # 关闭数据库连接
    engine.dispose()

# 示例调用
# import_songs_to_db('song_clean.csv', 'mysql+pymysql://root:123456@localhost/lstm_music_rec', 'new_music')





def import_playlists_to_db(csv_file, db_url, table_name):
    """
    将CSV文件中的歌单数据导入到指定的数据库表中。
    如果表中已有数据，则先清空表。

    :param csv_file: CSV文件的路径
    :param db_url: 数据库连接字符串
    :param table_name: 数据库表名
    """
    # 建立数据库连接
    engine = create_engine(db_url)

    # 读取CSV文件
    df = pd.read_csv(csv_file)

    # 重命名列
    df.columns = ['type', 'page', 'playlist_title', 'playlist_link', 'playlist_cover', 'play_count', 'author', 'gdid']


    with engine.connect() as connection:
        # 清空表
        # connection.execute(text(f'TRUNCATE TABLE {table_name};'))

        # 将DataFrame写入数据库
        df.to_sql(table_name, con=connection, if_exists='replace', index=False)
        print(df)
    # 关闭数据库连接
    engine.dispose()


# 示例调用
import_playlists_to_db('plalist_clean.csv', 'mysql+pymysql://root:123456@localhost/lstm_music_rec', 'new_playlists')