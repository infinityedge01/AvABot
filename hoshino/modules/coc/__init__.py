from .dices import rd, help_message, shoot, en
from .madness import ti, li
from .investigator import Investigator
from .san_check import sc
from .cards import _cachepath, cards, cache_cards, set_handler, show_handler, sa_handler, del_handler
from nonebot import message, NoneBot
import nonebot
from nonebot.helpers import send
from hoshino import R, Service, priv, util
from aiocqhttp import Event
import os

bot = nonebot.get_bot()

if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists(_cachepath):
    with open(_cachepath, "w", encoding="utf-8") as f:
        f.write("{}")
cards.load()


async def send_message_back(ev : Event, msg):
    if ev['message_type'] == 'group':
        await bot.send_group_msg(group_id = int(ev['group_id']), message = msg)
    return

async def rdhelphandler(event: Event):
    args = str(event.message)[5:].strip()
    await send_message_back(event, help_message(args))


async def shootcommandhandler(event: Event):
    await send_message_back(event, shoot())


async def enhandler(event: Event):
    args = str(event.message)[3:].strip()
    await send_message_back(event, en(args))


async def rdcommandhandler(event: Event):
    args = str(event.message)[2:].strip()
    try:
        uid = event['user_id']
    except:
        uid = event['tiny_id']
    if not("." in args):
        rrd = rd(args)
        if type(rrd) == str:
            await send_message_back(event, rrd)
        elif type(rrd) == list:
            await bot.send_private_msg(user_id=uid, message=rrd[0])


async def cochandler(event: Event):
    args = str(event.message)[4:].strip()
    try:
        args = int(args)
    except ValueError:
        args = 20
    inv = Investigator()
    await send_message_back(event, inv.age_change(args))
    if 15 <= args < 90:
        cache_cards.update(event, inv.__dict__, save=False)
        await send_message_back(event, inv.output())


async def ticommandhandler(event: Event):
    await send_message_back(event, ti())


async def licommandhandler(event: Event):
    await send_message_back(event, li())


async def schandler(event: Event):
    args = str(event.message)[3:].strip().lower()
    await send_message_back(event, sc(args, event=event))


async def sethandler(event: Event):
    args = str(event.message)[3:].strip().lower()
    await send_message_back(event, set_handler(event, args))


async def showhandler(event: Event):
    args = str(event.message)[5:].strip().lower()
    for msg in show_handler(event, args):
        await send_message_back(event, msg)


async def sahandler(event: Event):
    args = str(event.message)[3:].strip().lower()
    await send_message_back(event, sa_handler(event, args))


async def delhandler(event: Event):
    args = str(event.message)[4:].strip().lower()
    for msg in del_handler(event, args):
        await send_message_back(event, msg)

@bot.on_message
async def all_handler(ev : Event):
    if ev['message_type'] == 'group':
        if int(ev['group_id']) not in [1021182194,714681974, 207751910, 702429547]:
            return
    else:
        return
    if len(ev['message']) == 0:
        return
    msg = str(ev.message)
    if msg.startswith('.help'):
        await rdhelphandler(ev)
        return
    if msg.startswith('.shoot'):
        await shootcommandhandler(ev)
        return
    if msg.startswith('.en'):
        await enhandler(ev)
        return
    if msg.startswith('.ti'):
        await ticommandhandler(ev)
        return
    if msg.startswith('.li'):
        await licommandhandler(ev)
        return
    if msg.startswith('.coc'):
        await cochandler(ev)
        return
    if msg.startswith('.sc'):
        await schandler(ev)
        return
    if msg.startswith('.r'):
        await rdcommandhandler(ev)
        return
    if msg.startswith('.st'):
        await sethandler(ev)
        return
    if msg.startswith('.show'):
        await showhandler(ev)
        return
    if msg.startswith('.sa'):
        await sahandler(ev)
        return
    if msg.startswith('.del'):
        await delhandler(ev)
        return
    
    
    
    