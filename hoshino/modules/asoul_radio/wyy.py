import os

from Crypto.Cipher import AES
import base64
import json
import asyncio
import aiohttp
from nonebot import message
import nonebot
from nonebot.helpers import send
import requests
from fuzzywuzzy import fuzz
from hoshino import R, Service, priv, util
from .dj import *

bot = nonebot.get_bot()
sv = Service('asoul_wyy')
# 常量
headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0',
    'Referer':
        'https://music.163.com/',
    'Content-Type':
        'application/x-www-form-urlencoded',
}
post_url = 'https://music.163.com/weapi/song/enhance/player/url'
post_url2 = 'https://music.163.com/weapi/dj/program/detail?csrf_token='
content = {"ids": "", "br": 128000, "csrf_token": ""}
key1 = b'0CoJUm6Qyw8W8jud'
key2 = b'ryPnuAVT5RtiIWNi'
encSecKey = 'a71973af53caae445b554150da52e75ba5687609d28013aacea03e9ef07169560f156ca76be9ac8df7bb204e05b864756aa3dd2274a65d5be964f118f6d075006695059e10cdcc806306e9a5f2f36f5bf0379f511cd13a600a6cc7031c814583863ea84d3373dea69f74354cd2dc3af61d58eeb43b1de06f588ef361ebc1eed6 '

# 加密
pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
encrypt_token = lambda key, content: AES.new(key=key, mode=AES.MODE_CBC, IV=b'0102030405060708').encrypt(
    pad(content).encode())


# 接口
async def music_interface(song_id):
    content["ids"] = "[{}]".format(song_id)
    str_content = json.dumps(content)
    tmp = base64.b64encode(encrypt_token(key1, str_content)).decode()
    params = base64.b64encode(encrypt_token(key2, tmp)).decode()
    post_data = {
        'params': params,
        'encSecKey': encSecKey,
    }
    async with aiohttp.ClientSession() as requests:
        async with requests.post(url=post_url, headers=headers, data=post_data) as resp:
            try:
                js = json.loads(await resp.text())
                song_url = js['data'][0]['url']
                return song_url
            except Exception as e:
                print(e)
    await asyncio.sleep(1)
    async with aiohttp.ClientSession() as requests:
        async with requests.post(url=post_url, headers=headers, data=post_data) as resp:
            try:
                js = json.loads(await resp.text())
                song_url = js['data'][0]['url']
                return song_url
            except Exception as e:
                print(e)
                return ""

asouls = {}
with open(f'{os.getcwd()}/hoshino/modules/asoul_radio/asoul_music.json', 'r', encoding='utf-8') as asoul_f:
    asouls = json.load(asoul_f)

@sv.scheduled_job('cron', hour = '*/2')
async def load_song():
    global asouls
    asouls = await update_song()

def get_song(name, song):
    song_list = []
    for i in asouls:
        if name == i:
            for m in asouls[i]['songs']:
                if fuzz.ratio(song.lower().replace(' ', ''), m[0].lower().replace(' ', '')) > 50 or song.lower().replace(' ', '') in m[0].lower().replace(' ', ''):
                    singer = 'A-SOUL' if i == '团唱' else i
                    song_list.append((m[0], singer, asouls[i]['DJ'], asouls[i]['img'], m[1], m[2]))
    if name == 'all':
        for i in asouls:
            for m in asouls[i]['songs']:
                if fuzz.ratio(song.lower().replace(' ', ''), m[0].lower().replace(' ', '')) > 50 or song.lower().replace(' ', '') in m[0].lower().replace(' ', ''):
                    singer = 'A-SOUL' if i == '团唱' else i
                    song_list.append((m[0], singer, asouls[i]['DJ'], asouls[i]['img'], m[1], m[2]))
    return song_list


def music_info(song_id):
    content = {"id": song_id, "csrf_token": ""}
    str_content = json.dumps(content)
    tmp = base64.b64encode(encrypt_token(key1, str_content)).decode()
    params = base64.b64encode(encrypt_token(key2, tmp)).decode()
    post_data = {
        'params': params,
        'encSecKey': encSecKey,
    }
    resp = requests.post(url=post_url2, headers=headers, data=post_data)
    js = json.loads(resp.content)['program']
    return js['mainTrackId'], js['name']

current_song_list = {}

async def send_message_back(ev, msg):
    print(msg)
    if ev['message_type'] == 'guild':
        await bot.send_guild_channel_msg(guild_id = int(ev['guild_id']), channel_id = int(ev['channel_id']),message = msg)
    elif ev['message_type'] == 'group':
        await bot.send_group_msg(group_id = int(ev['group_id']), message = msg)
    return

@bot.on_message
async def order_song(ev):
    uni_group_id = 0
    if ev['message_type'] == 'guild':
        flag = 0
        if int(ev['guild_id']) == 54389341636635154 and int(ev['channel_id']) == 1411557:
            flag = 1
        elif int(ev['guild_id']) == 92473991636683621 and int(ev['channel_id']) == 1451313:
            flag = 1
        elif int(ev['guild_id']) == 73363381636714466 and int(ev['channel_id']) == 1451421:
            flag = 1
        if flag == 0:
            return
        uni_group_id = int(ev['guild_id']) % 19260817 * 10000000 + int(ev['channel_id'])
    elif ev['message_type'] == 'group':
        if int(ev['group_id']) not in [1021182194,714681974, 207751910, 702429547]:
            return
        uni_group_id = int(ev['group_id'])
    else:
        return
    
    if len(ev['message']) == 0:
        return
    command = str(ev['message']).split(' ')
    print(command)
    help_msg = '指令格式:\n/点歌 【向晚|贝拉|珈乐|嘉然|乃琳|团唱】 【】'
    help_msg_select = '指令格式:\n/选歌 【编号】'
    
    global current_song_list
    if command[0] == '/点歌':
        if len(command) < 3:
            await send_message_back(ev, message.MessageSegment.text('输入参数有误，请重新输入\n' + help_msg))
            return
        if command[1] not in ['向晚', '贝拉', '珈乐', '嘉然', '乃琳', '团唱']:
            await send_message_back(ev, message.MessageSegment.text('歌手有误，请重新输入' + help_msg))
            return
        current_song_list[uni_group_id] = get_song(command[1], command[2])
        if len(current_song_list[uni_group_id]) == 0:
            await send_message_back(ev, message.MessageSegment.text('找不到歌曲'))
            return
        msg_str = '你要找的歌曲可能是:'
        for i in range(len(current_song_list[uni_group_id])):
            msg_str = msg_str + '\n' + str(i + 1) + '： ' + current_song_list[uni_group_id][i][1] +  ' ' + current_song_list[uni_group_id][i][0]
        msg_str = msg_str + '\n请输入「/选歌 【编号】」来点歌'
        await send_message_back(ev, message.MessageSegment.text(msg_str))
        return
    if command[0] == '/选歌':
        if len(command) < 2:
            await send_message_back(ev, message.MessageSegment.text('输入参数有误，请重新输入\n' + help_msg_select))
            return
        if len(command[1]) > 3 or command[1].isdigit() == False:
            await send_message_back(ev, message.MessageSegment.text('输入参数有误，请重新输入\n' + help_msg_select))
            return
        if uni_group_id not in current_song_list.keys():
            await send_message_back(ev, message.MessageSegment.text('请先点歌\n' + help_msg))
            return
        if len(current_song_list[uni_group_id]) == 0:
            await send_message_back(ev, message.MessageSegment.text('请先点歌\n' + help_msg))
            return
        id = int(command[1])
        if id > len(current_song_list[uni_group_id]) or id == 0:
            await send_message_back(ev, message.MessageSegment.text('编号超过备选歌曲数目'))
            return
        music = current_song_list[uni_group_id][id - 1]
        url = await music_interface(music[4])
        if url == "":
            url = "http://m7.music.126.net/20211116144339/1081ba0c21c19c198136da50318e8c53/ymusic/obj/w5zDlMODwrDDiGjCn8Ky/11597941034/2610/f1bd/04b4/d4820331ca0102d46ccdc4ecebd08ac8.mp3"
        print(url)
        msg = '[CQ:xml,data=<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\' ?><msg serviceID="2" templateID="1" action="web" brief="&#91;分享&#93; {}" sourceMsgId="0" url="https://y.music.163.com/m/program?id={}" flag="0" adverSign="0" multiMsgFlag="0" ><item layout="2"><audio cover="{}" src="{}" /><title>{}</title><summary>{}</summary></item><source name="网易云音乐" icon="https://pic.rmb.bdstatic.com/911423bee2bef937975b29b265d737b3.png" url="http://web.p.qq.com/qqmpmobile/aio/app.html?id=1101079856" action="app" a_actionData="com.netease.cloudmusic" i_actionData="tencent100495085://" appid="100495085" /></msg>,resid=2]https://y.music.163.com/m/program?id={}'.format(music[0], music[5], music[3], url, music[0], music[1], music[5])
        msg2 = '[CQ:xml,data=<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\' ?><msg serviceID="146" templateID="1" action="web" brief="&#91;分享&#93; {}" sourceMsgId="0" url="https://y.music.163.com/m/program?id={}" flag="0" adverSign="0" multiMsgFlag="0"><item layout="2" advertiser_id="0" aid="0"><picture cover="{}" w="0" h="0" /><title>{}</title><summary>{}</summary></item><source name="网易云音乐" icon="https://pic.rmb.bdstatic.com/911423bee2bef937975b29b265d737b3.png" url="http://web.p.qq.com/qqmpmobile/aio/app.html?id=1101079856" action="app" a_actionData="com.netease.cloudmusic" i_actionData="tencent100495085://" appid="100495085" /></msg>,resid=146]https://y.music.163.com/m/program?id={}'.format(music[0], music[5], music[3], music[0], music[1], music[5])
        if ev['message_type'] == 'guild':
            await send_message_back(ev, msg2)
        else:
            await send_message_back(ev, msg)
        current_song_list[uni_group_id] = []
        return
