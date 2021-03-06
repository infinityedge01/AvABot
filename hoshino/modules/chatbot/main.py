import random
import nonebot
import json
from Crypto.Hash import MD5
from nonebot import on_command, get_bot
from nonebot import message
from nonebot.command import group
bot = get_bot()
from hoshino import R, Service, priv, util

# basic function for debug, not included in Service('chat')


sv = Service('chatbot')
#@sv.on_fullmatch('mua', 'muaä½ ä¸å£', only_to_me=True)
@sv.on_rex(r'(\s*(mua|ð)$)|(^(mua|ð)ä½ ä¸(ä¸|å£)(æ|~)?\s*?$)', only_to_me=True)
async def chat_mua(bot, ev):
    print(random.random() )
    if random.random() > 0.5: return
    chat_mua = [
        'm..muaä½ ä¸ä¸ä¹ä¸æ¯ä¸å¯ä»¥å¦ï¼',
        'mua',
        'é¡¶ç¢äººä½ å¨çåï¼å¨çè¯muaä½ ä¸ä¸'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s, at_sender=True)

#@sv.on_fullmatch('æ¥è¯¢åæç¶æ', '#æ¥è¯¢åæç¶æ', '#åæç¶æ', only_to_me=False)
@sv.on_rex(r'(^\s*(#)?(æ¥è¯¢)?(åæ|ææ|åæå¤§é­ç)ç¶æ\s*$)', only_to_me=False)
async def chat_querystat(bot, ev):
    await bot.send(ev, 'ç¾å°å¥³çäºæä½ å°ç®¡')

#@sv.on_fullmatch('æ¥è¯¢åæç¶æ', '#æ¥è¯¢åæç¶æ', '#åæç¶æ', only_to_me=False)
@sv.on_rex(r'(^\s*((åæ|ææ)å¨çå(ï¼|\,))?ç»ä½ ä¸æ³(ï¼|\!)?\s*$)', only_to_me=False)
async def chat_punch(bot, ev):
    chat_mua = [
        'é¡¶ç¢äººå¨çåï¼ç»ä½ ä¸æ³ï¼'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)
    
@sv.on_keyword('ð¤¤', only_to_me=True)
async def chat_guonan(bot, ev):
    if random.random() > 0.3: return
    chat_mua = [
        'å¥½...å¥½åå¼ä¹é´åæ¬¢å¾æ­£å¸¸å¦'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)

@sv.on_keyword('ð¥º', only_to_me=True)
async def chat_pleading(bot, ev):
    if random.random() > 0.3: return
    chat_mua = [
        'ð¥º'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)



@sv.on_keyword('é¡¶ç¢äºº', only_to_me=True)
async def chat_dwr(bot, ev):
    if random.random() > 0.5: return
    chat_mua = [
        'é¡¶ç¢äººä»¬è¦åææä¸èµ·èµ°ä¸å»å¦'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)


@sv.on_keyword('é»å¤´', only_to_me=True)
async def chat_drill(bot, ev):
    if random.random() > 0.5: return
    chat_mua = [
        'åæ¬¢æé»å¤´åï¼',
        'å°ææ±å¤§è¡èµ°ä¸èµ°ï¼çå¹½é»é»å¤´ï¼',
        'å°ææ±å¤§å¤´èµ°ä¸èµ°ï¼çå¹½é»é»å¤´ï¼'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)

@sv.on_keyword('æ°´æ¯', only_to_me=True)
async def chat_jellyfish(bot, ev):
    if random.random() > 0.5: return
    chat_mua = [
        'å«åï¼æ°´æ¯ä¸ºä»ä¹è¦åº¦è¿ç¸å¯¹å¤±è´¥çä¸çå¢ï¼',
        'æ°´æ¯â¦â¦æ°´æ¯â¦â¦æ®ééæççç©â¦â¦',
        'ä½å¶å®ï¼ä½ æä¹ç¥éæ°´æ¯ä¼æ²¡ææ¢¦æ³å¢ï¼æ¯å§ï¼',
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)

@sv.on_keyword('ä¸é¨äº', only_to_me=True)
async def chat_rain(bot, ev):
    if random.random() > 0.5: return
    chat_mua = [
        'åæ¥æ¯ä¸é¨äºï¼æä»¥ä¸ºä½ æææ´æ è¯­äº',
        'ä¸é¨å¤©äºæä¹åï¼æå¥½æ³ä½ ~',
        'ä¼æä¹è¿ä¹å°',
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)
