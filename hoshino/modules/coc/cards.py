from .investigator import Investigator
from .dices import Dices
from aiocqhttp import Event
from .messages import help_messages

import ujson as json

import os
import re
_cachepath = os.path.join("data", "coc_cards.json")


def get_group_id(event: Event):
    if event['message_type'] == 'group':
        return str(event['group_id'])
    elif event['message_type'] == 'guild':
        return str(event['channel_id'])
    else:
        return "0"


class Cards():
    def __init__(self) -> None:
        self.data: dict = {}

    def save(self) -> None:
        with open(_cachepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False)

    def load(self) -> None:
        with open(_cachepath, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def update(self, event: Event, inv_dict: dict, qid: str = "", save: bool = True):
        group_id = get_group_id(event)
        if not self.data.get(group_id):
            self.data[group_id] = {}
        self.data[group_id].update(
            {qid if qid else str(event["user_id"]): inv_dict})
        if save:
            self.save()

    def get(self, event: Event, qid: str = "") -> dict:
        group_id = get_group_id(event)
        if self.data.get(group_id):
            if self.data[group_id].get(qid if qid else str(event["user_id"])):
                return self.data[group_id].get(qid if qid else str(event["user_id"]))
        else:
            return None

    def delete(self, event: Event, qid: str = "", save: bool = True) -> bool:
        if self.get(event, qid=qid):
            if self.data[get_group_id(event)].get(qid if qid else str(event["user_id"])):
                self.data[get_group_id(event)].pop(
                    qid if qid else str(event["user_id"]))
            if save:
                self.save()
            return True
        return False

    def delete_skill(self, event: Event, skill_name: str, qid: str = "", save: bool = True) -> bool:
        if self.get(event, qid=qid):
            data = self.get(event, qid=qid)
            if data["skills"].get(skill_name):
                data["skills"].pop(skill_name)
                self.update(event, data, qid=qid, save=save)
                return True
        return False


cards = Cards()
cache_cards = Cards()
attrs_dict: dict = {
    "名字": ["name", "名字", "名称"],
    "年龄": ["age", "年龄"],
    "力量": ["str", "力量"],
    "体质": ["con", "体质"],
    "体型": ["siz", "体型"],
    "敏捷": ["dex", "敏捷"],
    "外貌": ["app", "外貌"],
    "智力": ["int", "智力", "灵感"],
    "意志": ["pow", "意志"],
    "教育": ["edu", "教育"],
    "幸运": ["luc", "幸运"],
    "理智": ["san", "理智", "san值", "理智值"],
    "魔法": ["mp", "魔法", "魔法值", "魔力", "魔力值"],
    "生命": ["lp", "hp", "生命", "生命值", "体力", "体力值"],
}

skills_dict: dict = {
    "计算机" : "计算机使用",
    "电脑" : "计算机使用",
    "信用" : "信用评级",
    "信誉" : "信用评级",
    "克苏鲁" : "克苏鲁神话",
    "cm" : "克苏鲁神话",
    "汽车" : "汽车驾驶",
    "驾驶" : "汽车驾驶",
    "汽车" : "汽车驾驶",
    "步枪": "步枪/霰弹枪",
    "霰弹枪": "步枪/霰弹枪",
    "步霰": "步枪/霰弹枪",
    "图书馆": "图书馆使用",
    "开锁": "锁匠",
    "撬锁": "锁匠",
    "自然学": "博物学",
    "领航": "导航",
    "重型操作": "操作重型机械",
    "重型机械": "操作重型机械",
    "重型": "操作重型机械",
    "重型机械操作": "操作重型机械",
    "重型机械操作": "操作重型机械",
}

def parse_update_list(args: str):
    ret = []
    l = len(args)
    i = 0
    while i < l:
        j = i
        while j + 1 < l:
            if not args[j].isdigit() and args[j + 1].isdigit(): break
            j += 1
        j += 1
        if j >= l: break
        k = j
        while k + 1 < l:
            if args[k].isdigit() and not args[k + 1].isdigit(): break
            k += 1
        k += 1
        ret.append((args[i:j], int(args[j:k])))
        i = k
    return ret


def set_handler(event: Event, args: str):
    if not args:
        if cache_cards.get(event):
            card_data = cache_cards.get(event)
            cards.update(event, inv_dict=card_data)
            inv = Investigator().load(card_data)
            return "成功从缓存保存人物卡属性：\n" + inv.output()
        else:
            return "未找到缓存数据，请先使用 .coc 指令生成角色"
    else:
        args = args.split("-")
        if cards.get(event):
            card_data = cards.get(event)
            inv = Investigator().load(card_data)
        else:
            return "未找到已保存数据，请先使用空白 .st 指令保存角色数据"
        toparse = ""
        if len(args) >= 2:
            inv.name = args[0]
            toparse = args[1]
        else:
            toparse = args[0]
        try:
            update_lst = parse_update_list(toparse)
        except:
            return "解析失败"
        print(update_lst)
        for x in update_lst:
            flag = 0
            for attr, alias in attrs_dict.items():
                if x[0] in alias:
                    if attr == "名字":
                        inv.__dict__[alias[0]] = str(x[1])
                    else:
                        try:
                            inv.__dict__[alias[0]] = int(x[1])
                        except ValueError:
                            return "请输入正整数属性数据"
                    cards.update(event, inv.__dict__)
                    flag = 1
            if flag == 1:
                continue
            try:
                if x[0] in skills_dict.keys():
                    inv.skills[skills_dict[x[0]]] = int(x[1])
                else:
                    inv.skills[x[0]] = int(x[1])
                cards.update(event, inv.__dict__)
            except ValueError:
                return "请输入正整数技能数据"
        return "数据更新成功, 如需查看数据请输入 .show 指令"


def show_handler(event: Event, args: str):
    r = []
    print(args, re.search(r"\[cq:at,qq=\d+\]", args))
    if not args:
        if cards.get(event):
            card_data = cards.get(event)
            inv = Investigator().load(card_data)
            r.append("使用中人物卡：\n" + inv.output())
        if cache_cards.get(event):
            card_data = cache_cards.get(event)
            inv = Investigator().load(card_data)
            r.append("已暂存人物卡：\n" + inv.output())
    elif args == "s":
        if cards.get(event):
            card_data = cards.get(event)
            inv = Investigator().load(card_data)
            r.append(inv.skills_output())
    elif re.search(r"\[cq:at,qq=\d+\]", args):
        qid = re.search(r"\[cq:at,qq=\d+\]", args).group()[10:-1]
        if cards.get(event, qid=qid):
            card_data = cards.get(event, qid=qid)
            inv = Investigator().load(card_data)
            r.append("查询到人物卡：\n" + inv.output())
            if args[0] == "s":
                r.append(inv.skills_output())
    if not r:
        r.append("无保存/暂存信息")
    return r


def del_handler(event: Event, args: str):
    r = []
    args = args.split(" ")
    for arg in args:
        if not arg:
            pass
        elif arg == "c" and cache_cards.get(event):
            if cache_cards.delete(event, save=False):
                r.append("已清空暂存人物卡数据")
        elif arg == "card" and cards.get(event):
            if cards.delete(event):
                r.append("已删除使用中的人物卡！")
        else:
            if cards.delete_skill(event, arg):
                r.append("已删除技能"+arg)
    if not r:
        r.append(help_messages.del_)
    return r


def sa_handler(event: Event, args: str):
    if not args:
        return help_messages.sa
    elif not cards.get(event):
        return "请先使用.st指令保存人物卡后再使用快速检定功能。"
    is_skill = 1
    for attr, alias in attrs_dict.items():
        if args in alias:
            args = alias[0]
            is_skill = 0
            break
    card_data = cards.get(event)
    dices = Dices()
    dices.a = True
    if not is_skill:
        dices.anum = card_data[args]
        return dices.roll()
    else:
        if not card_data.get("skills"):
            return "%s当前无任何技能数据。" % card_data["name"]
        if args in skills_dict.keys():
            args = skills_dict[args]
        if not card_data["skills"].get(args):
            return "%s当前没有名为「%s」的技能数据。" % (card_data["name"], args)
        dices.anum = card_data["skills"][args]
        return dices.roll()