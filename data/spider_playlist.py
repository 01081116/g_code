import random
import time
import csv
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'
}
csv_file = open('playlist_data.csv', 'w', newline='', encoding='utf-8-sig')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['类型', '页数', '歌单标题', '歌单链接', '歌单封面', '播放量', '作者'])

typelist = ['华语', '欧美', '流行', '摇滚', '民谣', '说唱']

for type_name in typelist:
    for page in range(50):
        offset = page * 35
        url = f'https://music.163.com/discover/playlist/?order=hot&cat={type_name}&limit=35&offset={offset}'
        try:
            # 发送请求获取页面内容
            time.sleep(random.random()*5)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # 解析页面内容
            iframe_soup = BeautifulSoup(response.text, 'html.parser')
            ul = iframe_soup.find('ul', class_='m-cvrlst f-cb', id='m-pl-container')
            if ul:
                lis = ul.find_all('li')
                for li in lis:
                    try:
                        # 歌单封面图片链接
                        cover_img = li.find('img', class_='j-flag')['src']
                        # 歌单标题
                        title = li.find('a', class_='tit f-thide s-fc0')['title']
                        # 歌单链接
                        playlist_url = 'https://music.163.com' + li.find('a', class_='tit f-thide s-fc0')['href']
                        # 播放量
                        play_count = li.find('span', class_='nb').text
                        # 歌单作者
                        author = li.find('a', class_='nm nm-icn f-thide s-fc3')['title']
                        print(f'类型: {type_name}, 第 {page + 1} 页')
                        print(f'歌单标题: {title}')
                        print(f'歌单链接: {playlist_url}')
                        print(f'歌单封面: {cover_img}')
                        print(f'播放量: {play_count}')
                        print(f'作者: {author}')
                        print('-' * 50)
                        # 写入 CSV 文件
                        csv_writer.writerow([type_name, page + 1, title, playlist_url, cover_img, play_count, author])
                    except Exception as e:
                        print(f'解析错误: {e}')
            else:
                print(f'未找到 ul 元素，类型: {type_name}, 第 {page + 1} 页')
        #     else:
        #         print(f'未找到 iframe 元素，类型: {type_name}, 第 {page + 1} 页')
        except requests.RequestException as e:
            print(f'请求错误: {e}')
# 关闭 CSV 文件
csv_file.close()