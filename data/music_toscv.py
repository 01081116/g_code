from crawl_model.wangyi import Wangyi
import pandas as pd
from sqlalchemy import create_engine, text

# 创建数据库连接
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/lstm_music_rec')  # 替换为你的数据库连接信息

# 初始化 Wangyi 实例
wy = Wangyi()

def insert_songs_to_db(num_records):
    # 清空 songs 表
    try:
        with engine.connect() as connection:
            truncate_query = text("TRUNCATE TABLE songs")
            connection.execute(truncate_query)
            print("已清空 songs 表。")
    except Exception as e:
        print(f"清空表时发生错误: {e}")
        return  # 如果清空表失败，则终止函数执行

    # 读取 CSV 文件
    df = pd.read_csv('song_clean.csv', header=None, skiprows=1, names=['song_name', 'song_id', 'playlist_id'])

    inserted_count = 0  # 记录插入的歌曲数量

    for index, row in df.iterrows():
        song_id = row['song_id']
        playlist_id = row['playlist_id']

        print(f"正在处理歌曲 ID: {song_id}")
        try:
            # 获取歌曲详情
            song_detail = wy.detail(str(song_id))
            if song_detail is None:
                print(f"歌曲 ID {song_id} 详情获取失败，跳过处理。")
                continue

            print(song_detail)

            # 检查 charge_type 是否为 0
            charge_type = song_detail.get('charge_type')
            if charge_type == 0:
                data = {
                    'song_id': song_id,
                    'song_name': song_detail['song_name'],
                    'singer_name': song_detail['singer_name'],
                    'album_name': song_detail['album_name'],
                    'cover_url': song_detail['cover_url'],
                    'popularity': song_detail['popularity'],
                    'playlist_id': playlist_id
                }

                print("准备插入的数据:", data)  # 打印准备插入的数据

                try:
                    with engine.connect() as connection:
                        insert_query = text("""
                            INSERT INTO songs (song_id, song_name, singer_name, album_name, cover_url, popularity, playlist_id)
                            VALUES (:song_id, :song_name, :singer_name, :album_name, :cover_url, :popularity, :playlist_id)
                        """)
                        connection.execute(insert_query, data)
                        connection.commit()
                        inserted_count += 1  # 增加插入计数
                except Exception as e:
                    print(f"插入数据时发生错误: {e}")

            # 检查插入数量是否达到要求
            if inserted_count >= num_records:
                break

        except Exception as e:
            print(f"处理歌曲 ID {song_id} 时发生错误: {e}")
            continue  # 跳过当前歌曲，继续处理下一个歌曲

    print("数据已成功插入到数据库中。")

# 调用函数，传入要插入的记录数量
insert_songs_to_db(1000)
