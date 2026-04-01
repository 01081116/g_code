import pandas as pd

def processing_songs():
    name_list = ['QQ登录', '微信登录', '网易邮箱账号登录', '微博登录']
    df = pd.read_csv('songs.csv')

    # 去重，考虑 '歌曲ID' 列
    df = df.drop_duplicates(subset=['歌曲id'])

    # 过滤掉包含在 name_list 中的标题
    df = df[~(df['标题'].isin(name_list))]

    df.to_csv('song_clean.csv', index=False)

def processing_playlist():
    df_playlist = pd.read_csv('playlist_data.csv')

    # 去重，考虑 'gdid' 列
    df_playlist['播放量'] = df_playlist['播放量'].str.replace('万', '0000')
    df_playlist['播放量'] = df_playlist['播放量'].astype(float)
    df_playlist['gdid'] = df_playlist['歌单链接'].str.split('=').str.get(-1)

    # 去重，考虑 'gdid' 列
    df_playlist = df_playlist.drop_duplicates(subset=['gdid'])

    df_playlist.to_csv('plalist_clean.csv', index=False)
    print(df_playlist)

# 调用函数
processing_songs()
processing_playlist()
