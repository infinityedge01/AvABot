import asyncio
import datetime
import re
import time
from email.utils import parsedate_tz
from typing import Any, Callable, Dict, Iterable, List, Tuple, Union

import aiohttp
import feedparser
from aiocqhttp.api import Api
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
import nonebot
from hoshino import Service

sv = Service("A-SOUL 动态推送")

def repl_emotion(s):
    s = s.group()
    s = re.sub(r'\<img alt=\"\[', '[', s)
    s = re.sub(r'\]\" [^\>]*\>', ']', s)
    return s
def parse_image(s : str):
    s = re.sub(r'\<img src=\"', '', s)
    s = re.sub(r'\" [^\>]*\>', '', s)
    return s
def parse(s : str):
    s = re.sub(r'\<img alt=\"\[[^\>]*\]\"[^\>]*\>', repl_emotion, s)
    img_lst = []
    lst = re.findall(r'\<img src=\"[^\>]*\"[^\>]*\>',s)
    for x in lst:
        img_lst.append(parse_image(x))
    s = s.replace('<br><br>', '\n')
    s = re.sub(r'\<[^>]*\>', '', s)
    return (s, img_lst)

class News:
    Passive = False
    Active = True
    Request = False

    def __init__(self,
                 bot_api: Api,
                 *args, **kwargs):
        self.api = bot_api
        self.news_interval_auto = True
        self._rssjob = {}
        self.sub_groups = [
            714681974,
            207751910,
            702429547
        ]
        self.sub_users = []
        self.rss = {
            "A-SOUL": {
                "name": "A-SOUL_Official",
                "source": "https://rss.infedg.xyz/bilibili/user/dynamic/703007996",
                "source2": "http://49.232.12.25:1200/bilibili/user/dynamic/703007996",
            },
            "AvA": {
                "name": "向晚大魔王",
                "source": "https://rss.infedg.xyz/bilibili/user/dynamic/672346917",
                "source2": "http://49.232.12.25:1200/bilibili/user/dynamic/672346917",
            },
            "Bella": {
                "name": "贝拉kira",
                "source": "https://rss.infedg.xyz/bilibili/user/dynamic/672353429",
                "source2": "http://49.232.12.25:1200/bilibili/user/dynamic/672353429",
            },
            "Carol": {
                "name": "珈乐Carol",
                "source": "https://rss.infedg.xyz/bilibili/user/dynamic/351609538",
                "source2": "http://49.232.12.25:1200/bilibili/user/dynamic/351609538",
            },
            "Diana": {
                "name": "嘉然今天吃什么",
                "source": "https://rss.infedg.xyz/bilibili/user/dynamic/672328094",
                "source2": "http://49.232.12.25:1200/bilibili/user/dynamic/672328094",
            },
            "Eileen": {
                "name": "乃琳Queen",
                "source": "https://rss.infedg.xyz/bilibili/user/dynamic/672342685",
                "source2": "http://49.232.12.25:1200/bilibili/user/dynamic/672342685",
            }
        }
        self.liveroom = {
            "A-SOUL": {
                "name": "A-SOUL_Official",
                "source": "https://api.live.bilibili.com/room/v1/Room/get_info?room_id=22632157&from=room",
                "headers": {
                    "Referer": "https://live.bilibili.com/22632157"
                },
            },
            "AvA": {
                "name": "向晚大魔王",
                "source": "https://api.live.bilibili.com/room/v1/Room/get_info?room_id=22625025&from=room",
                "headers": {
                    "Referer": "https://live.bilibili.com/22625025"
                },
            },
            "Bella": {
                "name": "贝拉kira",
                "source": "https://api.live.bilibili.com/room/v1/Room/get_info?room_id=22632424&from=room",
                "headers": {
                    "Referer": "https://live.bilibili.com/22632424"
                },
            },
            "Carol": {
                "name": "珈乐Carol",
                "source": "https://api.live.bilibili.com/room/v1/Room/get_info?room_id=22634198&from=room",
                "headers": {
                    "Referer": "https://live.bilibili.com/22634198"
                },
            },
            "Diana": {
                "name": "嘉然今天吃什么",
                "source": "https://api.live.bilibili.com/room/v1/Room/get_info?room_id=22637261&from=room",
                "headers": {
                    "Referer": "https://live.bilibili.com/22637261"
                },
            },
            "Eileen": {
                "name": "乃琳Queen",
                "source": "https://api.live.bilibili.com/room/v1/Room/get_info?room_id=22625027&from=room",
                "headers": {
                    "Referer": "https://live.bilibili.com/22625027"
                },
            }
        }
    async def from_liveroom_async(self, source) -> list:
        liveroom_source = self.liveroom[source]
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
              + "检查直播源：{}".format(liveroom_source["name"]))
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(liveroom_source["source"], headers=liveroom_source["headers"]) as response:
                    code = response.status
                    if code != 200:
                        print("直播源错误：{}，返回值：{}".format(
                            liveroom_source["name"], code))
                        return None
                    res = await response.json()
        except aiohttp.client_exceptions.ClientConnectionError:
            print("直播源连接错误："+liveroom_source["name"])
            return None
        except Exception as e:
            print("未知错误{} {}".format(type(e).__name__, e))
            return None
        if 'data' not in res.keys():
            print("直播源解析错误："+liveroom_source["name"])
            return None
        res = res['data']
        title = liveroom_source.get("title")
        liveroom_source["title"] = res['title']
        live_status = liveroom_source.get("live_status")
        liveroom_source["live_status"] = res['live_status']
        if title is None:
            print("直播源初始化："+liveroom_source["name"])
            return None
        news_list = list()
        if res['title'] != title:
            s = liveroom_source['name'] + '的直播间标题更新：\n'
            s = s + '标题：' + res['title'] + '\n'
            img_lst = []
            if 'user_cover' in res.keys() and res['user_cover'] != '':
                img_lst.append(res['user_cover'])
            news_list.append((s, img_lst, liveroom_source['headers']['Referer']))
        if res['live_status'] == 1 and live_status != 1:
            s = liveroom_source['name'] + '的直播间开播啦！\n'
            s = s + '标题：' + res['title'] + '\n'
            img_lst = []
            if 'user_cover' in res.keys() and res['user_cover'] != '':
                img_lst.append(res['user_cover'])
            news_list.append((s, img_lst, liveroom_source['headers']['Referer']))
        if news_list:
            return news_list
        else:
            return None
            
    async def from_rss_async(self, source) -> list:
        rss_source = self.rss[source]
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
              + "检查RSS源：{}".format(rss_source["name"]))
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(rss_source["source"], headers=rss_source.get("headers")) as response:
                    code = response.status
                    if code != 200:
                        print("rss源错误：{}，返回值：{}".format(
                            rss_source["name"], code))
                        res = None
                    else: res = await response.text()
        except aiohttp.client_exceptions.ClientConnectionError:
            print("rss源连接错误："+rss_source["name"])
            res = None
        except Exception as e:
            print("未知错误{} {}".format(type(e).__name__, e))
            res = None
        if res == None:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
              + "检查RSS源：{}".format(rss_source["name"]))
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(rss_source["source2"], headers=rss_source.get("headers")) as response:
                        code = response.status
                        if code != 200:
                            print("rss源错误：{}，返回值：{}".format(
                                rss_source["name"], code))
                            return None
                        res = await response.text()
            except aiohttp.client_exceptions.ClientConnectionError:
                print("rss源连接错误："+rss_source["name"])
                return None
            except Exception as e:
                print("未知错误{} {}".format(type(e).__name__, e))
                return None
        feed = feedparser.parse(res)
        if feed["bozo"]:
            print("rss源解析错误："+rss_source["name"])
            return None
        if len(feed["entries"]) == 0:
            print("rss无效："+rss_source["name"])
            return None
        last_id = rss_source.get("last_id")
        if rss_source.get("last_id") == None or  rss_source["last_id"] < feed["entries"][0]["id"]:
            rss_source["last_id"] = feed["entries"][0]["id"]
        print(rss_source["last_id"])
        if last_id is None:
            print("rss初始化："+rss_source["name"])
            return None
        news_list = list()
        flag = 0
        for item in feed["entries"]:
            if item["id"] <= last_id:
                flag = 1
                break

            s, img_lst = parse(item['summary'])
            if item['title'][0] != s[0]:
                s = item['title'] + '\n' + s
            if s.startswith('运营代转//转发自: @A-SOUL_Official:'):
                s = '运营代转//转发自: @A-SOUL_Official:'
                img_lst = []
            if s.startswith('管家代转//转发自: @A-SOUL_Official:'):
                s = '管家代转//转发自: @A-SOUL_Official:'
                img_lst = []
            news_list.append((s, img_lst, item['link']))
        if news_list:
            return news_list
        else:
            return None

    def auto_job(self):
        after_5s = datetime.datetime.now()+datetime.timedelta(seconds=5)

        # 每个 rss 启动第一个任务
        subscribes = [s for s in self.rss.keys()]
        for source in subscribes:
            self.scheduler.add_job(
                self.send_rss_news_async,
                args=(source,),
                id=source,
                trigger=DateTrigger(after_5s),
                misfire_grace_time=1,
                coalesce=True,
                max_instances=1,
            )
            
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                      + " Added Job")

    async def send_rss_news_async(self, source):
        res = await self.from_rss_async(source)
        if source == "A-SOUL":
            await self.send_news_msg_async(res, name = self.rss[source]['name'], msg0 = '的动态更新：\n', send_channel= self.official_channel)
        else:
            await self.send_news_msg_async(res, name = self.rss[source]['name'], msg0 = '的动态更新：\n', send_channel= self.member_channel)
    async def send_liveroom_news_async(self, source):
        res = await self.from_liveroom_async(source)
        await self.send_news_msg_async(res, send_prefix = False, send_channel= self.liveroom_channel)

    async def send_news_msg_async(self, res, name = '', msg0 = '的动态更新：\n', send_prefix = True, send_channel = None):
        sub_groups = self.sub_groups
        sub_users = self.sub_users
        if res is None:
            return
        elif isinstance(res, Exception):
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    + " Exception: " + str(res))
            return
        for dynamic in res:
            flag = 1
            if send_channel != self.official_channel:
                flag = 0
            if not ("日程表" in dynamic[0] and "直播间" in dynamic[0] and "小姐姐们的传送门" in dynamic[0]):
                flag = 0
            if flag == 1:
                l = dynamic[0].find("//转发自: @A-SOUL_Official:")
                if l != -1:
                    dynamic = (dynamic[0][:l] + "\n", dynamic[1], dynamic[2])
            msg = nonebot.message.MessageSegment.text('')
            if send_prefix: 
                msg = nonebot.message.MessageSegment.text(name + msg0)
            msg = msg + nonebot.message.MessageSegment.text(dynamic[0])
            for img in dynamic[1]:
                print(img)
                msg = msg + nonebot.message.MessageSegment.image(img)
                
            msg = msg + nonebot.message.MessageSegment.text(dynamic[2])
            for group in sub_groups:
                try:
                    await self.api.send_group_msg(
                        group_id=group,
                        message=msg,
                    )
                except:
                    pass
                await asyncio.sleep(0.5)
            for user in sub_users:
                try:
                    await self.api.send_private_msg(
                        user_id=user,
                        message=msg,
                    )
                except:
                    pass
                await asyncio.sleep(0.5)

            


news = News(bot_api = nonebot.get_bot())
@sv.scheduled_job('cron', second = '*/30')
async def _call():
    subscribes = [s for s in news.rss.keys()]
    liverooms = [s for s in news.liveroom.keys()]
    for source in subscribes:
        await news.send_rss_news_async(source)
    for source in liverooms:
        await news.send_liveroom_news_async(source)
        await asyncio.sleep(0.5)
    