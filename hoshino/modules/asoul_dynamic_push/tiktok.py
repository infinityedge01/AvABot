import time
import aiohttp
import asyncio
import nonebot
from nonebot.log import logger
from nonebot import MessageSegment
from hoshino import Service

sv = Service("A-SOUL 抖音推送")

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cache-control": "no-cache",
    "cookie": "_tea_utm_cache_1243={%22utm_source%22:%22copy%22%2C%22utm_medium%22:%22android%22%2C%22utm_campaign%22"
              ":%22client_share%22}",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Microsoft Edge\";v=\"92\"",
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84 "
}

asoul = {
    "乃琳Queen": "MS4wLjABAAAAxCiIYlaaKaMz_J1QaIAmHGgc3bTerIpgTzZjm0na8w5t2KTPrCz4bm_5M5EMPy92",
    "嘉然今天吃什么": "MS4wLjABAAAA5ZrIrbgva_HMeHuNn64goOD2XYnk4ItSypgRHlbSh1c",
    "向晚大魔王": "MS4wLjABAAAAxOXMMwlShWjp4DONMwfEEfloRYiC1rXwQ64eydoZ0ORPFVGysZEd4zMt8AjsTbyt",
    "珈乐Carol": "MS4wLjABAAAAuZHC7vwqRhPzdeTb24HS7So91u9ucl9c8JjpOS2CPK-9Kg2D32Sj7-mZYvUCJCya",
    "贝拉Kira": "MS4wLjABAAAAlpnJ0bXVDV6BNgbHUYVWnnIagRqeeZyNyXB84JXTqAS5tgGjAtw0ZZkv0KSHYyhP",
    "A-SOUL Official": "MS4wLjABAAAAflgvVQ5O1K4RfgUu3k0A2erAZSK7RsdiqPAvxcObn93x2vk4SKk1eUb6l_D4MX-n"
}

asoul_dy = {}

async def listen_dy():
    for i in asoul:
        new_dy = await nearly_dy(asoul[i])
        if new_dy:
            a = [dy for dy in new_dy if dy not in asoul_dy[i]]
            if a and (info := await dy_info(a[0])):
                bot = nonebot.get_bot()
                group_id = [714681974, 207751910, 702429547]
                logger.info(f'发现{i}抖音更新.')
                message = f'{i}的抖音更新：' + MessageSegment.image(info[1]) + info[0] + '\n↓点击链接观看↓\n'\
                          + 'https://www.douyin.com/video/'+a[0]
                # for g in group_id:
                #     await bot.call_api('send_group_msg', **{
                #         'message': message,
                #         'group_id': g['group_id']
                #     })
                asoul_dy[i] = new_dy
                for g in group_id:
                    try:
                        await bot.send_group_msg(group_id = g, message = message)
                    except:
                        pass
                    await asyncio.sleep(0.5)
        await asyncio.sleep(0.5) 
        # logger.info('sleep1秒')


async def nearly_dy(uid: str) -> list:
    url = f'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid={uid}&count=21'
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url=url) as response:
            try:
                m = []
                resp = (await response.json())['aweme_list']
                if resp:
                    m = [vid['aweme_id'] for vid in resp][:10]
                return m
            except Exception as e:
                print(e)
                return []


async def dy_info(id: str):
    url = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={id}'
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url=url) as response:
            try:
                resp = (await response.json())['item_list'][0]
                return [resp['desc'], resp['video']['cover']['url_list'][0]]
            except Exception as e:
                print(e)
                return []


async def dy_init():
    for i in asoul:
        asoul_dy[i] = await nearly_dy(asoul[i])
        if asoul_dy[i]:
            pass
        else:
            logger.info(f'{i}初始化失败')
        # await asyncio.sleep(1)
    logger.info(str(asoul_dy))
    logger.info("抖音监测初始化成功")


@sv.scheduled_job('cron', second = '45')
async def dy_job():
    if len(asoul_dy) == 0:
        await dy_init()
    else:
        await listen_dy()
    