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
    "??????": ["name", "??????", "??????"],
    "??????": ["age", "??????"],
    "??????": ["str", "??????"],
    "??????": ["con", "??????"],
    "??????": ["siz", "??????"],
    "??????": ["dex", "??????"],
    "??????": ["app", "??????"],
    "??????": ["int", "??????", "??????"],
    "??????": ["pow", "??????"],
    "??????": ["edu", "??????"],
    "??????": ["luc", "??????"],
    "??????": ["san", "??????", "san???", "?????????"],
    "??????": ["mp", "??????", "?????????", "??????", "?????????"],
    "??????": ["lp", "hp", "??????", "?????????", "??????", "?????????"],
}

skills_dict: dict = {
    "?????????" : "???????????????",
    "??????" : "???????????????",
    "??????" : "????????????",
    "??????" : "????????????",
    "?????????" : "???????????????",
    "cm" : "???????????????",
    "??????" : "????????????",
    "??????" : "????????????",
    "??????" : "????????????",
    "??????": "??????/?????????",
    "?????????": "??????/?????????",
    "??????": "??????/?????????",
    "?????????": "???????????????",
    "??????": "??????",
    "??????": "??????",
    "?????????": "?????????",
    "??????": "??????",
    "????????????": "??????????????????",
    "????????????": "??????????????????",
    "??????": "??????????????????",
    "??????????????????": "??????????????????",
    "??????????????????": "??????????????????",
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
            return "???????????????????????????????????????\n" + inv.output()
        else:
            return "???????????????????????????????????? .coc ??????????????????"
    else:
        args = args.split("-")
        if cards.get(event):
            card_data = cards.get(event)
            inv = Investigator().load(card_data)
        else:
            return "????????????????????????????????????????????? .st ????????????????????????"
        toparse = ""
        if len(args) >= 2:
            inv.name = args[0]
            toparse = args[1]
        else:
            toparse = args[0]
        try:
            update_lst = parse_update_list(toparse)
        except:
            return "????????????"
        print(update_lst)
        for x in update_lst:
            flag = 0
            for attr, alias in attrs_dict.items():
                if x[0] in alias:
                    if attr == "??????":
                        inv.__dict__[alias[0]] = str(x[1])
                    else:
                        try:
                            inv.__dict__[alias[0]] = int(x[1])
                        except ValueError:
                            return "??????????????????????????????"
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
                return "??????????????????????????????"
        return "??????????????????, ??????????????????????????? .show ??????"


def show_handler(event: Event, args: str):
    r = []
    print(args, re.search(r"\[cq:at,qq=\d+\]", args))
    if not args:
        if cards.get(event):
            card_data = cards.get(event)
            inv = Investigator().load(card_data)
            r.append("?????????????????????\n" + inv.output())
        if cache_cards.get(event):
            card_data = cache_cards.get(event)
            inv = Investigator().load(card_data)
            r.append("?????????????????????\n" + inv.output())
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
            r.append("?????????????????????\n" + inv.output())
            if args[0] == "s":
                r.append(inv.skills_output())
    if not r:
        r.append("?????????/????????????")
    return r


def del_handler(event: Event, args: str):
    r = []
    args = args.split(" ")
    for arg in args:
        if not arg:
            pass
        elif arg == "c" and cache_cards.get(event):
            if cache_cards.delete(event, save=False):
                r.append("??????????????????????????????")
        elif arg == "card" and cards.get(event):
            if cards.delete(event):
                r.append("?????????????????????????????????")
        else:
            if cards.delete_skill(event, arg):
                r.append("???????????????"+arg)
    if not r:
        r.append(help_messages.del_)
    return r


def sa_handler(event: Event, args: str):
    if not args:
        return help_messages.sa
    elif not cards.get(event):
        return "????????????.st??????????????????????????????????????????????????????"
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
            return "%s??????????????????????????????" % card_data["name"]
        if args in skills_dict.keys():
            args = skills_dict[args]
        if not card_data["skills"].get(args):
            return "%s?????????????????????%s?????????????????????" % (card_data["name"], args)
        dices.anum = card_data["skills"][args]
        return dices.roll()