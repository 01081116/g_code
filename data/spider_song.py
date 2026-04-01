import csv
import random
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

# 读取包含歌单链接的 CSV 文件
def read_playlist_csv(file_path):
    playlists = []
    df = pd.read_csv(file_path)
    df = df[df['类型'].isin(['流行', '摇滚', '民谣', '说唱'])]
    df['播放量'] = df['播放量'].str.replace('万','0000')
    df['播放量'] = df['播放量'].astype(float)
    top_playlists = df.groupby('类型').apply(lambda x: x.nlargest(1000, '播放量')).reset_index(drop=True)
    for i, r in top_playlists.iterrows():
        playlists.append(r)
    print(top_playlists)
    return playlists

def getHtml(url,headers):
    try:
        r = requests.get(url,headers = headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except:
        print('爬取失败')
        return ''


# 请求歌单链接并解析内容
def parse_playlist(url):
    with open('songs.csv', 'a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        try:
            time.sleep(random.random()*5)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            li = soup.select('.f-hide li a')
            for i in li:
                id=i['href'].split('=')[-1]
                name=i.text
                writer.writerow([name,id,url.split('=')[-1]])
        except requests.RequestException as e:
            print(f"请求歌单链接时出错: {e}")
    return []

# 将解析后的歌曲信息保存到 CSV 文件
def save_songs_to_csv(file_path):
    fieldnames = ['标题', '歌曲id', '所属歌单']
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()


if __name__ == "__main__":
    # 包含歌单链接的 CSV 文件路径
    playlist_csv_path = 'playlist_data.csv'
    # 保存歌曲信息的 CSV 文件路径
    output_csv_path = 'songs.csv'
    # save_songs_to_csv(output_csv_path)
    playlists = read_playlist_csv(playlist_csv_path)
    all_songs = []
    for playlist in playlists:
        playlist_url = playlist['歌单链接']
        print(f"正在解析歌单: {playlist['歌单标题']}")
        songs = parse_playlist(playlist_url)
        all_songs.extend(songs)


    print(f"歌曲信息已保存到 {output_csv_path}")