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
#@sv.on_fullmatch('mua', 'mua你一口', only_to_me=True)
@sv.on_rex(r'(\s*(mua|😘)$)|(^(mua|😘)你一(下|口)(捏|~)?\s*?$)', only_to_me=True)
async def chat_mua(bot, ev):
    print(random.random() )
    if random.random() > 0.5: return
    chat_mua = [
        'm..mua你一下也不是不可以啦！',
        'mua',
        '顶碗人你在看吗，在的话mua你一下'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s, at_sender=True)

#@sv.on_fullmatch('查询向晚状态', '#查询向晚状态', '#向晚状态', only_to_me=False)
@sv.on_rex(r'(^\s*(#)?(查询)?(向晚|晚晚|向晚大魔王)状态\s*$)', only_to_me=False)
async def chat_querystat(bot, ev):
    await bot.send(ev, '美少女的事情你少管')

#@sv.on_fullmatch('查询向晚状态', '#查询向晚状态', '#向晚状态', only_to_me=False)
@sv.on_rex(r'(^\s*((向晚|晚晚)在看吗(，|\,))?给你一拳(！|\!)?\s*$)', only_to_me=False)
async def chat_punch(bot, ev):
    chat_mua = [
        '顶碗人在看吗，给你一拳！'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)
    
@sv.on_keyword('🤤', only_to_me=True)
async def chat_guonan(bot, ev):
    if random.random() > 0.3: return
    chat_mua = [
        '好...好兄弟之间喜欢很正常啦'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)

@sv.on_keyword('🥺', only_to_me=True)
async def chat_pleading(bot, ev):
    if random.random() > 0.3: return
    chat_mua = [
        '🥺'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)



@sv.on_keyword('顶碗人', only_to_me=True)
async def chat_dwr(bot, ev):
    if random.random() > 0.5: return
    chat_mua = [
        '顶碗人们要和晚晚一起走下去哦'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)


@sv.on_keyword('钻头', only_to_me=True)
async def chat_drill(bot, ev):
    if random.random() > 0.5: return
    chat_mua = [
        '喜欢我钻头吗？',
        '到枝江大街走一走，看幽默钻头！',
        '到枝江大头走一走，看幽默钻头！'
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)

@sv.on_keyword('水母', only_to_me=True)
async def chat_jellyfish(bot, ev):
    if random.random() > 0.5: return
    chat_mua = [
        '别啊，水母为什么要度过相对失败的一生呢？',
        '水母……水母……普通透明的生物……',
        '但其实，你怎么知道水母会没有梦想呢？是吧？',
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)

@sv.on_keyword('下雨了', only_to_me=True)
async def chat_rain(bot, ev):
    if random.random() > 0.5: return
    chat_mua = [
        '原来是下雨了，我以为你把我整无语了',
        '下雨天了怎么办，我好想你~',
        '伞怎么这么小',
    ]
    s = random.choice(chat_mua)
    await bot.send(ev, s)
