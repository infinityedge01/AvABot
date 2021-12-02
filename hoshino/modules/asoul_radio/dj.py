import time, os
import requests
import re
from bs4 import BeautifulSoup
import json
from hoshino import R, Service, priv, util

class Djradio:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
            'Referer': 'https://music.163.com/',
            'Host': 'music.163.com'
        }
        self.radio_url = 'https://music.163.com/djradio?id={}&order={}&_hash=programlist&limit=100&offset={}'

    def get_radio(self, id, page='1', order='降序'):
        songlist = []
        order = {'降序': '1', '升序': '2'}[order]
        url = self.radio_url.format(id, order, str(100 * (int(page) - 1)))
        try:
            soup = BeautifulSoup(requests.get(url, headers=self.headers).text, 'lxml')
            total = soup.find('span', attrs={'class': 'sub s-fc4'}).get_text()
            total = re.search(r'共(\d+)期', total).group(1)
            cnt = int(int(total) / 100) if int(total) % 100 == 0 else int(int(total) / 100) + 1  # 页数
            for one in soup.find('table', attrs={'class': 'm-table m-table-program'}).find('tbody').find_all('tr'):
                titel = one.find('td', attrs={'class': 'col2'}).find('div', attrs={'class': 'tt f-thide'}).find(
                    'a')
                songlist.append((titel.get_text(), one['id'].split('-')[-1], str(titel).split('<a href="/program?id=')[1].split('\" title=\"')[0]))
            if cnt > 1:
                time.sleep(1)
                url = self.radio_url.format(id, order, str(100 * (int(page))))
                soup = BeautifulSoup(requests.get(url, headers=self.headers).text, 'lxml')
                for one in soup.find('table', attrs={'class': 'm-table m-table-program'}).find('tbody').find_all('tr'):
                    titel = one.find('td', attrs={'class': 'col2'}).find('div', attrs={'class': 'tt f-thide'}).find(
                        'a')
                    songlist.append((titel.get_text(), one['id'].split('-')[-1], str(titel).split('<a href="/program?id=')[1].split('\" title=\"')[0]))
            # print(len(songlist), songlist)
            return songlist
        except Exception as e:
            print("抓取电台榜单出现问题：{} 榜单ID：{}".format(e, id))

#@sv.scheduled_job('cron', minute = '*')
async def update_song():
    asoul_music = {
        "向晚": {
            "DJ": "959003611",
            "img": "https://p1.music.126.net/itGB9iv4iD42ywQRcv1Xnw==/109951165742145059.jpg?param=200y200",
            "songs": []
        }, "贝拉": {
            "DJ": "959475841",
            "img": "https://p1.music.126.net/ZFPkPPDY97gpF4kpWHxzZA==/109951165775456553.jpg?param=200y200",
            "songs": []
        }, "珈乐": {
            "DJ": "959471867",
            "img": "https://p1.music.126.net/o6zwD1WTzQJTiVMMGKkFqA==/109951165775220810.jpg?param=200y200",
            "songs": []
        }, "嘉然": {
            "DJ": "959370203",
            "img": "https://p1.music.126.net/okKo0P2k_kKFMi9NHejd0Q==/109951166329625793.jpg?param=200y200",
            "songs": []
        }, "乃琳": {
            "DJ": "959453342",
            "img": "https://p1.music.126.net/jBBJp20lYbZKqSBgLkg0oA==/109951165773493066.jpg?param=200y200",
            "songs": []
        }, "团唱": {
            "DJ": "959803751",
            "img": "https://p1.music.126.net/8j2zkmZQByvYJFyEqklQGA==/109951165806918926.jpg?param=200y200",
            "songs": []
        }
    }
    radio = Djradio()
    for i in asoul_music:
        asoul_music[i]['songs'] = radio.get_radio(asoul_music[i]['DJ'])
    print(asoul_music)
    with open(f"{os.getcwd()}/hoshino/modules/asoul_radio/asoul_music.json", 'w', encoding='utf-8') as f:
        json.dump(asoul_music, f, ensure_ascii=False)
    return asoul_music
