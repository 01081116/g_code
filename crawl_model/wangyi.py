import json
import time

import requests
from execjs import compile
# from flask import current_app
# from app import system
xx = '010001'
yy = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
zz = '0CoJUm6Qyw8W8jud'
OTHER_COOKIE = ''


def replace_lastChar(former_str):
    if len(former_str.split('?')) >= 2:
        replace_char = former_str.split('?')[0]
        return replace_char
    else:
        return former_str


class Wangyi:
    def __init__(self):
        self.headers = {
            'authority': 'music.163.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'referer': 'https://music.163.com/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
        self.cookies = {
            # 'MUSIC_U': 'NMTID=00O1vZIuA3oJnzWRUHAilblEcCXS44AAAGMtVhDYQ; vinfo_n_f_l_n3=5fa1c3b211a52efc.1.0.1709639575030.0.1709641190327; _ntes_nnid=02ddc23957e25e48edecbe07eb99db4b,1709642093967; _ntes_nuid=02ddc23957e25e48edecbe07eb99db4b; WEVNSM=1.0.0; WNMCID=awnban.1709642095577.01.0; WM_TID=qmj0W1xEAy9EERERRQfFKBDsUIQgCGBu; ntes_utid=tid._.1shAQrChvR5AU0EBVBLRgw5E6b%252BGEqi1._.0; sDeviceId=YD-WZrtNUAO695AEhBAUFeBfXfBoNfbGARB; WM_NI=hJ3o9Z1TLoNlswcEzel8nZqbBgejwNToyGDRh%2F%2FMjzeI5hcxCjrwEgCGCsgh4xga8rONMOCTc%2F4vMtguf5ANzK00K%2B%2FajV1Mqftw%2Bs7Y2Q5wP3oJcaxLDhg4rDsBh6uJUlo%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee92dc64a29fbfb1c169bae78fa7d55f828b8fb1d24b8288a5b9d17ffc9c9e98ef2af0fea7c3b92aac96fd90bc52f38c8490cd68b1a9ada6f96fb0e8a2bbf46a82b9ab8bf64698b1b7a8c75aacf1e1aee972a797fb89e27481b6be98c86d81998d94e664f8a8a982bb7a8d9283b0c260a1f1fc97d080a5abaad6c446ba9500d1ca21edbfa6b7b447b3babc98aa79f587feb2b87d94eda1abe26bbc948c89e640b29cbda3eb3eb7969b8dee37e2a3; __snaker__id=ZQYTOQ6bDEEPHFP7; __csrf=83bf30afe732f89378b3282ed887e929; __remember_me=true; MUSIC_U=000F082F531869F827F944633589E602A830189F37674D69D4690C887F6E3E8FBD7E8D702DFA9C8E71AA130F0360B76CF0B5D1DFCF90CA622296586C9E35F556CA970E392084AECFDAC38B521FDC7CF7CD02EF5CE9100645E38824C90FCE48BF32E2DD063AEDE2505BB18ACCFF32CBD974002B87C7D640369E2ED6F42D7294641D4F596FC8CCD6F2AB904B536CBEC51A2A6154E7B41343623A2845BD17B69FA877D005DBC9670CE216FF943B9C23FA0707320583D014D49BCED778AAF29970C34FD0C5C1FAF21AD59321B6DD10E2E44028F51B671E7CED48E8E59A487CAB3BE38842DC9BA582F964249A82C9C1936542294437863CA3814F6C917BDFE00A84524238CFA732A1F88B5CB96091DDCD6222931DF245142876F9BB8806B3023BE178E03D76BC1BE97419B608B85721BABEAFFC285BE246849B698D8E2D51C08C601CB55CAAABEAB45E380AEEE2A13ECFF1A035046B735F8B5924BF92D7A4C0B331D4AC; ntes_kaola_ad=1; gdxidpyhxdE=SRzaUqjymJ3zCxd8cY4nJ3llIcA8mld8kb1rhnjQxUdn%2FZbD10aqj%2BSC9xSIE1qEZ2xC5eza8ejCs4B%2FAKD15wqvNLu%2FwkZ6tQivYTQgbpNKrlL0QoiZRHCe2eO3X9I5CJJrxyO7z0epMBD%5CqXuvJXMXlpSfOOzYSVHy4Hrsxms1lGg5%3A1718197394015; JSESSIONID-WYYY=6BDPqhay47VuxalDk%2BuRu%5CgsHyvDi5vj5Ms19%2F%5CiCUDgAHMC2oRPCJ%2BWn%5CSRT%2BMFG0eCzTxWT3kSo6DA1p5Nitsqwh4MeCgQhnpNQqC5XYqICiIDyoAn5kYKU8j1cp0pkozA8dWv%2BhrG7jyHXTuBkTXlVozf%5Ce8zgJWDUFUvzTpvKTIo%3A1718209000848; _iuqxldmzr_=33; playerid=16035308',
            'MUSIC_U': 'MUSIC_R_T=1542251459862; MUSIC_A_T=1542251294902; NMTID=00OoQfPdlzKAaUuf0iTqSJWePl_OjsAAAGT3WT6aQ; vinfo_n_f_l_n3=5fa1c3b211a52efc.1.0.1709639575030.0.1709641190327; _ntes_nnid=55ebc091310b39b42261e43da30715ce,1734586204336; _ntes_nuid=55ebc091310b39b42261e43da30715ce; WEVNSM=1.0.0; WNMCID=uccgkm.1734586206343.01.0; WM_TID=v06g4PeEjjRARARQQVLGW6LiaTNSYqFn; ntes_utid=tid._.oamizlWX78RARgAVRFPHX%252FemLDIGdO%252Bi._.0; sDeviceId=YD-coo82SN9F3FABlEVUAaWH%2FeiKTZHcfqv; __snaker__id=ZQYTOQ6bDEEPHFP7; __remember_me=true; ntes_kaola_ad=1; __csrf=3d4e3865fef0009476ee39e12eaa0d64; MUSIC_U=007BAFCC4E242CED769E3CC4418B7843C85621892C0DDFF8AA4016CE166EFF2CCA99E948F51639C8C7EEAF8F3B8A225952E6CD2F18EF0E2D13C86FB8CFB4218759F5ED5A16A9E9EB7351EC30B981E43BC7DB1379030F94B7ED3C5DF2747610546BF1380CE7090CA2599A7AE4972378B21B4568C9018611383EA169DA70C7AD603F9CE43B9A2E7EF627ADF4985A2B6AE64852BADDCB92A7D33CE03A0625552296D8E38807658F2C3D552272BE9E8E47C8F063F3B0A33AAAD9D81A4B030B1A771A574B0AC446590893EC79971316C64A21985A81E7357ECF17F35D85FB07329B8885D3293B08DA898F74E9A3E292A8ED6DA2019650C37DEADBDAFBEB1BF2E4A23F041CFD73BBDC0E746A1D78FD7187D0C97A2190EFCD931C0660CAFF0E16A91427B6B60C11F91494A5B03C4E0A617B82CE459E21F9679AEE6455E3C9A9EB7C0BABC21DE9A342401991DEC4CC72966F3EB618017F59F170C0BEA243DB53FFFD02F2CC; JSESSIONID-WYYY=u20jSozpXgPmDFvINamKpIEsTxw%2B9dHZ7A%5CFn38g9ZRGJVnC%2FAMvguNmpGsec%2FcoPwNzc5i0AYQWXvZ0jTfxuseIQpCqFyOYSyP%2BPpNZgpIEHr2KfP2qe8kgyhfUflD2dnG3rCw%2FvSzgmKuKWX%2FeuHUqkt4uGqHBzo5JMqTff2RWqNSk%3A1734588004305; _iuqxldmzr_=32; playerid=691394551'

        }
        self.params = {
            'csrf_token': "3d4e3865fef0009476ee39e12eaa0d64",
        }

    def ajax_request(self, url, _i3x):
        for _ in range(5):
            # try:
            param = compile(open('./static/js/wangyi.js', 'r', encoding='utf-8').read()) \
                .call('d', json.dumps(_i3x, separators=(',', ':')), xx, yy, zz)
            data = {
                'params': param['encText'],
                'encSecKey': param['encSecKey']
            }
            resp = requests.post(url, headers=self.headers, params=self.params, cookies=self.cookies,
                                 data=data, timeout=10).json()

            return resp
            # except requests.exceptions.RequestException as e:
            #     # current_app.logger.error('ajax_request: %s', str(e))
            #     time.sleep(5)
        else:
            return {}

    def search(self, name, offset):
        _i3x = {
            "hlpretag":r'<span class=\"s-fc7\">',
            "hlposttag": "</span>",
            "id": "160947",
            "s": "自由の翅",
            "type": "1",
            "offset": "0",
            "total": "true",
            "limit": "30",
            "csrf_token": self.params['csrf_token']
        }
        url = 'https://music.163.com/weapi/cloudsearch/get/web'
        response = self.ajax_request(url=url, _i3x=_i3x)
        print(response)
        songs = response.get('result', {}).get('songs')
        if songs:
            return [{
                'type': 'wy',
                'id': song.get('id'),
                'name': song.get('name'),
                'singer': song.get('ar', [{}])[0].get('name'),
                'album': song.get('al', {}).get('name'),
                'cover_url': song.get('al', {}).get('picUrl')
            } for song in songs if song['privilege']['plLevel'] != 'none']
        else:
            print("no songs")

    def get_lyric(self, id):
        _i3x = {
            "id": id,
            "lv": -1,
            "tv": -1,
            "csrf_token": self.params['csrf_token']
        }
        response = self.ajax_request('https://music.163.com/weapi/song/lyric', _i3x)
        lyric_1 = response.get('lrc', {}).get('lyric')
        lyric_2 = response.get('tlyric', {}).get('lyric')
        return [lyric_1, lyric_2]

    def get_comment(self, id, times=-1):
        i3x = {
            'csrf_token': self.params['csrf_token'],
            'cursor': str(times),
            'offset': "0",
            'orderType': "1",
            'pageNo': "1",
            'pageSize': "20",
            'rid': f"R_SO_4_{id}",
            'threadId': f"R_SO_4_{id}",
        }
        datas = self.ajax_request('https://music.163.com/weapi/comment/resource/comments/get', i3x)
        hotComments = datas.get('data', {}).get('hotComments') if datas.get('data', {}).get('hotComments') else []
        commonComments = datas["data"]["comments"]
        allComments = hotComments + commonComments if times == -1 else commonComments
        return [{
            'user': info.get('user', {}).get('nickname'),
            'createTime': info.get('timeStr'),
            'likeCount': info.get('likedCount'),
            'text': info.get('content'),
            'time': info.get('time')
        } for info in allComments]

    def get_musicUrl(self, mid):
        i3x = {
            "ids": f"[{mid}]",
            "level": "standard",
            "encodeType": "aac",
            "csrf_token": self.params['csrf_token']
        }
        response = self.ajax_request('https://music.163.com/weapi/song/enhance/player/url/v1', i3x)
        Url = response.get("data", [{}])[0].get('url')
        if not Url and self.cookies['MUSIC_U'] != OTHER_COOKIE:
            self.cookies['MUSIC_U'] = OTHER_COOKIE
            return self.get_musicUrl(mid)
        else:
            return replace_lastChar(Url) if Url else None

    def get_everyday_recommend(self):
        _i3x = {
            "offset": "0",
            "total": "true",
            "csrf_token": self.params['csrf_token']
        }
        self.cookies['MUSIC_U'] = OTHER_COOKIE
        resp = self.ajax_request(url='https://music.163.com/weapi/v2/discovery/recommend/songs', _i3x=_i3x)
        songs = resp['recommend']
        if songs:
            return [{
                'type': 'wy',
                'id': song.get('id'),
                'name': song.get('name'),
                'singer': song.get('artists', [{}])[0].get('name'),
                'album': song.get('album', {}).get('name'),
                'cover_url': song.get('album', {}).get('picUrl')
            } for song in songs]

    def get_playlist(self, id):
        _13x = {
            "id": id,
            "offset": "0",
            "total": "true",
            "limit": "1000",
            "n": "1000",
            "csrf_token": self.params['csrf_token']
        }
        resp = self.ajax_request('https://music.163.com/weapi/v6/playlist/detail', _13x)
        playlist = resp.get('playlist', {})
        playlist_name = playlist.get('name')
        playlist_description = playlist.get('description')
        playlist_creator = playlist.get('creator', {}).get('nickname')
        playlist_cover = playlist.get('coverImgUrl')
        playlist_songs = playlist.get('tracks')
        privileges = resp.get('privileges')
        if not privileges:
            return {}
        privileges_list = [{
            'id': privilege.get('id'),
            'plLevel': privilege.get('plLevel'),
        } for privilege in privileges]
        songs = [{
            'id': song.get('id'),
            'name': song.get('name'),
            'singer': song.get('ar', [{}])[0].get('name'),
            'album': song.get('al', {}).get('name'),
            'cover_url': song.get('al', {}).get('picUrl')
        } for song, plLevel in zip(playlist_songs, privileges_list) if plLevel['plLevel'] != 'none']
        return {
            'name': playlist_name,
            'cover': playlist_cover,
            'songs': songs,
            'creator': playlist_creator,
            'description': playlist_description,
        }

    def detail(self, id):
        _i3x = {
            "id": str(id),  # 使用传入的 id
            "c": f"[{{\"id\":\"{id}\"}}]",
            "csrf_token": self.params['csrf_token']
        }
        url = 'https://music.163.com/weapi/v3/song/detail'
        response = self.ajax_request(url=url, _i3x=_i3x)
        # print(11111, response)
        songs = response.get('songs')
        if songs:
            # 取第一首歌的信息
            song = songs[0]
            # 获取 chargeInfoList 中的 chargeType 字段
            charge_info_list = response.get('privileges', [{}])[0].get('chargeInfoList', [])
            # 只取第一个 chargeType
            charge_type = charge_info_list[0].get('chargeType') if charge_info_list else None

            return {
                'song_name': song.get('name'),
                'singer_name': song.get('ar', [{}])[0].get('name'),
                'album_name': song.get('al', {}).get('name'),
                'cover_url': song.get('al', {}).get('picUrl'),
                'popularity': song.get('pop'),  # 添加热度字段
                'charge_type': charge_type  # 只取第一个 chargeType
            }
        else:
            print("no songs")
            return None


if __name__ == '__main__':
    wy = Wangyi()
    print(wy.detail(346576))
    print(wy.detail(168091))
    print(wy.detail(1962385456))
    print(wy.detail(1962385459))
    print(wy.detail(169174))
    print(wy.get_musicUrl(169174))

# chargeInfoList