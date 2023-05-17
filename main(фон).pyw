# -*- coding: utf-8 -*-
# pip install vk_api, regex, pyqiwip2p, ray
import locale
import math
import os
import pickle
import random
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread
from time import sleep

import ciso8601
import pytz
import requests
import vk_api
from PIL import Image
from pyqiwip2p import QiwiP2P
from vk_api import VkUpload
from vk_api.longpoll import VkEventType, VkLongPoll

import btns
import cfg
import msgs
import utils
from cfg import *
from models import *


class CreateLongPoll(VkLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                if str(e)[1] != '<':
                    print(e, end=" FROM MAIN.PY->MyLongPoll->listen\n")


def numbersToEmoji(num):
    x = ""
    for a in str(num):
        a = int(a)
        if a == 1:
            x = x.join("1️⃣ ")
        if a == 2:
            x = x.join("2️⃣ ")
        if a == 3:
            x = x.join("3️⃣ ")
        if a == 4:
            x = x.join("4️⃣ ")
        if a == 5:
            x = x.join("5️⃣ ")
        if a == 6:
            x = x.join("6️⃣ ")
        if a == 7:
            x = x.join("7️⃣ ")
        if a == 8:
            x = x.join("8️⃣ ")
        if a == 9:
            x = x.join("9️⃣ ")
        if a == 0:
            x = x.join("0️⃣")
    return x


def buildCharacter(name, acs='nothing.png', costumes='nothing.png', hairstyles='nothing.png', head='nothing.png',
                   shoes='nothing.png', tattoo='nothing.png', tshirts='nothing.png'):
    standart = Image.open('imgs/av/стандарт.jpg')
    if acs.lower().find('ничего') != -1:
        acs = 'nothing.png'
    if costumes.lower().find('ничего') != -1:
        costumes = 'nothing.png'
    if hairstyles.lower().find('ничего') != -1:
        hairstyles = 'nothing.png'
    if head.lower().find('ничего') != -1:
        head = 'nothing.png'
    if shoes.lower().find('ничего') != -1:
        shoes = 'nothing.png'
    if tattoo.lower().find('ничего') != -1:
        tattoo = 'nothing.png'
    if tshirts.lower().find('ничего') != -1:
        tshirts = 'nothing.png'
    if costumes == "nothing.png":
        img = Image.open(f'imgs/av/tattoo/{tattoo}')
        standart.paste(img, (0, 0), img)
        img = Image.open(f'imgs/av/hairstyles/{hairstyles}')
        standart.paste(img, (0, 0), img)
        img = Image.open(f'imgs/av/head/{head}')
        standart.paste(img, (0, 0), img)
        img = Image.open(f'imgs/av/shoes/{shoes}')
        standart.paste(img, (0, 0), img)
        img = Image.open(f'imgs/av/tshirts/{tshirts}')
        standart.paste(img, (0, 0), img)
        img = Image.open(f'imgs/av/acs/{acs}')
        standart.paste(img, (0, 0), img)
    else:
        img = Image.open(f'imgs/av/costumes/{costumes}')
        standart.paste(img, (0, 0))
    standart.save(f'trash/{name}.jpg')
    return f'trash/{name}.jpg'


class VkBot:
    def __init__(self):
        try:
            self.vk_session = vk_api.VkApi(token=vk_token)
            self.vk_session_user = vk_api.VkApi(token=vk_token_user)
            self.longpoll = CreateLongPoll(self.vk_session)
            self.vk = self.vk_session.get_api()
            self.db = None
            self.event = None
            self.upload = VkUpload(self.vk)
            self.attachment = ()
            self.x2 = {}
            self.x3 = {}
            self.x5 = {}
            self.x50 = {}
            self.endgame = 60
            with open('lastenergy.sav', 'rb') as data:
                self.lastenergy = pickle.load(data)[0]
                data.close()
        except Exception as e:
            print(e, end=" FROM MAIN.PY->VkBot->__init__\n")

    def upload_photo(self, photo):
        response = self.upload.photo_messages(photo)[0]
        return response['owner_id'], response['id'], response['access_key']

    def send_message(self, message, keyboard=None, uid=None, chat=None):
        if uid is None and chat is None:
            uid = self.db.vk_id
        if keyboard is not None:
            keyboard = keyboard.get_keyboard()
        if len(self.attachment) == 0:
            attachment = None
        elif type(self.attachment) == str:
            attachment = self.attachment
        else:
            attachment = f'photo{self.attachment[0]}_{self.attachment[1]}_{self.attachment[2]}'
        self.vk_session.method("messages.send", {
            'chat_id': chat,
            'user_id': uid,
            'message': message,
            'keyboard': keyboard,
            'attachment': attachment,
            'random_id': 0
        })

    def startingV(self):
        if self.event.text.lower() == "начать":
            self.send_message(msgs.start_msg()[0], btns.start_btn()[0])
            self.send_message(msgs.start_msg()[1], btns.start_btn()[1])
        if self.event.text == "❌ Отмена" or self.event.text == "🚪 Выйти":
            self.send_message("Действие отменено ❗", btns.start_btn()[1])
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                word="",
                randomword=""
            ))
        if self.event.text.lower() == "помощь":
            self.send_message(msgs.help_msg(), btns.help_btns())

    def bonusV(self):
        if self.event.text == "🎁 Бонус":
            if datetime.now() - self.db.lasttimeusedbonus >= timedelta(days=1):
                if random.randint(1, 100) <= 98:
                    con.execute(update(User).where(User.columns.vk_id == self.event.user_id).values(
                        money=self.db.money + 250000000000, gb=self.db.gb + 100, lasttimeusedbonus=datetime.now()))
                    self.send_message(msgs.bonus_msg(self.db.lasttimeusedbonus)[0])
                else:
                    con.execute(update(User).where(User.columns.vk_id == self.event.user_id).values(
                        pcase=self.db.pcase + 1, lasttimeusedbonus=datetime.now()))
                    self.send_message(msgs.bonus_msg(self.db.lasttimeusedbonus)[2])
            else:
                self.send_message(msgs.bonus_msg(self.db.lasttimeusedbonus)[1])

    def topV(self):
        if self.event.text.lower() == "🏆 топ":
            all_users_top = con.execute(select(User).order_by(desc(User.columns.crowns))).fetchall()
            all_users_top = [x._mapping for x in all_users_top]  # NOQA
            if len(all_users_top) < 10:
                counter = 10
            else:
                counter = len(all_users_top)
            top = [{"name": fr"[id{x.vk_id}|{x.name}]", "crowns": x.crowns, "money": x.money,
                    "place": list(all_users_top[:counter]).index(x)} for
                   x in all_users_top[:counter] if x.vk_id != 0]
            for _ in range(0, counter - len(top)):
                top.append({"name": "?", "crowns": 0, "money": 0, "place": 0})
            if len(all_users_top) > 1000:
                counter = 1000
            else:
                counter = len(all_users_top)
            usrp = None
            for a in range(0, counter):
                if self.db.vk_id == all_users_top[a].vk_id:
                    usrp = numbersToEmoji(a + 1)
            if usrp == "":
                usrp = "➡1️⃣0️⃣0️⃣0️⃣"
            top.insert(len(top),
                       {"name": self.db.name, "crowns": self.db.crowns, "money": self.db.money, "place": usrp})
            self.send_message(msgs.user_top_msg(top), btns.top_btn())
        if self.event.text.lower() == "⚔ топ кланов" or self.event.text.lower() == "клан топ":
            all_clans_top = con.execute(select(Clan).order_by(desc(Clan.columns.rating))).fetchall()
            all_clans_top = [x._mapping for x in all_clans_top]  # NOQA
            if len(all_clans_top) < 10:
                counter = 10
            else:
                counter = len(all_clans_top)
            if len(all_clans_top) != 0:
                top = [{"name": fr"[id{x.owner_id}|{x.name}]", "crowns": x.rating, "money": x.coffers,
                        "users": len(x.users.split("/")) - 1} for x in all_clans_top[:counter]]
            else:
                top = []
            for _ in range(0, counter - len(top)):
                top.append({"name": "?", "crowns": 0, "money": 0, "users": 0})
            self.send_message(msgs.clan_top_msg(top))
        if self.event.text.lower() == "🏆 топ гонщиков":
            all_users_top = con.execute(select(User).where(User.columns.car != "").
                                        order_by(desc(User.columns.rr))).fetchall()
            all_users_top = [x._mapping for x in all_users_top]  # NOQA
            if len(all_users_top) < 10:
                counter = 10
            else:
                counter = len(all_users_top)
            top = [{"name": fr"[id{x.vk_id}|{x.name}]", "cups": x.rr,
                    "place": list(all_users_top[:counter]).index(x)} for
                   x in all_users_top[:counter]]
            for _ in range(0, counter - len(top)):
                top.append({"name": "?", "cups": 0, "place": 0})
            if len(all_users_top) > 1000:
                counter = 1000
            else:
                counter = len(all_users_top)
            usrp = None
            for a in range(0, counter):
                if self.db.vk_id == all_users_top[a].vk_id:
                    usrp = numbersToEmoji(a + 1)
            if usrp == "":
                usrp = "➡1️⃣0️⃣0️⃣0️⃣"
            top.insert(len(top),
                       {"name": self.db.name, "cups": self.db.rr, "place": usrp})
            self.send_message(msgs.riders_top_msg(top))
        if self.event.text.lower() == "топ федералов":
            all_users_top = con.execute(select(User).where(User.columns.vk_id != 1).
                                        order_by(desc(User.columns.words))).fetchall()
            all_users_top = [x._mapping for x in all_users_top]  # NOQA
            if len(all_users_top) < 10:
                counter = 10
            else:
                counter = len(all_users_top)
            top = [{"name": fr"[id{x.vk_id}|{x.name}]", "words": x.words,
                    "place": list(all_users_top[:counter]).index(x)} for
                   x in all_users_top[:counter]]
            for _ in range(0, counter - len(top)):
                top.append({"name": "?", "words": 0, "place": 0})
            if len(all_users_top) > 1000:
                counter = 1000
            else:
                counter = len(all_users_top)
            usrp = None
            for a in range(0, counter):
                if self.db.vk_id == all_users_top[a].vk_id:
                    usrp = numbersToEmoji(a + 1)
            if usrp == "":
                usrp = "➡1️⃣0️⃣0️⃣0️⃣"
            top.insert(len(top),
                       {"name": self.db.name, "words": self.db.words, "place": usrp})
            self.send_message(msgs.federalstopMsg(top))

    def clanV(self):
        if self.event.text.lower() == "клан помощ" or self.event.text.lower() == "клан помощь":
            self.send_message(msgs.clan_help_msg())
        if self.event.text.lower() in {"⚔ клан", "кланы", "клан"}:
            if self.db.clan == "":
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
            else:
                self.send_message(msgs.clan_msg(utils.getOrCreateClanById(self.db.clan)))
        if self.event.text.lower()[:13] == "клан создать ":
            if self.db.money >= 100000000000:
                if self.db.clan == "":
                    clan = utils.getOrCreateClanById(self.event.user_id, True)
                    con.execute(update(Clan).where(Clan.columns.owner_id == self.event.user_id).
                                values(name=self.event.text.lower()[13:], users=f"{self.db.vk_id}/"))
                    self.send_message(
                        fr"""Вы успешно создали клан под названием «{self.event.text.lower()[13:]}», ему присвоен ID {clan.id}. 👋🏻""")
                    user = utils.getOrCreateUserById(self.event.user_id)
                    con.execute(update(User).where(User.columns.vk_id == self.event.user_id).
                                values(clan=str(self.db.vk_id), money=user.money - 100000000000))
                else:
                    self.send_message("Вы уже состоите в клане❗")
            else:
                self.send_message(f"Вам не хватает ${'{0:,}'.format(100000000000 - self.db.money).replace(',', '.')} ❌")
        if self.event.text.lower() == "клан удалить":
            if int(self.db.clan) == self.event.user_id:
                clan = utils.getOrCreateClanById(self.db.clan)
                for x in clan.users.split("/")[:len(clan.users.split("/")) - 1]:
                    conection.execute(update(User).where(User.columns.vk_id == x).values(clan=""))
                con.execute(delete(Clan).where(Clan.columns.owner_id == self.event.user_id))
                self.send_message("Вы успешно удалили клан❗")
            elif self.db.clan == "":
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
            else:
                self.send_message("Вы должны быть основателем клана чтобы его удалить! ❌")
        if self.event.text.lower()[:14] == "клан изменить ":
            if self.db.clan == str(self.event.user_id):
                if 17 > len(self.event.text.lower()[14:]) > 2:
                    conection.execute(update(Clan).where(Clan.columns.vk_id == self.event.user_id).
                                      values(name=self.event.text[14:]))
                    self.send_message(
                        f"Вы успешно изменили имя своего клана на [id{self.db.vk_id}|{self.event.text[14:]}]✅")
                else:
                    self.send_message("Вы указали некорректное имя!(имя должно не превышать 16 символов и быть не"
                                      "меньше 3-х)❌")
            elif self.db.clan == "":
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
            else:
                self.send_message("Вы не можете менять имя клана если вы не являетесь его основателем!❌")
        if self.event.text.lower()[:16] == "клан пригласить ":
            try:
                if int(self.db.clan) == self.event.user_id:
                    users = utils.getOrCreateClanById(self.event.user_id).users
                    users = len(users.split("/")[:len(users.split("/")) - 1])
                    if users < 50:
                        try:
                            invited = utils.getOrCreateUserById(self.event.text.lower()[16:], False)
                            clan = utils.getOrCreateClanById(self.event.user_id)
                            if clan.users.find(str(invited.vk_id)) == -1:
                                if invited.clan_invites.find(self.db.clan) == -1:
                                    con.execute(update(User).where(User.columns.vk_id == invited.vk_id).
                                                values(clan_invites=invited.clan_invites + f"{self.db.clan}/"))
                                    self.send_message(
                                        f"Вы успешно пригласили в клан [id{invited.vk_id}|{invited.name}]!")
                                    self.send_message(
                                        f"Вас пригласили в клан [id{utils.getOrCreateClanById(self.db.clan).owner_id}|"
                                        f"{utils.getOrCreateClanById(self.db.clan).name}]!", uid=invited.vk_id)
                                else:
                                    self.send_message("Пользователю уже отправлено приглашение! ❌")
                            else:
                                self.send_message("Пользователь уже состоит в клане! ❌")
                        except:
                            traceback.print_exc()
                            self.send_message("Вам нужно пригласить игрока по его ID вконтакте(только цифры) ❌")
                    else:
                        self.send_message("В вашем клане 50/50 пользователей! ❌")
                elif self.db.clan == "":
                    self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
                else:
                    self.send_message("Чтобы пригласить Пользователя в клан нужно быть администратором! ❌")
            except ValueError:
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
        if self.event.text.lower()[:15] == "клан исключить ":
            if int(self.db.clan) == self.event.user_id:
                if utils.getOrCreateClanById(self.db.vk_id).users.find(self.event.text.lower()[15:]) != -1:
                    con.execute(update(User).where(User.columns.vk_id == self.event.text.lower()[15:]).values(clan=''))
                    invites = utils.getOrCreateClanById(self.db.vk_id).users.split('/')
                    invites = [f"{x}/" for x in invites if x != self.event.text.lower()[15:] and x != ""]
                    invites = "".join(invites)
                    con.execute(update(Clan).where(Clan.columns.owner_id == self.event.user_id).
                                values(users=invites))
                    self.send_message("Пользователь успешно исключен")
                    self.send_message("Вас исключили из клана!", uid=self.event.text.lower()[15:])
                else:
                    self.send_message("Пользователь не найден! ❌")
            elif self.db.clan == "":
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
            else:
                self.send_message("Только администратор может исключать пользователей! ❌")
        if self.event.text.lower() == "клан выйти":
            if self.db.clan == "":
                leaving = utils.getOrCreateClanById(self.event.user_id).users.split("/")
                leaving = [f"{x}/" for x in leaving if x != self.db.vk_id and x != ""]
                leaving = ''.join(leaving)
                con.execute(update(Clan).where(Clan.columns.owner_id == self.db.clan).values(users=leaving))
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(clan=''))
                self.send_message("Вы вышли из клана. ✔")
            else:
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
        if self.event.text.lower()[:14] == "клан вступить ":
            if self.db.clan == "":
                acu = self.event.text.lower()[14:]
                if self.db.clan_invites.find(f"{acu}/") != -1:
                    acc = con.execute(select(Clan).where(Clan.columns.id == acu)).fetchone()._mapping  # NOQA
                    user_clan_invites = utils.getOrCreateUserById(self.db.clan).clan_invites.split("/")
                    user_clan_invites = [f"{x}/" for x in user_clan_invites if x != str(acu) and x != ""]
                    user_clan_invites = ''.join(user_clan_invites)
                    con.execute(update(User).where(User.columns.vk_id == self.event.user_id).values(
                        clan=acc.owner_id, clan_invites=user_clan_invites))
                    con.execute(
                        update(Clan).where(Clan.columns.id == acu).values(users=acc.users + f"{self.event.user_id}/"))
                    self.send_message("Вы успешно вступили в клан. ✔")
                else:
                    self.send_message("Вам не поступало приглашение в этот клан. ❌")
            else:
                self.send_message("Bы не можете вступить в несколько кланов сразу. ❌")
        if self.event.text.lower() == "клан казна":
            if self.db.clan != "":
                coffers = utils.getOrCreateClanById(self.db.clan).coffers_history.split('/')
                coffers = [x.split(".") for x in coffers]
                coffers.pop()
                coffers = [{"id": h[0], "name": h[1], "summ": h[2]} for h in coffers]
                self.send_message(msgs.top_clan_coffers(coffers))
            else:
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
        if self.event.text.lower()[:11] == "клан казна ":
            try:
                summ = int(self.event.text.lower()[11:])
                if self.db.money >= summ:
                    if self.db.clan != "":
                        clan_c = utils.getOrCreateClanById(self.db.clan)
                        if summ <= clan_c.coffers + clan_c.base * 100000000000000:
                            coffer_hist = clan_c.coffers_history + f"{self.event.user_id}.{self.db.name}.{summ}/"
                            con.execute(update(Clan).where(Clan.columns.owner_id == self.db.clan).values(
                                coffers=clan_c.coffers + summ, coffers_history=coffer_hist))
                            self.send_message(
                                f"Вы пополнили казну клана на {'{0:,}'.format(summ).replace(',', '.')}$ 💵")
                            con.execute(update(User).where(User.columns.vk_id == self.event.user_id).values(
                                money=self.db.money - summ))
                        else:
                            self.send_message("Казна переполнена! ❌")
                    else:
                        self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
                else:
                    self.send_message(f"У тебя не хватает {'{0:,}'.format(summ - self.db.money).replace(',', '.')}$ ❌")
            except:
                self.send_message("Tакой команды не существует, отправь «помощь» чтобы узнать мои команды. 😖")
        if self.event.text.lower() == "клан состав":
            if self.db.clan != "":
                clan_users = utils.getOrCreateClanById(self.event.user_id)
                clan_name = clan_users.name
                clan_users = clan_users.users.split("/")
                clan_users = [{"id": x, "name": utils.getOrCreateUserById(int(x)).name} for x in clan_users if x != ""]
                self.send_message(msgs.clan_composition(clan_users, clan_name))
            else:
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
        if self.event.text.lower() == "клан магазин":
            if self.db.clan != "":
                self.send_message(msgs.clan_shop())
            else:
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
        if self.event.text.lower()[:13] == "клан магазин ":
            if self.db.clan != "":
                order = self.event.text.lower()[13:].split()
                if len(order) == 1:
                    order.append('1')
                if len(order) == 2:
                    order[1] = int(order[1])
                    clan = utils.getOrCreateClanById(self.db.clan)
                    shield = ciso8601.parse_datetime(clan.shield).timestamp()
                    shield = datetime.fromtimestamp(shield + 86400)
                    if order[0] == '1':
                        if self.db.money >= 10000000000:
                            if clan.knights + order[1] < 10000 * clan.base:
                                con.execute(update(Clan).where(Clan.columns.owner_id == self.db.clan).values(
                                    knights=clan.knights + order[1], power=clan.power + 12))
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    money=self.db.money - 10000000000))
                                self.send_message(
                                    f"Вы купили Рыцарь {order[1]} шт. за  {'{0:,}'.format(15000000000 * order[1]).replace(',', '.')}$ 💵")
                            else:
                                self.send_message("Вы достигли лимита по количеству Рыцарей! ❌")
                        else:
                            self.send_message(f"У тебя не хватает. ❌")
                    if order[0] == '2':
                        if self.db.money >= 15000000000:
                            if clan.archers + order[1] < 10000 * clan.base:
                                con.execute(update(Clan).where(Clan.columns.owner_id == self.db.clan).values(
                                    archers=clan.archers + order[1], power=clan.power + 21))
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    money=self.db.money - 15000000000))
                                self.send_message(
                                    f"Вы купили Лучник {order[1]} шт.  за {'{0:,}'.format(15000000000 * order[1]).replace(',', '.')} $ 💵")
                            else:
                                self.send_message("Вы достигли лимита по количеству Лучников! ❌")
                        else:
                            self.send_message(f"У тебя не хватает. ❌")
                    if order[0] == '3':
                        if self.db.gb >= 250:
                            if clan.balloons + order[1] < 10000 * clan.base:
                                if clan.base >= 5:
                                    con.execute(update(Clan).where(Clan.columns.owner_id == self.db.clan).values(
                                        balloons=clan.balloons + order[1], power=clan.power + 74))
                                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                        gb=self.db.gb - 250))
                                    self.send_message(
                                        f"Вы купили Воздушный Шар {order[1]} шт.  за {250 * order[1]} GB 💵")
                                else:
                                    self.send_message("Воздушный Шар доступен с 5 уровня базы. ❌")
                            else:
                                self.send_message("Вы достигли лимита по количеству Воздушных Шаров! ❌")
                        else:
                            self.send_message(f"У тебя не хватает. ❌")
                    if order[0] == '4':
                        if self.db.gb >= 1000:
                            if clan.dragons + order[1] < 10000 * clan.base:
                                if clan.base >= 10:
                                    con.execute(update(Clan).where(Clan.columns.owner_id == self.db.clan).values(
                                        dragons=clan.dragons + order[1], power=clan.power + 456))
                                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                        gb=self.db.gb - 1000))
                                    self.send_message(
                                        f"Вы купили Дракон {order[1]} шт.  за {'{0:,}'.format(1000 * order[1]).replace(',', '.')} GB 💵")
                                else:
                                    self.send_message("Дракон доступен с 10 уровня базы. ❌")
                            else:
                                self.send_message("Вы достигли лимита по количеству Драконов! ❌")
                        else:
                            self.send_message(f"У тебя не хватает. ❌")
                    if order[0] == '5':
                        if self.db.money >= 100000000000:
                            con.execute(update(Clan).where(Clan.columns.owner_id == self.db.clan).values(
                                shield=shield))
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money - 100000000000))
                            self.send_message(
                                f"Вы купили {order[1]} дней Щита за {'{0:,}'.format(100000000000 * order[1]).replace(',', '.')} $ 💵")
                        else:
                            self.send_message(f"У тебя не хватает. ❌")
                else:
                    self.send_message("Такой команды не существует, отправь «помощь» чтобы узнать мои команды. 😖")
            else:
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
        if self.event.text.lower() == "клан атака":
            if self.db.clan == str(self.event.user_id):
                clan = utils.getOrCreateClanById(self.db.clan)
                clans = con.execute(Clan.select().where(
                    # (Clan.columns.owner_id != self.db.vk_id) &
                    (Clan.columns.power <= clan.power)
                ).order_by(Clan.columns.coffers)).fetchall()
                clans = [x._mapping for x in clans]  # NOQA
                for x in clans[:]:
                    if ciso8601.parse_datetime(x['shield']) > datetime.now():
                        clans.remove(x)
                clans.reverse()
                if len(clans) != 0:
                    attacked_clan = clans[0]
                    clan = utils.getOrCreateClanById(self.db.clan)
                    randomwarrior = random.randint(1, 100)
                    stealing_coffers = math.ceil(attacked_clan['coffers'] / 100 * 30)
                    msg = f"Ваш клан потерпел поражение перед {clan.name}, вы потеряли:"
                    if attacked_clan['power'] > 0:
                        if 50 > randomwarrior > 0:
                            con.execute(update(Clan).where(Clan.columns.id == attacked_clan['id']).values(
                                coffers=attacked_clan['coffers'] - stealing_coffers,
                                knights=attacked_clan['knights'] - math.ceil(attacked_clan['knights'] / 100 * 10),
                                power=attacked_clan['power'] - math.ceil(attacked_clan['knights'] / 100 * 10) * 12,
                                loses=attacked_clan['loses'] + 1,
                                shield=datetime.fromtimestamp(datetime.now().timestamp() + 86400)
                            ))
                            msg = msg + f"\n-{math.ceil(attacked_clan['knights'] / 100 * 10)} рыцарей❌"
                        if 80 >= randomwarrior >= 50:
                            con.execute(update(Clan).where(Clan.columns.id == attacked_clan['id']).values(
                                coffers=attacked_clan['coffers'] - stealing_coffers,
                                archers=attacked_clan['archers'] - math.ceil(attacked_clan['archers'] / 100 * 10),
                                power=attacked_clan['power'] - math.ceil(attacked_clan['archers'] / 100 * 10) * 21,
                                loses=attacked_clan['loses'] + 1,
                                shield=datetime.fromtimestamp(datetime.now().timestamp() + 86400)
                            ))
                            msg = msg + f"\n-{math.ceil(attacked_clan['archers'] / 100 * 5)} лучников❌"
                        if 95 >= randomwarrior > 80:
                            con.execute(update(Clan).where(Clan.columns.id == attacked_clan['id']).values(
                                coffers=attacked_clan['coffers'] - stealing_coffers,
                                balloons=attacked_clan['balloons'] - math.ceil(attacked_clan['balloons'] / 100 * 10),
                                power=attacked_clan['power'] - math.ceil(attacked_clan['balloons'] / 100 * 10) * 74,
                                loses=attacked_clan['loses'] + 1,
                                shield=datetime.fromtimestamp(datetime.now().timestamp() + 86400)
                            ))
                            msg = msg + f"\n-{math.ceil(attacked_clan['balloons'] / 100 * 2)} воздушных шаров❌"
                        if 100 >= randomwarrior > 95:
                            con.execute(update(Clan).where(Clan.columns.id == attacked_clan['id']).values(
                                coffers=attacked_clan['coffers'] - stealing_coffers,
                                dragons=attacked_clan['dragons'] - math.ceil(attacked_clan['dragons'] / 100 * 10),
                                power=attacked_clan['power'] - math.ceil(attacked_clan['dragons'] / 100 * 10) * 456,
                                loses=attacked_clan['loses'] + 1,
                                shield=datetime.fromtimestamp(datetime.now().timestamp() + 86400)
                            ))
                            msg = msg + f"\n-{math.ceil(attacked_clan['dragons'] / 100 * 1)} драконов❌"
                    msg = msg + f"\n{stealing_coffers}$ из казны клана❌\nВы получили щит на 1 день."
                    con.execute(update(Clan).where(Clan.columns.owner_id == self.event.user_id).values(
                        coffers=utils.getOrCreateClanById(self.event.user_id).coffers + stealing_coffers,
                        wins=utils.getOrCreateClanById(self.event.user_id).wins + 1,
                        rating=utils.getOrCreateClanById(self.event.user_id).rating + 1
                    ))
                    self.send_message(
                        f"Вы успешно получили {'{0:,}'.format(stealing_coffers).replace(',', '.')}$ из казны атакованного клана. ✔")
                    self.send_message(msg, uid=attacked_clan['owner_id'])
                else:
                    self.send_message("Не удалось найти подходящий для атаки клан. ❌")
            elif self.db.clan == "":
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
            else:
                self.send_message("Вы не можете атаковать если вы не являетесь основателем клана! ❌")
        if self.event.text.lower() == "клан уровень":
            if self.db.clan != "":
                self.send_message(msgs.baseUpMsg(utils.getOrCreateClanById(self.db.clan).base), btns.baseUp_btn())
            else:
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')
        if self.event.text.lower() == "клан улучшить":
            if self.db.clan != "":
                clan = utils.getOrCreateClanById(self.db.clan)
                if self.db.gb >= 10000 * clan.base:
                    con.execute(update(Clan).where(Clan.columns.owner_id == self.db.clan).values(
                        base=clan.base + 1
                    ))
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        gb=self.db.gb - 10000 * clan.base
                    ))
                    self.send_message("Вы успешно улучшили уровень базы.")
                else:
                    self.send_message(
                        f"У тебя не хватает {'{0:,}'.format(10000 * clan.base - self.db.gb).replace(',', '.')}")
            else:
                self.send_message('Вы не состоите в клане!\nИнформация по командам: "клан помощь"🔔')

    def clothesV(self):
        if self.event.text.lower().find('тест') == -1:
            if self.event.text.lower() == "👔 одежда" or self.event.text.lower() == "одежда":
                self.send_message(msgs.clothesMsg(), btns.clothes_btns())
            if self.event.text.lower() == "прическа":
                self.send_message(msgs.hairstyleMsg(), btns.backToClothes_btn())
            if self.event.text.lower() == "тату":
                self.send_message(msgs.tattooMsg(), btns.backToClothes_btn())
            if self.event.text.lower() == "голова":
                self.send_message(msgs.headMsg(), btns.backToClothes_btn())
            if self.event.text.lower() == "футболка":
                self.send_message(msgs.tshortMsg(), btns.backToClothes_btn())
            if self.event.text.lower() == "костюм":
                self.send_message(msgs.costumeMsg(), btns.backToClothes_btn())
            if self.event.text.lower() == "обувь":
                self.send_message(msgs.shoesMsg(), btns.backToClothes_btn())
            if self.event.text.lower() == "аксессуары" or self.event.text.lower() == "аксесуары":
                self.send_message(msgs.accessoriesMsg(), btns.backToClothes_btn())
            if self.event.text.lower().find('прическа ') != -1:
                name = list(cfg.hairstyles)[int(self.event.text[9:]) - 1]
                num = cfg.hairstyles[name]
                if list(num)[0] == 'money':
                    if self.db.money >= num['money']:
                        if self.db.hairstyle != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money - num['money'], hairstyle=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['money']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
                elif list(num)[0] == 'gb':
                    if self.db.gb >= num['gb']:
                        if self.db.hairstyle != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                gb=self.db.gb - num['gb'], hairstyle=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['gb']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
            if self.event.text.lower().find('тату ') != -1:
                name = list(cfg.tattoes)[int(self.event.text[5:]) - 1]
                num = cfg.tattoes[name]
                if list(num)[0] == 'money':
                    if self.db.money >= num['money']:
                        if self.db.tattoo != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money - num['money'], tattoo=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['money']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
                elif list(num)[0] == 'gb':
                    if self.db.gb >= num['gb']:
                        if self.db.tattoo != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                gb=self.db.gb - num['gb'], tattoo=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['gb']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
            if self.event.text.lower().find('голова ') != -1:
                name = list(cfg.heads)[int(self.event.text[7:]) - 1]
                num = cfg.heads[name]
                if list(num)[0] == 'money':
                    if self.db.money >= num['money']:
                        if self.db.head != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money - num['money'], head=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['money']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
                elif list(num)[0] == 'gb':
                    if self.db.gb >= num['gb']:
                        if self.db.head != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                gb=self.db.gb - num['gb'], head=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['gb']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
            if self.event.text.lower().find('футболка ') != -1:
                name = list(cfg.tshorts)[int(self.event.text[9:]) - 1]
                num = cfg.tshorts[name]
                if list(num)[0] == 'money':
                    if self.db.money >= num['money']:
                        if self.db.tshort != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money - num['money'], tshort=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['money']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
                elif list(num)[0] == 'gb':
                    if self.db.gb >= num['gb']:
                        if self.db.tshort != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                gb=self.db.gb - num['gb'], tshort=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['gb']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
            if self.event.text.lower().find('костюм ') != -1:
                name = list(cfg.costumes)[int(self.event.text[7:]) - 1]
                num = cfg.costumes[name]
                if list(num)[0] == 'money':
                    if self.db.money >= num['money']:
                        if self.db.costume != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money - num['money'], costume=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['money']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
                elif list(num)[0] == 'gb':
                    if self.db.gb >= num['gb']:
                        if self.db.costume != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                gb=self.db.gb - num['gb'], costume=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['gb']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
            if self.event.text.lower().find('акс ') != -1:
                name = list(cfg.accessories)[int(self.event.text[4:]) - 1]
                num = cfg.accessories[name]
                if list(num)[0] == 'money':
                    if self.db.money >= num['money']:
                        if self.db.accessories != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money - num['money'], accessories=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['money']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
                elif list(num)[0] == 'gb':
                    if self.db.gb >= num['gb']:
                        if self.db.accessories != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                gb=self.db.gb - num['gb'], accessories=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['gb']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
            if self.event.text.lower().find('обувь ') != -1:
                name = list(cfg.shoes)[int(self.event.text[6:]) - 1]
                num = cfg.shoes[name]
                if list(num)[0] == 'money':
                    if self.db.money >= num['money']:
                        if self.db.shoes != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money - num['money'], shoes=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['money']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
                elif list(num)[0] == 'gb':
                    if self.db.gb >= num['gb']:
                        if self.db.shoes != name:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                gb=self.db.gb - num['gb'], shoes=name
                            ))
                            self.send_message(
                                f"Вы успешно купили {name} за {'{0:,}'.format(num['gb']).replace(',', '.')}$")
                        else:
                            self.send_message('На вас уже это надето!')
                    else:
                        self.send_message('У тебя не хватает.')
        else:
            try:
                acs = costume = hairstyle = head = shoes = tattoo = tshirt = 'nothing.png'
                if self.event.text.lower().find('акс тест ') != -1:
                    num = int(self.event.text[9:])
                    if num != 1:
                        acs = f'{list(cfg.accessories)[num - 1]}.png'
                        name = acs.replace('.png', '')
                    else:
                        name = list(cfg.accessories)[num - 1]
                        acs = 'nothing.png'
                elif self.event.text.lower().find('костюм тест ') != -1:
                    num = int(self.event.text[12:])
                    if num != 1:
                        costume = f'{list(cfg.costumes)[num - 1]}.jpg'
                        name = costume.replace('.png', '')
                    else:
                        name = list(cfg.costumes)[num - 1]
                        costume = 'nothing.png'
                elif self.event.text.lower().find('прическа тест ') != -1 or self.event.text.lower().find(
                        'причёска тест ') != -1:
                    num = int(self.event.text[14:])
                    if num != 1:
                        hairstyle = f'{list(cfg.hairstyles)[num - 1]}.png'
                        name = hairstyle.replace('.png', '')
                    else:
                        name = list(cfg.hairstyles)[num - 1]
                        hairstyle = 'nothing.png'
                elif self.event.text.lower().find('голова тест ') != -1:
                    num = int(self.event.text[12:])
                    if num != 1:
                        head = f'{list(cfg.heads)[num - 1]}.png'
                        name = head.replace('.png', '')
                    else:
                        name = list(cfg.heads)[num - 1]
                        head = 'nothing.png'
                elif self.event.text.lower().find('обувь тест ') != -1:
                    num = int(self.event.text[11:])
                    if num != 1:
                        shoes = f'{list(cfg.shoes)[num - 1]}.png'
                        name = shoes.replace('.png', '')
                    else:
                        name = list(cfg.shoes)[num - 1]
                        shoes = 'nothing.png'
                elif self.event.text.lower().find('тату тест ') != -1:
                    num = int(self.event.text[10:])
                    if num != 1:
                        tattoo = f'{list(cfg.tattoes)[num - 1]}.png'
                        name = tattoo.replace('.png', '')
                    else:
                        name = list(cfg.tattoes)[num - 1]
                        tattoo = 'nothing.png'
                    if name == "xui":
                        name = "***"
                elif self.event.text.lower().find('футболка тест ') != -1:
                    num = int(self.event.text[14:])
                    if num != 1:
                        tshirt = f'{list(cfg.tshorts)[num - 1]}.png'
                        name = tshirt.replace('.png', '')
                    else:
                        name = list(cfg.tshorts)[num - 1]
                        tshirt = 'nothing.png'
                else:
                    name = None
                if name is not None:
                    self.send_message("Примерка началась..")
                    self.attachment = self.upload_photo(buildCharacter(self.db.vk_id, acs=acs, costumes=costume,
                                                                       hairstyles=hairstyle, head=head, shoes=shoes,
                                                                       tattoo=tattoo, tshirts=tshirt))
                    self.send_message(f"Вы примерили {name}👕")
                else:
                    self.attachment = ()
            except IndexError:
                self.send_message("Эта позиция не доступна для примерки.")
            self.attachment = ()
            try:
                os.remove(f'trash/{self.db.vk_id}.jpg')
            except FileNotFoundError:
                pass

    def businessV(self):
        if self.event.text.lower() == "💼 бизнес":
            if self.db.business == "":
                self.send_message("У Вас нет бизнеса! ❌\nДля покупки бизнеса отправьте «Бизнесы»")
            else:
                self.attachment = self.upload_photo(f"imgs/business/{self.db.business}.jpg")
                self.send_message(msgs.businessMsg(utils.getOrCreateUserById(self.db.vk_id)),
                                  btns.business_btns(self.db.businessupgrade))
                self.attachment = ()
        if self.event.text.lower() == "бизнесы":
            self.send_message(msgs.buybusinessMsg())
        if self.event.text.lower()[:7] == "бизнес " and self.event.text.lower()[:14] != "бизнес нанять ":
            try:
                num = int(self.event.text[7])
                if self.db.business == "":
                    name = list(cfg.businesses)[num - 1]
                    if self.db.money >= cfg.businesses[name]['cost']:
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            money=self.db.money - cfg.businesses[name]['cost'],
                            business=name,
                            businessmoney=0,
                            businessupgrade=False,
                            businessworkers=0,
                            businesslastsalary=datetime.now()
                        ))
                        self.send_message(
                            f"Вы успешно купили «{name}» 🤑\n💰 Ваш баланс: {'{0:,}'.format(self.db.money).replace(',', '.')}$")
                    else:
                        self.send_message("У тебя не хватает.")
                else:
                    self.send_message("У Вас уже есть бизнес! 🙌\nЧтобы продать его отправьте «Продать бизнес»")
            except:
                self.send_message("Я вас не понял🧐")
        if self.event.text.lower()[:14] == "бизнес нанять ":
            if self.db.business != "":
                if self.db.businessworkers < 100:
                    try:
                        val = int(self.event.text.lower()[14:])
                        if val > 100 - self.db.businessworkers:
                            val = 100 - self.db.businessworkers
                        if self.db.money >= val * 400:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money - val * 400,
                                businessworkers=self.db.businessworkers + val
                            ))
                            self.send_message(
                                f"Вы наняли {val} рабочих за {'{0:,}'.format(val * 400).replace(',', '.')}$ 🤑")
                        else:
                            self.send_message("У тебя не хватает.")
                    except:
                        self.send_message("Я вас не понял🧐")
                else:
                    self.send_message('У Вас работает максимальное количество людей ❌')
            else:
                self.send_message("У Вас нет бизнеса! ❌\nДля покупки бизнеса отправьте «Бизнесы»")
        if self.event.text.lower() == "💰 бизнес снять":
            if self.db.business != "":
                salary = (datetime.now().timestamp() - self.db.businesslastsalary.timestamp()) // 3600
                salary = int(salary * cfg.businesses[self.db.business]['salary'])
                if self.db.businessworkers < 100:
                    salary = int(salary / 2)
                if self.db.businessupgrade:
                    salary = int(salary * 2.5)
                if salary > 0:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        businesslastsalary=datetime.now(),
                        money=self.db.money + salary,
                        businesspaymentval=self.db.businesspaymentval + 1
                    ))
                    self.send_message(
                        f"Bы сняли с бизнеса {'{0:,}'.format(salary).replace(',', '.')}$ 😯\n💰 На руках: {'{0:,}'.format(self.db.money).replace(',', '.')}")
                else:
                    self.send_message("Hа счету бизнеса нет денег. ❌")
            else:
                self.send_message("У Вас нет бизнеса! ❌\nДля покупки бизнеса отправьте «Бизнесы»")
        if self.event.text.lower() == "⬆ бизнес улучшить":
            if self.db.business != "":
                if not self.db.businessupgrade:
                    cost = cfg.businesses[self.db.business]['cost'] * 2
                    if self.db.money >= cost:
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            businessupgrade=True,
                            money=self.db.money - cost
                        ))
                        self.send_message(
                            f"Вы успешно улучшили «{self.db.business}»☺\n💰 Ваш баланс: {self.db.money}$\n")
                    else:
                        self.send_message(
                            f"Тебе не хватает {'{0:,}'.format(self.db.money - cost).replace(',', '.')}$.\n💰 На руках: {'{0:,}'.format(self.db.money).replace(',', '.')}")
                else:
                    self.send_message("Bаш бизнес максимально улучшен! ❌")
            else:
                self.send_message("У Вас нет бизнеса! ❌\nДля покупки бизнеса отправьте «Бизнесы»")
        if self.event.text.lower() == "продать бизнес":
            if self.db.business != "":
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    business="",
                    businessupgrade=False,
                    businessworkers=0,
                    businesslastsalary=datetime.now(),
                    businessmoney=0,
                    money=self.db.money + (cfg.businesses[self.db.business]['cost'] / 4)
                ))
                self.send_message(
                    f"Вы успешно продали свой бизнес.\n💰 На руках: {'{0:,}'.format(self.db.money).replace(',', '.')}")
            else:
                self.send_message("У Вас нет бизнеса! ❌\nДля покупки бизнеса отправьте «Бизнесы»")

    def farmV(self):
        if self.event.text.lower() == "💾 ферма" or self.event.text.lower() == "фермы":
            msg = msgs.farmMsg(self.db, self.event.text.lower())
            if msg.find("Ha ваших фермах еще нет биткоинов.") != -1:
                self.attachment = self.upload_photo("imgs/farms/waiting.jpg")
            elif msg.find("Вы собрали со своих ферм") != -1:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    farmpaymentval=self.db.farmpaymentval + 1
                ))
                self.attachment = self.upload_photo("imgs/farms/getbtc.jpg")
            self.send_message(msg)
            self.attachment = ()
        if self.event.text.lower() == "продать биткоин":
            if self.db.btc > 0:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    btc=0,
                    money=self.db.money + self.db.btc * 22593000
                ))
                self.attachment = self.upload_photo("imgs/farms/getbtc.jpg")
                self.send_message(msgs.sellbtcMsg(self.db))
                self.attachment = ()
            else:
                self.send_message("Hа вашем балансе нет биткоинов. ❌")
        if self.event.text.lower()[:6] == "фермы ":
            num = int(self.event.text.lower()[6]) - 1
            farm = cfg.farms[list(cfg.farms)[num]]
            if self.db.money >= farm['cost']:
                db = self.db
                if db.asic == db.dragonmintt1 == db.fm2018bt400 == db.genesis == db.gigawatt == db.gorilla == 0:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        lastsellingbtc=datetime.now()
                    ))
                if list(cfg.farms)[num] == 'asic':
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        asic=self.db.asic + 1,
                        money=self.db.money - farm['cost']
                    ))
                elif list(cfg.farms)[num] == 'dragonmintt1':
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        dragonmintt1=self.db.dragonmintt1 + 1,
                        money=self.db.money - farm['cost']
                    ))
                elif list(cfg.farms)[num] == 'fm2018bt400':
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        fm2018bt400=self.db.fm2018bt400 + 1,
                        money=self.db.money - farm['cost']
                    ))
                elif list(cfg.farms)[num] == 'genesis':
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        genesis=self.db.genesis + 1,
                        money=self.db.money - farm['cost']
                    ))
                elif list(cfg.farms)[num] == 'gigawatt':
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        gigawatt=self.db.gigawatt + 1,
                        money=self.db.money - farm['cost']
                    ))
                elif list(cfg.farms)[num] == 'gorilla':
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        gorilla=self.db.gorilla + 1,
                        money=self.db.money - farm['cost']
                    ))
                self.send_message(msgs.buyfarmMsg(list(cfg.farms)[num], self.db.money - farm['cost']))
            else:
                self.send_message(f"У вас не хватает, наличными {'{0:,}'.format(self.db.money).replace(',', '.')}$ ❌")

    def printerV(self):
        with open('lasttick.sav', 'rb') as data:
            lasttick = pickle.load(data)[0].timestamp()
            data.close()
        if datetime.now().timestamp() - lasttick >= 3600:
            ticksval = (datetime.now().timestamp() - lasttick) // 3600
            nextlasttick = datetime.fromtimestamp(lasttick + (ticksval * 3600))
            userswithprinter = con.execute(select(User).where(User.columns.printer != "")).fetchall()
            userswithprinter = [x._mapping for x in userswithprinter]  # NOQA
            for _ in range(int(ticksval)):
                for user in userswithprinter:
                    con.execute(update(User).where(User.columns.vk_id == user['vk_id']).values(
                        cartridge=user['cartridge'] - int(ticksval)
                    ))
            lasttick = nextlasttick
            with open('lasttick.sav', 'wb') as data:
                pickle.dump([lasttick], data)
                data.close()
        userswith0cartridge = con.execute(select(User).where(User.columns.cartridge == 0)).fetchall()
        userswith0cartridge = [x._mapping for x in userswith0cartridge]  # NOQA
        for user in userswith0cartridge:
            con.execute(update(User).where(User.columns.vk_id == user['vk_id']).values(
                printer="",
                cartridge=100,
                lasttakemoney=datetime.now()
            ))
            self.send_message("В вашем принтере закончились чернила, его заклинило и он сломался. :(",
                              uid=user['vk_id'])
        if self.event.text.lower() == "принтер":
            self.send_message(msgs.printerMsg(self.db)[0], msgs.printerMsg(self.db)[1])
        if self.event.text.lower() == "принтеры":
            self.send_message(msgs.allprintersMsg())
        if self.event.text.lower()[:9] == "принтеры ":
            if self.db.printer == "":
                num = int(self.event.text.lower()[9]) - 1
                printer_name = list(cfg.printers)[num]
                printer = cfg.printers[printer_name]
                if self.db.money >= printer['cost']:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money - printer['cost'],
                        printer=printer_name,
                        lasttakemoney=datetime.now()
                    ))
                    self.send_message(
                        f"Bы купили «{printer_name}» за {'{0:,}'.format(printer['cost']).replace(',', '.')}$ ☺")
                else:
                    self.send_message(
                        f"У тебя не хватает {'{0:,}'.format(printer['cost'] - self.db.money).replace(',', '.')}$ ❌")
            else:
                self.send_message(f"У Вас уже есть принтер ({self.db.printer})! 🙌\n"
                                  "Чтобы продать его отправьте «Продать принтер»")
        if self.event.text.lower() == "продать принтер":
            if self.db.printer != "":
                money = self.db.money + (cfg.printers[self.db.printer]['cost'] / 100 * 10)
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    printer="",
                    cartridge=100,
                    lasttakemoney=datetime.now(),
                    money=money
                ))
                self.send_message(
                    f"Вы успешно продали {self.db.printer} ✅\n💰 На руках: {'{0:,}'.format(money).replace(',', '.')}")
            else:
                self.send_message(msgs.printerMsg(self.db, False))
        if self.event.text.lower().find("принтер заправить") != -1:
            if self.db.printer != "":
                if self.db.cartridge != 100:
                    if self.db.money >= 1000:
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            money=self.db.money - 1000,
                            cartridge=100
                        ))
                        self.send_message(f"Bы успешно заправили принтер «{self.db.printer}» за 1.000$ 🎨")
                    else:
                        self.send_message(
                            f"У тебя не хватает {'{0:,}'.format(1000 - self.db.money).replace(',', '.')}$ ❌")
                else:
                    self.send_message("Bаш принтер не требует заправки. 🎨")
            else:
                self.send_message(msgs.printerMsg(self.db, False))
        if self.event.text.lower().find("принтер снять") != -1:
            if self.db.printer != "":
                if datetime.now().timestamp() - self.db.lasttakemoney.timestamp() >= 3600:
                    moneyrange = (datetime.now().timestamp() - self.db.lasttakemoney.timestamp()) // 3600
                    money = int(cfg.printers[self.db.printer]['salary'] * moneyrange)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money + money,
                        lasttakemoney=datetime.now()
                    ))
                    self.send_message(f"Bы сняли с принтера {'{0:,}'.format(money).replace(',', '.')}$ 💰")
            else:
                self.send_message(msgs.printerMsg(self.db)[0])

    def entertainingV(self):
        if self.event.text.lower() == "развлекательное":
            self.send_message(msgs.entertainingMsg())
        if self.event.text.lower() == "игры":
            self.send_message(msgs.gamesMsg())
        if self.event.text.lower() == "разное":
            self.send_message(msgs.otherMsg())
        if self.event.text.lower() == "анекдот":
            self.send_message(cfg.jokes[random.randint(0, len(cfg.jokes) - 1)])
        if self.event.text.lower()[:10] == "переверни ":
            self.send_message(f'Держи, {self.event.text.lower()[:9:-1]}')
        if self.event.text.lower()[:4] == "шар ":
            self.send_message(random.choice(['🔮 Знаки говорят - "да"', '🔮 Знаки говорят - "нет"',
                                             '🔮 Определённо да', '🔮 Определённо нет', '🔮 Да', '🔮 Нет']))
        if self.event.text.lower()[:7] == "выбери ":
            self.send_message(f'Конечно {random.choice(self.event.text.lower()[7:].split(" или "))}!')
        if self.event.text.lower()[:5] == "инфа ":
            self.send_message(
                f"[id{self.db.vk_id}|{self.db.name}], "
                f"{random.choices(['Мне кажется', 'шанс этого', 'мне кажется около', 'вероятность'])[0]} "
                f"{random.randint(0, 100)}%")
        if self.event.text.lower()[:5] == "реши ":
            try:
                self.send_message(f"Ответ: {eval(self.event.text.lower()[5:])}")
            except:
                self.send_message("Использование: «реши [1+2*3]» ❌")
        if self.event.text.lower() == "курс":
            self.send_message("Курс биткоина\n💸 Покупка: 23.313$\n🔋 Продажа: 22.925$")
        if self.event.text.lower() == "баланс":
            self.send_message(
                f"[id{self.db.vk_id}|{self.db.name}], на руках: {'{0:,}'.format(self.db.money).replace(',', '.')}$ 💵\n💸 {'{0:,}'.format(self.db.gb).replace(',', '.')} GB")

    def carsV(self):
        if self.event.text.lower() == "🐴 машина":
            if self.db.car == "":
                self.send_message("У Вас нет машины.\nСписок всех машин по команде: «машины» 🚗")
            else:
                self.send_message(msgs.carMsg(self.db), btns.car_btns())
        if self.event.text.lower() == "машины":
            self.send_message(msgs.carsMsg())
        if self.event.text.lower()[:7] == "машины ":
            if self.db.car == "":
                num = int(self.event.text.lower()[7:]) - 1
                car_name = list(cfg.cars)[num]
                car = cfg.cars[car_name]
                if self.db.money >= car['cost']:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        car=car_name,
                        money=self.db.money - car['cost'],
                        maxv=cfg.cars[car_name]['max'],
                        do100=cfg.cars[car_name]['do100'],
                        hp=cfg.cars[car_name]['hp']
                    ))
                    self.send_message(msgs.buycarMsg(car_name))
                else:
                    self.send_message(
                        f"У тeбя нe хватаeт, наличными {'{0:,}'.format(self.db.money).replace(',', '.')}$ ❌")
            else:
                self.send_message(f"У Вас уже есть машина ({self.db.car})! 🙌")
        if self.event.text.lower() == "⬆ машина улучшить":
            if self.db.car != "":
                self.send_message(msgs.upgradecarMsg(self.db))
            else:
                self.send_message("У Вас нет машины.\nСписок всех машин по команде: «машины» 🚗")
        if self.event.text.lower()[:16] == "машина улучшить ":
            if self.db.car != "":
                part = self.event.text.lower()[16:]
                if len(part) > 2:
                    if part == "шины":
                        if self.db.tires < 3:
                            if self.db.money >= cfg.cars[self.db.car]['cost'] / 2.5:
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    tires=self.db.tires + 1,
                                    money=self.db.money - (cfg.cars[self.db.car]['cost'] / 2.5),
                                    do100=self.db.do100 - 0.15
                                ))
                                self.send_message(f"Шины были улучшены [{self.db.tires + 1}/3] ⚒")
                            else:
                                self.send_message("У тебя не хватает.")
                        else:
                            self.send_message("Шины максимально улучшены. ⚒")
                    if part == "диски":
                        if self.db.rims < 3:
                            if self.db.money >= cfg.cars[self.db.car]['cost'] / 2.5:
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    rims=self.db.rims + 1,
                                    money=self.db.money - (cfg.cars[self.db.car]['cost'] / 2.5)
                                ))
                                self.send_message(f"Диски были улучшены [{self.db.rims + 1}/3] ⚒")
                            else:
                                self.send_message("У тебя не хватает.")
                        else:
                            self.send_message("Диски максимально улучшены. ⚒")
                    if part == "двигатель":
                        if self.db.engine < 3:
                            if self.db.money >= cfg.cars[self.db.car]['cost'] / 2.5:
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    engine=self.db.engine + 1,
                                    money=self.db.money - (cfg.cars[self.db.car]['cost'] / 2.5),
                                    hp=self.db.hp + 31,
                                    do100=self.db.do100 - 0.2
                                ))
                                self.send_message(f"Двигатель был улучшен [{self.db.engine + 1}/3] ⚒")
                            else:
                                self.send_message("У тебя не хватает.")
                        else:
                            self.send_message("Двигатель максимально улучшен. ⚒")
                    if part == "бензобак":
                        if self.db.fueltank < 3:
                            if self.db.money >= cfg.cars[self.db.car]['cost'] / 2.5:
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    fueltank=self.db.fueltank + 1,
                                    money=self.db.money - (cfg.cars[self.db.car]['cost'] / 2.5),
                                    maxv=self.db.maxv + 8,
                                    do100=self.db.do100 - 0.01
                                ))
                                self.send_message(f"Бензобак был улучшен [{self.db.fueltank + 1}/3] ⚒")
                            else:
                                self.send_message("У тебя не хватает.")
                        else:
                            self.send_message("Бензобак максимально улучшен. ⚒")
                    if part == "подвеску":
                        if self.db.suspension < 3:
                            if self.db.money >= cfg.cars[self.db.car]['cost'] / 2.5:
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    suspension=self.db.suspension + 1,
                                    money=self.db.money - (cfg.cars[self.db.car]['cost'] / 2.5),
                                    maxv=self.db.maxv + 5,
                                    do100=self.db.do100 - 0.01
                                ))
                                self.send_message(f"Подвеска была улучшена [{self.db.suspension + 1}/3] ⚒")
                            else:
                                self.send_message("У тебя не хватает.")
                        else:
                            self.send_message("Подвеска максимально улучшена. ⚒")
                    if part == "тормоза":
                        if self.db.brakes < 10:
                            if self.db.money >= cfg.cars[self.db.car]['cost'] / 2.5:
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    brakes=self.db.brakes + 1,
                                    money=self.db.money - (cfg.cars[self.db.car]['cost'] / 2.5),
                                    maxv=self.db.maxv + 5,
                                    do100=self.db.do100 - 0.01
                                ))
                                self.send_message(f"Тормоза были улучшены [{self.db.brakes + 1}/10] ⚒")
                            else:
                                self.send_message("У тебя не хватает.")
                        else:
                            self.send_message("Тормоза максимально улучшены. ⚒")
                    if part == "турбины":
                        if self.db.turbines < 5:
                            if self.db.money >= cfg.cars[self.db.car]['cost'] / 2.5:
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    turbines=self.db.turbines + 1,
                                    money=self.db.money - (cfg.cars[self.db.car]['cost'] / 2.5),
                                    maxv=self.db.maxv + 24,
                                    do100=self.db.do100 - 0.1
                                ))
                                self.send_message(f"Турбины были улучшены [{self.db.turbines + 1}/5] ⚒")
                            else:
                                self.send_message("У тебя не хватает.")
                        else:
                            self.send_message("Турбины максимально улучшены. ⚒")
                    if part == "управление":
                        if self.db.control < 20:
                            if self.db.money >= cfg.cars[self.db.car]['cost'] / 2.5:
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    control=self.db.control + 1,
                                    money=self.db.money - (cfg.cars[self.db.car]['cost'] / 2.5),
                                    maxv=self.db.maxv + 8,
                                    do100=self.db.do100 - 0.01
                                ))
                                self.send_message(f"Управление было улучшено [{self.db.control + 1}/20] ⚒")
                            else:
                                self.send_message("У тебя не хватает.")
                        else:
                            self.send_message("Управление максимально улучшено. ⚒")
                    if part == "чип":
                        if self.db.chip < 1:
                            if self.db.money >= cfg.cars[self.db.car]['cost'] / 2.5:
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    chip=self.db.chip + 1,
                                    money=self.db.money - (cfg.cars[self.db.car]['cost'] / 2.5),
                                    do100=self.db.do100 - 0.01,
                                    hp=self.db.hp + 100
                                ))
                                self.send_message(f"Чип был улучшен [{self.db.chip + 1}/1] ⚒")
                            else:
                                self.send_message("У тебя не хватает.")
                        else:
                            self.send_message("Чип максимально улучшен. ⚒")
            else:
                self.send_message("У Вас нет машины.\nСписок всех машин по команде: «машины» 🚗")
        if self.event.text.lower().find("гонка") != -1:
            if self.db.car != "":
                choosencar = con.execute(select(User).where(User.columns.car != "")).fetchall()
                if len(choosencar) != 1:
                    choosencar = choosencar[random.randint(0, len(choosencar) - 1)]._mapping  # NOQA
                    if datetime.now().timestamp() - self.db.lastrace.timestamp() > 600:
                        self.send_message(msgs.raceMsg(choosencar))
                        cups = 0
                        if (choosencar['hp'] + choosencar['maxv']) * (choosencar['do100'] / 100) < (
                                self.db.hp + self.db.maxv) * (self.db.do100 / 100):
                            self.send_message("Вы первыми пришли к финишу! +300 🏆", btns.car_btns())
                            cups = 300
                            winstreek = self.db.racewinstreek + 1
                        elif (choosencar['hp'] + choosencar['maxv']) * (choosencar['do100'] / 100) > (
                                self.db.hp + self.db.maxv) * (self.db.do100 / 100):
                            self.send_message("Первым к финишу пришёл противник! -300 🏆\n"
                                              "⚙ Улучшайте свой автомобиль чтобы стать быстрее.", btns.car_btns())
                            if self.db.cups > 0:
                                cups = -300
                            winstreek = 0
                        else:
                            winstreek = self.db.racewinstreek
                            self.send_message("Ничья!", btns.car_btns())
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            lastrace=datetime.now(),
                            cups=self.db.rr + cups,
                            racewinstreek=winstreek
                        ))
                        con.execute(update(User).where(User.columns.vk_id == choosencar['vk_id']).values(
                            lastrace=datetime.now()))
                    else:
                        seconds = datetime.now().timestamp() - self.db.lastrace.timestamp()
                        self.send_message(f"Машина проходит техосмотр, подождите "
                                          f"{(seconds % 3600) // 60} мин. {seconds % 60} сек.! 🚧")
                else:
                    self.send_message("Подходящих машин не нашлось. ❌\n⏳ Повторите попытку позже.")
            else:
                self.send_message("У Вас нет машины.\nСписок всех машин по команде: «машины» 🚗")
        if self.event.text.lower() == "продать машину":
            if self.db.car != "":
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    car="",
                    money=int(cfg.cars[self.db.car]['cost'] / 2.5)
                ))
                self.send_message(
                    f"Вы продали «{self.db.car}» за {'{0:,}'.format(int(cfg.cars[self.db.car]['cost'] / 2.5)).replace(',', '.')}$")
            else:
                self.send_message("У Вас нет машины.\nСписок всех машин по команде: «машины» 🚗")
        if self.event.text.lower() == "машина госномер":
            if self.db.car != "":
                if self.db.num == "":
                    self.send_message(f"[id{self.db.vk_id}|{self.db.name}], нажми кнопку ниже для смены госномера. 🎫",
                                      btns.gonum_btn())
                else:
                    self.send_message(f"[id{self.db.vk_id}|{self.db.name}], нажми кнопку ниже для смены госномера.\n"
                                      f"🎫 Ваш госномер: {self.db.num}",
                                      btns.gonum_btn())
            else:
                self.send_message("У Вас нет машины.\nСписок всех машин по команде: «машины» 🚗")
        if self.event.text == "🎫 Сменить госномер":
            letters = "".join(
                [random.choice(["А", "В", "Е", "К", "М", "Н", "О", "Р", "С", "Т", "X", "У"]) for _ in range(3)])
            numbers = "".join([random.choice(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]) for _ in range(3)])
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                num=f'{letters[:2]}{numbers}{letters[2]} {random.choice(cfg.regions)}'
            ))
            self.send_message(f'Hа авто был установлен госномер: {letters[:2]}{numbers}{letters[2]}'
                              f' {random.choice(cfg.regions)} 🎫\n'
                              f' Ваш баланс: {"{0:,}".format(self.db.money).replace(",", ".")}$', btns.gonum_btn())
        if self.event.text == "💼 Чемодан" or self.event.text.lower() == "чемодан":
            if len(self.db.numbers) in {0, 1}:
                self.send_message("У тебя нету госномеров в чемодане. ❌", btns.putgonum())
            else:
                msg = f'Tвои госномера в чемодане:\nnumbers\n❗ Достать госномер: "чемодан [ID]"'
                allnumbers = self.db.numbers.split('/')
                allnumbers.pop()
                for x in range(len(allnumbers)):
                    msg = msg.replace('numbers', f'{numbersToEmoji(x + 1)} {allnumbers[x]}\nnumbers')
                msg = msg.replace("numbers", "")
                self.send_message(msg, btns.putgonum())
        if self.event.text.lower() == "положить госномер":
            if self.db.num != "":
                self.send_message(f"Ты положил госномер {self.db.num} в чемодан.", btns.gonum_btn())
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    num="",
                    numbers=self.db.numbers + f"{self.db.num}/"
                ))
            else:
                self.send_message("У тебя нет госномера.", btns.gonum_btn())
        if self.event.text.lower()[:8] == "чемодан ":
            if len(self.db.numbers) not in {0, 1}:
                allnumbers = self.db.numbers.split('/')
                allnumbers.pop()
                try:
                    num = allnumbers[int(self.event.text[8:]) - 1]
                    self.send_message(f"Вы достали госномер {num}.")
                    allnumbers = "".join([f"{x}/" for x in allnumbers if x != num])
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        num=num,
                        numbers=allnumbers
                    ))
                except:
                    self.send_message("Вы написали некорректный номер")
            else:
                self.send_message("У вас нет этого номера.")

    def bossesV(self):
        if self.event.text.lower()[:5] == "#босс" and (
                self.db.vk_id == 731937175 or self.db.vk_id == 746110579 or self.db.vk_id == 776036799):
            text = self.event.text.lower().split('\n')
            text.pop(0)
            r = requests.get(
                self.vk_session.method("messages.getById", {"message_ids": self.event.message_id})['items'][0][
                    'attachments'][0]['photo']['sizes'][-1]['url'])
            with open('boss/img.jpg', 'wb') as f:
                f.write(r.content)
            boss = {'name': text[0].replace('имя: ', ''), 'hp': int(text[1].replace('хп: ', ''))}
            boss['hpleft'] = boss['hp']
            with open('boss.sav', 'wb') as data:
                pickle.dump([boss], data)
                data.close()
            con.execute(update(User).values(power=1, dmg=0))
        with open('boss.sav', 'rb') as data:
            boss = pickle.load(data)[0]
            data.close()
        if self.event.text.lower() == "босс":
            if len(boss) > 1:
                self.attachment = self.upload_photo("boss/img.jpg")
                self.send_message(msgs.bossMsg(self.db, boss), btns.boss_btns())
                self.attachment = ()
            else:
                self.send_message("Босс скоро появится, следи за новостями в группе. 🙁")
        if self.event.text.lower() == "босс атака" or self.event.text == "🔨 Босс атака":
            with open('boss.sav', 'rb') as data:
                boss = pickle.load(data)[0]
                data.close()
            if len(boss) > 1:
                boss['hpleft'] = boss['hpleft'] - self.db.power
                with open('boss.sav', 'wb') as data:
                    pickle.dump([boss], data)
                    data.close()
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    dmg=self.db.dmg + self.db.power
                ))
                self.send_message(f"Вы нанесли по боссу {self.db.power} урона")
            else:
                self.send_message("Босс скоро появится, следи за новостями в группе. 🙁")
        if self.event.text.lower() == "босс сила" or self.event.text == "👊 Босс сила":
            if self.db.money >= self.db.power * 100000000000:
                with open('boss.sav', 'rb') as data:
                    boss = pickle.load(data)[0]
                    data.close()
                if len(boss) > 1:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money - (self.db.power * 100000000000),
                        power=self.db.power + 1
                    ))
                    self.send_message(f"Вы улучшили свою атаку до {self.db.power + 1}")
                else:
                    self.send_message("Босс скоро появится, следи за новостями в группе. 🙁")
            else:
                self.send_message("У тебя не хватает.")
        if len(boss) > 1:
            with open('boss.sav', 'rb') as data:
                boss = pickle.load(data)[0]
                data.close()
            if boss['hpleft'] <= 0:
                users = [x._mapping for x in con.execute(select(User).where(User.columns.dmg > 0)).fetchall()]
                for user in users:
                    self.send_message(
                        f"Босса убили, награды были разделены по урону!(+{'{0:,}'.format(user['dmg'] * 2500000).replace(',', '.')})",
                        uid=user['vk_id'])
                    con.execute(update(User).where(User.columns.vk_id == user['vk_id']).values(
                        money=user['money'] + (user['dmg'] * 2500000),
                        power=1,
                        dmg=0
                    ))
                os.remove("boss/img.jpg")
                boss = {}
                with open('boss.sav', 'wb') as data:
                    pickle.dump([boss], data)
                    data.close()

    def utilsV(self):
        if self.event.text.lower().find("репорт") != -1:
            self.send_message(f"Новый репорт: {self.event.text}", uid=731937175)
        if self.db.vk_id in {731937175, 7461105799}:
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                money=999999999999999999,
                gb=999999999999999999
            ))
        if datetime.now().timestamp() - self.db.lastpension.timestamp() >= 14 * 24 * 60 * 60:
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                pension=self.db.pension + 500000000000,
                lastpension=datetime.now()
            ))

    def otherV(self):
        if self.event.text.lower() == "профиль":
            character = buildCharacter(f'{self.db.vk_id}.png', f'{self.db.accessories}.png', f'{self.db.costume}.jpg',
                                       f'{self.db.hairstyle}.png', f'{self.db.head}.png', f'{self.db.shoes}.png',
                                       f'{self.db.tattoo}.png', f'{self.db.tshort}.png')
            self.attachment = self.upload_photo(character)
            self.send_message(msgs.profileMsg(self.db))
            self.attachment = ()
            os.remove(character)
        if self.event.text.lower() == "уровень":
            self.send_message(msgs.lvlqMsg(self.db))
        if self.event.text.lower() == "уровень повысить":
            self.send_message("Bы готовы начать игру сначала? Баланс, биткойны, банк, рейтинг и кейсы будут обнулены."
                              f'📢 Чтобы повысить уровень, напишите "Уровень повысить {self.db.lvl + 1}"')
        if self.event.text.lower() == f"уровень повысить {self.db.lvl + 1}":
            cost = 50000000000000 + (25000000000000 * (self.db.lvl + 1))
            if self.db.money >= cost:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    lasttimeusedbonus=datetime.now() - timedelta(seconds=86400),
                    money=0,
                    gb=0,
                    crowns=0,
                    clan="",
                    clan_invites="",
                    hairstyle="Ничего",
                    tattoo="Ничего",
                    head="Ничего",
                    tshort="Ничего",
                    costume="Ничего",
                    shoes="Ничего",
                    accessories="Ничего",
                    business="",
                    businessmoney=0,
                    businessupgrade=False,
                    businessworkers=0,
                    businesslastsalary=datetime.now(),
                    asic=0,
                    dragonmintt1=0,
                    fm2018bt400=0,
                    genesis=0,
                    gigawatt=0,
                    gorilla=0,
                    lastsellingbtc=datetime.now().replace(year=2040),
                    btc=0,
                    printer="",
                    cartridge=100,
                    lasttakemoney=datetime.now(),
                    car="",
                    tires=1,
                    rims=1,
                    engine=1,
                    fueltank=1,
                    suspension=1,
                    brakes=1,
                    turbines=1,
                    control=1,
                    chip=0,
                    num="",
                    hp=0,
                    maxv=0,
                    do100=0,
                    rr=0,
                    lastrace=datetime.now(),
                    power=1,
                    dmg=0,
                    lvl=self.db.lvl + 1,
                    xp=0,
                    yacht="",
                    airplane="",
                    helicopter="",
                    home="",
                    pet="",
                    petlvl=0,
                    petsatiety=0,
                    petjoy=0,
                    petage=datetime.now(),
                    petlasthike=datetime.now(),
                    phone="",
                    pc="",
                    status="user",
                    potion="",
                    energy=10,
                    iron=0,
                    gold=0,
                    diamonds=0,
                    matter=0,
                    antimatter=0,
                    one="❌",
                    two="❌",
                    three="❌",
                    four="❌",
                    five="❌",
                    six="❌",
                    seven="❌",
                    eight="❌",
                    nine="❌",
                    ten="❌",
                    eleven="❌",
                    tradewinstreek=0,
                    cupwinstreek=0,
                    casinowinstreek=0,
                    cubewinstreek=0,
                    businesspaymentval=0,
                    farmpaymentval=0,
                    caseopenval=0,
                    transfermoneyval=0,
                    racewinstreek=0
                ))
                self.send_message("Вы успешно повысили уровень. Поздравления!")
                if self.db.lvl + 1 == 30:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        dcase=self.db.dcase + 100
                    ))
            else:
                self.send_message(
                    f"Для повышения на {self.db.lvl + 1} уровень, вам нужно иметь на балансе {'{0:,}'.format(cost).replace(',', '.')}$ 📶")
        if self.event.text.lower() == "пенсия":
            self.attachment = self.upload_photo("imgs/pension.jpg")
            self.send_message(f'Дата регистрации: {self.db.registrationdate.strftime("%d.%m.%Y")} 📅\n'
                              f"💳 Размер вашей пенсии: {'{0:,}'.format(self.db.pension).replace(',', '.')}$"
                              '\n🌍 Получить пенсию: "Пенсия снять"')
            self.attachment = ()
        if self.event.text.lower() == "пенсия снять":
            nextpension = datetime.fromtimestamp(self.db.lastpension.timestamp() - 1209600). \
                strftime("приходите за новой %d.%m.%Y  в %H:%M:%S ⏰")
            if self.db.pension != 0:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    pension=0,
                    money=self.db.money + self.db.pension
                ))
                self.send_message(
                    f"Bы получили пенсию в размере {'{0:,}'.format(self.db.pension).replace(',', '.')}$, {nextpension}")
            else:
                self.send_message(f"Получать пенсию можно раз в две недели, {nextpension}")
        if self.event.text.lower()[:4] == "банк":
            if len(self.event.text.lower().split()) > 2:
                summ = int(self.event.text.lower().split()[2].replace(".", "").replace("к", "000").replace(",", ""))
                if self.db.bank >= summ:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        bank=self.db.bank - summ,
                        money=self.db.money + summ
                    ))
                    self.send_message(
                        f"Вы сняли {summ}$ с банка\n💰 На руках: {'{0:,}'.format(self.db.money - summ).replace(',', '.')}$")
                else:
                    self.send_message(
                        f"У тебя не xватает, на счету в банке {'{0:,}'.format(self.db.bank).replace(',', '.')}$ ❌")
            elif len(self.event.text.lower().split()) > 1:
                summ = int(self.event.text.lower().split()[1].replace(".", "").replace("к", "000").replace(",", ""))
                if self.db.money > summ:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        bank=self.db.bank + summ,
                        money=self.db.money - summ
                    ))
                    self.send_message(
                        f"Вы положили в банк {'{0:,}'.format(summ).replace(',', '.')}$ 🤑\n💰 На руках {'{0:,}'.format(self.db.money + summ).replace(',', '.')}$\n"
                        f"💳 В банке {'{0:,}'.format(self.db.bank + summ).replace(',', '.')}$")
                else:
                    self.send_message(
                        f"У тебя не xватает, наличкой {'{0:,}'.format(self.db.money).replace(',', '.')}$ ❌")
            else:
                self.send_message(
                    f"Hа балансе в банке {'{0:,}'.format(self.db.bank).replace(',', '.')}$\n✍🏻 Введите «Банк [кол-во]» для пополнения")
        if self.event.text.lower() == "действия":
            self.send_message('''Bы можете совершать действия над другими игроками бота. Список возможных действий: 

💋 Поцеловать [имя] 
🤗 Обнять [имя] 
🧙 Заколдовать [имя] 
🦷 Укусить [имя] 
🖐 Шлепнуть [имя] 
🐈 Погладить [имя] 
🦵 Пнуть [имя] 
🍌 Отсосать [имя] 
🌭 Отлизать [имя] 
🦍 Трахнуть [имя] 
⛲ Обоссать [имя] 
🍾 Отравить [имя] 
👊 Уебать [имя] 
🐔 Изнасиловать [имя] 
🔪 Кастрировать [имя] 
👺 Испугать [имя] 

💬 Например: "Ударить Максима"''')

    def shopV(self):
        if self.event.text.lower() == "магазин":
            self.send_message(msgs.shopMsg())
        if self.event.text.lower() == "яхты":
            self.send_message(msgs.yachtsMsg())
        if self.event.text.lower()[:5] == "яхта ":
            num = int(self.event.text.lower()[5:]) - 1
            yachtname = list(cfg.yachts)[num]
            yachtcost = cfg.yachts[yachtname]
            if self.db.money >= yachtcost:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    yacht=yachtname,
                    money=self.db.money - yachtcost
                ))
                self.send_message(f"Bы купили «{yachtname}» за {'{0:,}'.format(yachtcost).replace(',', '.')}$ 😯")
            else:
                self.send_message("у тебя не хватает.")
        if self.event.text.lower().replace("ё", "е") == "самолеты":
            self.send_message(msgs.airplanesMsg())
        if self.event.text.lower().replace("ё", "е")[:8] == "самолет ":
            num = int(self.event.text.lower()[8:]) - 1
            airplanename = list(cfg.airplanes)[num]
            airplanecost = cfg.airplanes[airplanename]
            if self.db.money >= airplanecost:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    airplane=airplanename,
                    money=self.db.money - airplanecost
                ))
                self.send_message(f"Bы купили «{airplanename}» за {'{0:,}'.format(airplanecost).replace(',', '.')}$ 😯")
            else:
                self.send_message("у тебя не хватает.")
        if self.event.text.lower() == "вертолеты" or self.event.text.lower() == "вертолёты":
            self.send_message(msgs.helicoptersMsg())
        if self.event.text.lower()[:9] == "вертолет " or self.event.text.lower()[:9] == "вертолёт ":
            num = int(self.event.text.lower()[9:]) - 1
            helicoptername = list(cfg.helicopters)[num]
            helicoptercost = cfg.helicopters[helicoptername]
            if self.db.money >= helicoptercost:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    helicopter=helicoptername,
                    money=self.db.money - helicoptercost
                ))
                self.send_message(
                    f"Bы купили «{helicoptername}» за {'{0:,}'.format(helicoptercost).replace(',', '.')}$ 😯")
            else:
                self.send_message("у тебя не хватает.")
        if self.event.text.lower() == "дома":
            self.send_message(msgs.homesMsg())
        if self.event.text.lower()[:4] == "дом ":
            num = int(self.event.text.lower()[4:]) - 1
            homename = list(cfg.homes)[num]
            homecost = cfg.homes[homename]
            if self.db.money >= homecost:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    home=homename,
                    money=self.db.money - homecost
                ))
                self.send_message(f"Вы купили «{homename}» за {'{0:,}'.format(homecost).replace(',', '.')}$ 😯")
            else:
                self.send_message("У тебя не хватает.")
        if self.event.text.lower() == "питомцы" or (self.db.pet == "" and self.event.text.lower() == "питомец"):
            self.send_message(msgs.petsMsg())
        if self.event.text.lower()[:8] == "питомец ":
            num = int(self.event.text.lower()[8:]) - 1
            petname = list(cfg.pets)[num]
            petcost = cfg.pets[petname]
            if self.db.money >= petcost:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    money=self.db.money - petcost,
                    pet=petname,
                    petlvl=1,
                    petsatiety=100,
                    petjoy=100,
                    petage=datetime.now()
                ))
                self.send_message(f"Bы успешно купили себе в питомцы «{petname}», "
                                  f'отправляйте питомца в поход и прокачивайте её уровень.')
            else:
                self.send_message("У тебя не хватает.")
        if self.event.text.lower() == "продать питомца":
            if self.db.pet != "":
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    pet="",
                    money=self.db.money + (cfg.pets[self.db.pet] / 10)
                ))
                self.send_message(
                    f"Вы продали питомца. На руках {'{0:,}'.format(self.db.money + (cfg.pets[self.db.pet] / 10)).replace(',', '.')}")
            else:
                self.send_message("У вас нет питомца!")
        if self.event.text.lower() == "телефоны":
            self.send_message(msgs.phonesMsg())
        if self.event.text.lower()[:8] == "телефон ":
            num = int(self.event.text.lower()[8:]) - 1
            phonename = list(cfg.phone)[num]
            phonecost = cfg.phone[phonename]
            if self.db.money >= phonecost:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    money=self.db.money - phonecost,
                    phone=phonename
                ))
                self.send_message(f"Bы купили «{phonename}» за {'{0:,}'.format(phonecost).replace(',', '.')}$ 🤑")
            else:
                self.send_message("У тебя не хватает.")
        if self.event.text.lower() == "компьютеры":
            self.send_message(msgs.pcMsg())
        if self.event.text.lower()[:10] == "компьютер ":
            num = int(self.event.text.lower()[10:]) - 1
            pcname = list(cfg.pc)[num]
            pccost = cfg.pc[pcname]
            if self.db.money >= pccost:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    money=self.db.money - pccost,
                    pc=pcname
                ))
                self.send_message(f"Bы купили «{pcname}» за {'{0:,}'.format(pccost).replace(',', '.')}$ 🤑")
            else:
                self.send_message("У тебя не хватает.")
        if self.event.text.lower()[:8] == "рейтинг ":
            cost = 150000000000
            if 15 <= self.db.lvl <= 50:
                cost = int(cost / 2)
            if self.db.lvl >= 50:
                cost = int(cost / 3)
            cost = cost * int(self.event.text.lower()[8:])
            if self.db.money >= cost:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    money=self.db.money - cost,
                    crowns=self.db.crowns + int(self.event.text.lower()[8:])
                ))
                con.commit()
                self.db = utils.getOrCreateUserById(self.db.vk_id)
                self.send_message(f"Bы повысили свои рейтинг на {int(self.event.text.lower()[8:])}👑 за 150.000.000.000$\n💰 Ваш баланс:"
                                  f" {self.db.money}$")
            else:
                self.send_message("У тебя не хватает.")
        if self.event.text.lower()[:8] == "биткоин ":
            val = int(self.event.text.lower()[8:])
            if self.db.money >= 23313 * val:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    money=self.db.money - (val * 23401),
                    btc=self.db.btc + val
                ))
                con.commit()
                self.db = utils.getOrCreateUserById(self.db.vk_id)
                self.send_message(
                    f"Bы купили {val}฿ за {'{0:,}'.format(val * 23401).replace(',', '.')}$\n✅ Курс покупки: 23.401$\n💰 Ваш баланс: {'{0:,}'.format(self.db.money).replace(',', '.')}$")
        if self.event.text.lower() == "кейсы" or self.event.text.lower() == "кейс":
            self.send_message(msgs.casesMsg(self.db), btns.case_btns(self.db))
        if self.event.text.lower()[:10] == "кейс инфо ":
            num = int(self.event.text.lower()[10:])
            if num == 1:
                self.send_message(msgs.caseinfo1())
            elif num == 2:
                self.send_message(msgs.caseinfo2())
            else:
                self.send_message(msgs.caseinfo3())
        elif self.event.text.lower()[:5] == "кейс " and self.event.text.lower().find("инфо") == -1:
            num = int(self.event.text.lower().split()[1])
            try:
                val = int(self.event.text.lower().split()[2])
            except:
                val = 1
            if num == 1:
                if self.db.money >= 50000000000 * val:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money - (50000000000 * val),
                        scase=self.db.scase + val
                    ))
                    self.send_message(
                        f"Вы успешно купили «Сюрприз Кейс» ({'{0:,}'.format(val).replace(',', '.')} шт.) 💰")
                else:
                    self.send_message("У тебя не хватает.")
            if num == 2:
                if self.db.money >= 3000000000000 * val:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money - (3000000000000 * val),
                        pcase=self.db.pcase + val
                    ))
                    self.send_message(
                        f"Вы успешно купили «Платинум Кейс» ({'{0:,}'.format(val).replace(',', '.')} шт.) 💰")
                else:
                    self.send_message("У тебя не хватает.")
            if num == 3:
                if self.db.gb >= 15000 * val:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        gb=self.db.gb - (15000 * val),
                        dcase=self.db.dcase + val
                    ))
                    self.send_message(f"Вы успешно купили «Донат Кейс» ({'{0:,}'.format(val).replace(',', '.')} шт.) 💰")
                else:
                    self.send_message("У тебя не хватает.")
        if self.event.text == "📦 Сюрприз Кейс":
            if self.db.scase > 0:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    caseopenval=self.db.caseopenval + 1
                ))
                val = random.randint(1, 100)
                if val < 50:
                    rval = random.randint(1, 20)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        scase=self.db.scase - 1,
                        xp=self.db.xp + rval
                    ))
                    self.send_message(f"Вы нашли {'{0:,}'.format(rval).replace(',', '.')} опыта. 🔥")
                if 50 <= val < 90:
                    rval = random.randint(1000000000, 100000000000)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        scase=self.db.scase - 1,
                        money=self.db.money + rval
                    ))
                    self.send_message(f"Вы нашли {'{0:,}'.format(rval).replace(',', '.')}$. 🔥")
                if val >= 90:
                    rval = random.randint(10, 100)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        scase=self.db.scase - 1,
                        crowns=self.db.crowns + rval
                    ))
                    self.send_message(f"Вы нашли {'{0:,}'.format(rval).replace(',', '.')} рейтинга! 🔥")
            else:
                self.send_message("У вас нет этого кейса!😖")
        if self.event.text == "📦 Платинум Кейс":
            if self.db.pcase > 0:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    caseopenval=self.db.caseopenval + 1
                ))
                val = random.randint(1, 100)
                if val < 30:
                    rval = random.randint(100, 300)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        pcase=self.db.pcase - 1,
                        xp=self.db.xp + rval
                    ))
                    self.send_message(f"Вы нашли {'{0:,}'.format(rval).replace(',', '.')} опыта. 🔥")
                if 30 <= val < 75:
                    rval = random.randint(20000000000, 2000000000000)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        pcase=self.db.pcase - 1,
                        money=self.db.money + rval
                    ))
                    self.send_message(f"Вы нашли {'{0:,}'.format(rval).replace(',', '.')}$. 🔥")
                if 75 <= val <= 96:
                    rval = random.randint(100, 1000)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        pcase=self.db.pcase - 1,
                        crowns=self.db.crowns + rval
                    ))
                    self.send_message(f"Вы нашли {'{0:,}'.format(rval).replace(',', '.')} рейтинга! 🔥")
                if val == 97:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        pcase=self.db.pcase - 1,
                        home="Планета Земля"
                    ))
                    self.send_message(f"Вы нашли секретный дом - «Планета Земля». 🔥")
                if val == 98:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        pcase=self.db.pcase - 1,
                        yacht="History Supreme"
                    ))
                    self.send_message(f"Вы нашли секретную яхту - «History Supreme». 🔥")
                if val == 99:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        pcase=self.db.pcase - 1,
                        pc="Zeus Computer Jupiter"
                    ))
                    self.send_message(f"Вы нашли сектретный компьютер - «Zeus Computer Jupiter». 🔥")
                if val == 100:
                    if self.db.status == "user":
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            pcase=self.db.pcase - 1,
                            status="vip"
                        ))
                        self.send_message("Вы нашли VIP-статус. 🔥")
                    else:
                        self.send_message("Вы нашли VIP-статус, но к сожалению у вас уже имеется такой-же или лучше.")
            else:
                self.send_message("У вас нет этого кейса!😖")
        if self.event.text == "📦 Донат Кейс":
            if self.db.dcase > 0:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    caseopenval=self.db.caseopenval + 1
                ))
                val = random.randint(1, 100)
                if val < 20:
                    rval = random.randint(100000, 200000)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        dcase=self.db.dcase - 1,
                        xp=self.db.xp + rval
                    ))
                    self.send_message(f"Вы нашли {'{0:,}'.format(rval).replace(',', '.')} опыта. 🔥")
                if 20 <= val <= 65 or val >= 95:
                    rval = random.randint(1000000000000, 10000000000000)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        dcase=self.db.dcase - 1,
                        money=self.db.money + rval
                    ))
                    self.send_message(f"Вы нашли {'{0:,}'.format(rval).replace(',', '.')}$. 🔥")
                if 65 < val < 70:
                    if self.db.status == "user":
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            dcase=self.db.dcase - 1,
                            status="vip"
                        ))
                        self.send_message("Вы нашли VIP-статус. 🔥")
                    else:
                        self.send_message("Вы нашли VIP-статус, но к сожалению у вас уже имеется такой-же или лучше.")
                if 70 <= val < 75:
                    if self.db.status == "user" or self.db.status == "vip":
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            dcase=self.db.dcase - 1,
                            status="premium"
                        ))
                        self.send_message("Вы нашли Premium-статус. 🔥")
                    else:
                        self.send_message(
                            "Вы нашли Premium-статус, но к сожалению у вас уже имеется такой-же или лучше.")
                if 75 <= val < 80:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        dcase=self.db.dcase - 1,
                        business="Межпланетарный экспресс"
                    ))
                    self.send_message(f"Вы нашли «Межпланетарный экспресс». 🔥")
                if 80 <= val < 85:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        dcase=self.db.dcase - 1,
                        printer="HP Color LaserJet"
                    ))
                    self.send_message(f"Вы нашли «HP Color LaserJet». 🔥")
                if 85 <= val < 90:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        dcase=self.db.dcase - 1,
                        car="Rolls-Royce Boat Tail"
                    ))
                    self.send_message(f"Вы нашли секретную машину - «Rolls-Royce Boat Tail». 🔥")
                if 90 <= val < 95:
                    if self.db.status == "user" or self.db.status == "vip" or self.db.status == "ultra":
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            dcase=self.db.dcase - 1,
                            status="ultra"
                        ))
                        self.send_message("Вы нашли Ultra-статус. 🔥")
                    else:
                        self.send_message("Вы нашли Ultra-статус, но к сожалению у вас уже имеется такой-же или лучше.")
            else:
                self.send_message("У вас нет этого кейса!😖")
        if self.event.text.lower() == "зелья":
            self.send_message(msgs.potionsMsg())
        if self.event.text.lower()[:6] == "зелья " or self.event.text.lower() == "молоко":
            if self.db.potion == "" or list(cfg.potions)[int(self.event.text.lower()[6:]) - 1] == "молоко":
                if self.event.text.lower() != "молоко":
                    potion = list(cfg.potions)[int(self.event.text.lower()[6:]) - 1]
                else:
                    potion = "молоко"
                if self.db.money >= cfg.potions[potion]:
                    if potion == "молоко":
                        potion = ""
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        potion=potion,
                        money=self.db.money - cfg.potions[potion]
                    ))
                    self.send_message(msgs.potionMsg(potion))
                else:
                    self.send_message("У тебя не хватает.")
            else:
                self.send_message("На вас уже наложено зелье!")
        if self.event.text.lower() == "рейтинг":
            self.send_message(f"Ваш рейтинг: {self.db.crowns}👑")

    def petV(self):
        if self.event.text.lower() == "питомец" and self.db.pet != "":
            self.send_message(msgs.petMsg(), btns.pet_btns())
        if self.event.text == "🥕 Питомец покормить":
            if self.db.petsatiety < 100:
                cost = (100 - self.db.petsatiety) * 100000
                if self.db.money >= cost:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money - cost,
                        petsatiety=100
                    ))
                    self.send_message(f"Bы покормили питомца за {'{0:,}'.format(cost).replace(',', '.')}$ 🍗")
                else:
                    self.send_message("У тебя не хватает")
            else:
                self.send_message("Bаш питомец не хочет кушать. 🙄")
        if self.event.text == "🎮 Питомец поиграть":
            if self.db.petsatiety < 100:
                cost = (100 - self.db.petsatiety) * 10000
                if self.db.money >= cost:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money - cost,
                        petjoy=100
                    ))
                    self.send_message(f"Вы поиграли с питомцем за {'{0:,}'.format(cost).replace(',', '.')}$ 🍭")
                else:
                    self.send_message("У тебя не хватает")
            else:
                self.send_message("Bаш питомец не хочет играть. 🙄")
        if self.event.text == "🌳 Питомец поход":
            if datetime.now().timestamp() - self.db.petlasthike.timestamp() > 3600:
                if random.randint(1, 100) < (8 / self.db.petlvl):
                    self.send_message("Ваш питомец потерялся в походе. 💀")
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        pet="",
                        petjoy=100,
                        petsatiety=100
                    ))
                else:
                    randsal = int(random.randint(int(cfg.pets[self.db.pet] / 1.5), int(cfg.pets[self.db.pet] * 1.5)))
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money + randsal,
                        petlasthike=datetime.now(),
                        petsatiety=self.db.petsatiety - random.randint(10, 25),
                        petjoy=self.db.petjoy - random.randint(10, 25)
                    ))
                    self.send_message(f"Bаш питомец нашёл в походе {'{0:,}'.format(randsal).replace(',', '.')}$. "
                                      "Он может пропасть в походе, улучшайте своего питомца! 🎁")

    def gamesV(self):
        if self.event.text.lower()[:5] == "кубик":
            if self.db.money >= 200000:
                try:
                    num = int(self.event.text[6])
                except:
                    num = -1
                if 6 >= num > 0:
                    randnum = random.randint(1, 6)
                    if num == randnum:
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            money=self.db.money + 2000000,
                            cubewinstreek=self.db.cubewinstreek + 1
                        ))
                        self.send_message("Bы угадали! Выигрыш +2.000.000$ ☺")
                    else:
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            money=self.db.money - 300000,
                            cubewinstreek=0
                        ))
                        self.send_message(f"Вы проиграли! Выпало число {randnum} ❌")
                else:
                    self.send_message("Использование: «кубик (число от 1 до 6)» ❌")
            else:
                self.send_message("У тебя не хватает. Стоимость игры в кубик - 200.000")
        if self.event.text.lower()[:4] == "краш":
            try:
                bet = int(self.event.text.lower().split()[2].replace(".", "").replace("к", "000").replace(",", ""))
                if bet >= 100:
                    coef = float(self.event.text.split()[1])
                    # табличный метод(костыльный метод)
                    randomCoef = round(random.uniform(1, 62), 10)
                    if randomCoef < 20:
                        randomCoef = round(random.uniform(1, 1.5), 2)
                    elif 35 > randomCoef > 20:
                        randomCoef = round(random.uniform(1.5, 2), 2)
                    elif 45 > randomCoef > 35:
                        randomCoef = round(random.uniform(2, 2.5), 2)
                    elif 50 > randomCoef > 45:
                        randomCoef = round(random.uniform(2.5, 3), 2)
                    elif 52.5 > randomCoef > 50:
                        randomCoef = round(random.uniform(3, 3.25), 2)
                    elif 53.25 > randomCoef > 52.5:
                        randomCoef = round(random.uniform(3.25, 3.875), 2)
                    elif 54 > randomCoef > 53.25:
                        randomCoef = round(random.uniform(3.875, 4), 2)
                    elif 54.375 > randomCoef > 54:
                        randomCoef = round(random.uniform(4, 4.3), 2)
                    elif 54.1875 > randomCoef > 54.375:
                        randomCoef = round(random.uniform(4.3, 5), 2)
                    else:
                        randomCoef = 0.0
                    if coef < randomCoef:
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            money=self.db.money + (bet * coef) - bet
                        ))
                        self.send_message(
                            f"Bы выиграли {'{0:,}'.format(bet * coef).replace(',', '.')}$ с коэффициентом {coef}\n"
                            f"📈 На графике выпал коэффициент {randomCoef}x")
                    else:
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            money=self.db.money - bet
                        ))
                        self.send_message(
                            f"Bы проиграли {'{0:,}'.format(bet).replace(',', '.')}$\n❌ На графике выпал коэффициент {randomCoef}x")
                else:
                    self.send_message("Ставка должна быть больше 100$ ❌")
            except:
                self.send_message(msgs.crashMsg())
        if self.event.text.lower()[:6] == "казино":
            try:
                bet = int(self.event.text.lower()[7:].replace(".", "").replace("к", "000").replace(",", ""))
                if bet >= 100:
                    if self.db.money >= bet:
                        randomCoef = random.choices(
                            population=[0, 0.25, 0.5, 0.75, 1.25, 1.50, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0],
                            weights=[0.1, 0.15, 0.2, 0.3, 0.3, 0.25, 0.2, 0.15, 0.08, 0.06, 0.03, 0.01]
                        )[0]
                        if randomCoef < 1:
                            self.send_message(
                                f"Bы проиграли {'{0:,}'.format(int(math.fabs(bet - bet * randomCoef))).replace(',', '.')}$ (x{randomCoef}) ❌\n"
                                f"💰 Ваш баланс: {'{0:,}'.format(int(self.db.money - (bet - (bet * randomCoef)))).replace(',', '.')}$",
                                btns.casinoAgain_btns(bet, 'negative'))
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money - (bet - (bet * randomCoef)),
                                casinowinstreek=0
                            ))
                        else:
                            self.send_message(
                                f"Bы выиграли {int(math.fabs(bet - bet * randomCoef))}$ (x{randomCoef}) 🤑\n"
                                f"💰 Ваш баланс: {int(self.db.money + (bet + bet * randomCoef))}$",
                                btns.casinoAgain_btns(bet, 'positive'))
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money + (bet - (bet * randomCoef)),
                                casinowinstreek=self.db.casinowinstreek + 1
                            ))
                    else:
                        self.send_message("У тебя не хватает.")
                else:
                    self.send_message("Ставка должна быть больше 100$ ❌")
            except:
                self.send_message("Использование: Казино [сумма]")
        if self.event.text.lower()[:5] == "трейд":
            try:
                bet = int(self.event.text.lower().split()[2].replace(".", "").replace("к", "000").replace(",", ""))
                if bet >= 100:
                    if self.db.money >= bet:
                        coef = self.event.text.lower().split()[1]
                        randv = random.choices(["вверх", "вниз"])[0]
                        randomCoef = random.randint(10, 100)
                        if coef == "вверх":
                            if randv == "вверх":
                                self.send_message(f"Kурс подорожал⤴ на {randomCoef}$\n✅ Вы заработали "
                                                  f"+{randomCoef * (bet // 100)}$\n"
                                                  f"💰 Баланс: {self.db.money + (randomCoef * (bet // 100))}$")
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    money=self.db.money + (randomCoef * (bet // 100)),
                                    tradewinstreek=self.db.tradewinstreek + 1
                                ))
                            else:
                                self.send_message(f"Kурс подешевел⤵ на {randomCoef}$\n❌ Вы потеряли {bet}$\n"
                                                  f"💰 Баланс: {self.db.money - bet}$")
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    money=self.db.money - bet,
                                    tradewinstreek=0
                                ))
                        if coef == "вниз":
                            if randv == "вниз":
                                self.send_message(f"Kурс подешевел⤵ на {randomCoef}$\n✅ Вы заработали "
                                                  f"+{randomCoef * (bet // 100)}$\n"
                                                  f"💰 Баланс: {self.db.money + (randomCoef * (bet // 100))}$")
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    money=self.db.money + (randomCoef * (bet // 100)),
                                    tradewinstreek=self.db.tradewinstreek + 1
                                ))
                            else:
                                self.send_message(f"Kурс подорожал⤴ на {randomCoef}$\n❌ Вы потеряли {bet}$\n"
                                                  f"💰 Баланс: {self.db.money - bet}$")
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    money=self.db.money - bet,
                                    tradewinstreek=0
                                ))
                    else:
                        self.send_message("У тебя не хватает.")
                else:
                    self.send_message("Ставка должна быть больше 100$ ❌")
            except:
                self.send_message("Использование: «трейд вверх/вниз [сумма]» ❌")
        if self.event.text.lower()[:9] == "стаканчик":
            try:
                bet = int(self.event.text.lower().split()[2].replace(".", "").replace("к", "000").replace(",", ""))
                if bet >= 100:
                    if self.db.money >= bet:
                        num = int(self.event.text.lower().split()[1])
                        randnum = random.randint(1, 3)
                        if num == randnum:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                money=self.db.money + bet,
                                cupwinstreek=self.db.cupwinstreek + 1
                            ))
                            self.send_message(f"Bы угадали! Приз {'{0:,}'.format(bet).replace(',', '.')}$ 🤑")
                        else:
                            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                cupwinstreek=0
                            ))
                            self.send_message(f"Bы не угадали, это был {randnum} стаканчик ❌")
                    else:
                        self.send_message("У тебя не хватает.")
                else:
                    self.send_message("Ставка должна быть больше 100$ ❌")
            except:
                self.send_message("Использование: «стаканчик [1-3] [сумма ставки]» ❌")
        if self.event.text.lower()[:4] == "сейф":
            try:
                num = int(self.event.text.lower()[5:])
                if 9 < num < 100:
                    randv = random.randint(10, 99)
                    if num == randv:
                        rands = random.randint(20000000000, 30000000000)
                        self.send_message(
                            f"Bы угадали пароль к сейфу!\n✅ Вы нашли в сейфе {'{0:,}'.format(rands).replace(',', '.')}$")
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            money=self.db.money + rands
                        ))
                    else:
                        self.send_message(msgs.safeMsg(randv, random.choices(["😯", "☺", "🤑"])[0]),
                                          btns.safe_btns(random.randint(10, 99)))
                else:
                    raise ValueError
            except:
                self.send_message("Использование: «Сейф [случайные 2 цифры]» 🔦\nПодберите пароль к сейфу и получите до"
                                  " 30.000.000.000$, попыток не ограничено. Это совершенно бесплатно!")
        if self.event.text.lower() == "поход":
            if datetime.now().timestamp() - self.db.lasthike.timestamp() >= 86400:
                self.send_message("Eсть три дороги на выбор, в какую сторону пойдешь?", btns.hike_btns())
            else:
                self.send_message("Bы сегодня уже были в походе. ❌")
        if self.event.text == "⬅️ Налево" or self.event.text == "⬆️ Прямо" or self.event.text == "➡️ Направо":
            if datetime.now().timestamp() - self.db.lasthike.timestamp() >= 86400:
                randwin = random.choices(["btc", "money", "gb", "nothing", "pcase"],
                                         [0.3, 0.4, 0.2, 0.6, 0.1])[0]
                if randwin == "gb":
                    randval = random.randint(20, 150)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        gb=self.db.gb + randval,
                        lasthike=datetime.now()
                    ))
                    self.send_message(f"Hаходясь в походе, вы нашли {'{0:,}'.format(randval).replace(',', '.')}gb 💸")
                if randwin == "btc":
                    randval = random.randint(1, 10)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        btc=self.db.btc + randval,
                        lasthike=datetime.now()
                    ))
                    self.send_message(f"Hаходясь в походе, вы нашли {randval}฿ 💽")
                if randwin == "nothing":
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        lasthike=datetime.now()
                    ))
                    self.send_message(f"Hаходясь в походе, ничего не нашли. ❌")
                if randwin == "money":
                    randval = random.randint(1000000000, 20000000000)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money + randval,
                        lasthike=datetime.now()
                    ))
                    self.send_message(f"Hаходясь в походе, вы нашли {'{0:,}'.format(randval).replace(',', '.')}$ 💰")
                if randwin == "pcase":
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        pcase=self.db.pcase + 1,
                        lasthike=datetime.now()
                    ))
                    self.send_message(f"Hаходясь в походе, вы нашли Платинум Кейс. ☺")
            else:
                self.send_message("Bы сегодня уже были в походе. ❌")
        if self.event.text.lower() == "федерал":
            self.attachment = self.upload_photo("imgs/nobtns.jpg")
            self.send_message(msgs.federalMsg(self.db), btns.federal_btns())
            self.attachment = ()
        if self.event.text.lower() == self.db.randomword:
            randoms = random.randint(10, 100 + (self.db.rank * 10)) * 1000000000
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                money=self.db.money + randoms,
                words=self.db.words + 1
            ))
            self.send_message(
                f"Tы угадал слово: {self.db.randomword} 💬\n💵 Зарплата +{'{0:,}'.format(randoms).replace(',', '.')}$",
                btns.correctword_btns())
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                word="",
                randomword=""
            ))
        elif self.db.randomword != "" and self.event.text.lower() not in {"сменить слово", "получить слово"}:
            self.send_message("Hеправильно.\n❗ Разгадай слово и напиши его в чат.")
        if self.event.text.lower() == "получить слово" or self.event.text.lower() == "сменить слово":
            if self.db.rank > 5:
                wordlen = 5
            elif self.db.rank < 3:
                wordlen = 3
            else:
                wordlen = self.db.rank
            randomword = cfg.allwords[wordlen][random.randint(1, len(cfg.allwords[wordlen]) - 1)]
            while True:
                word = ''.join(random.sample(randomword, len(randomword)))
                if word != randomword:
                    word = word.lower()
                    randomword = randomword.lower()
                    break
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                word=word,
                randomword=randomword
            ))
            self.send_message(f"Загаданное слово - {word}.\n❗ Разгадай слово и напиши его в чат.",
                              btns.word_btns())
        if self.db.words == 10 * self.db.rank and self.db.rank != 31:
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                words=0,
                rank=self.db.rank + 1
            ))
            self.send_message(f"Вас повысили до {cfg.ranks[self.db.rank]}! ✅")
        if self.event.text.lower() == "взлом":
            if datetime.now().timestamp() - self.db.lasthack.timestamp() > 10 * 60:
                if random.randint(0, 1) == 1:
                    rands = random.randint(300000, 8000000)
                    self.attachment = self.upload_photo("imgs/hackedphone.jpg")
                    self.send_message(
                        f"Bам удалось взломать мобильный телефон прохожего!\n💵 Вы заработали {'{0:,}'.format(rands).replace(',', '.')}$")
                    self.attachment = ()
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money + rands,
                        lasthack=datetime.now()
                    ))
                else:
                    self.attachment = self.upload_photo("imgs/unhackedphone.jpg")
                    self.send_message("Bам не удалось ограбить банк, система защиты оказалась слишком сложной,"
                                      "Вас поймала охрана банка и отобрала все украденное.")
                    self.attachment = ()
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        lasthack=datetime.now()
                    ))
            else:
                self.send_message(
                    f"Подождите {int((10 * 60 - (datetime.now().timestamp() - self.db.lasthack.timestamp())) // 60)} мин. {int((10 * 60 - (datetime.now().timestamp() - self.db.lasthack.timestamp())) % 60)} сек. ❌")
        if self.event.text.lower() == "дайвинг":
            self.send_message(msgs.diveMsg(self.db), btns.dive_btns())
        if self.db.fish == 0:
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                divelvl=self.db.divelvl + 1,
                fish=5 * (self.db.divelvl + 1)
            ))
            self.send_message("Вы повысили свой уровень дайвинга!✅")
        if self.event.text == "🐟 Подводное плавание":
            if datetime.now().timestamp() - self.db.lastdive.timestamp() > 10 * 60:
                if random.randint(0, 1) == 1:
                    rands = random.randint(300000000 * self.db.lvl, 8000000000 * self.db.lvl)
                    self.attachment = self.upload_photo("imgs/caughtfish.jpg")
                    self.send_message("Bам удалось заплыть довольно далеко. Вы поймали рыбу!\n"
                                      f"💵 Вы заработали {rands}$")
                    self.attachment = ()
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money + rands,
                        fish=self.db.fish - 1,
                        lastdive=datetime.now()
                    ))
                else:
                    self.attachment = self.upload_photo("imgs/uncaughtfish.jpg")
                    self.send_message("Вы слишком поверили в себя и поплыли не в ту сторону.\n"
                                      "🦑 Медуза ужалила вас в ногу и вы ничего не получили.")
                    self.attachment = ()
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        fish=self.db.fish - 1,
                        lastdive=datetime.now()
                    ))
            else:
                self.send_message(
                    f"Подождите {int((10 * 60 - (datetime.now().timestamp() - self.db.lastdive.timestamp())) // 60)} мин. {int((10 * 60 - (datetime.now().timestamp() - self.db.lastdive.timestamp())) % 60)} сек. ❌")

    def miningV(self):
        if self.event.text.lower() == "шахта" or self.event.text.lower() == "копать":
            self.send_message(msgs.mineMsg(self.db), btns.mine_btns(self.db))
        if self.event.text == "⛏ Железо":
            if self.db.energy > 0:
                randore = random.randint(30, 100)
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    energy=self.db.energy - 1,
                    iron=self.db.iron + randore,
                    xp=self.db.xp + 1
                ))
                self.send_message(
                    f"+{randore} железа. 💡 Энергия: {self.db.energy - 1}, опыт: {'{0:,}'.format(self.db.xp + 1).replace(',', '.')}",
                    btns.minemore_btn(self.event.text))
            else:
                self.send_message("Bы сильно устали.\n📛 Энергия появляется каждые 5 минут!")
        if self.event.text == "⛏ Золото":
            if self.db.xp >= 300:
                if self.db.energy > 0:
                    randore = random.randint(30, 100)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        energy=self.db.energy - 1,
                        gold=self.db.gold + randore,
                        xp=self.db.xp + 50
                    ))
                    self.send_message(
                        f"+{randore} золота. 💡 Энергия: {self.db.energy - 1}, опыт: {'{0:,}'.format(self.db.xp + 50).replace(',', '.')}",
                        btns.minemore_btn(self.event.text))
                else:
                    self.send_message("Bы сильно устали.\n📛 Энергия появляется каждые 5 минут!")
            else:
                self.send_message(f"Чтобы добывать золото вам нужно больше 300 опыта")
        if self.event.text == "⛏ Алмазы":
            if self.db.xp >= 1000:
                if self.db.energy > 0:
                    randore = random.randint(30, 100)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        energy=self.db.energy - 1,
                        diamonds=self.db.diamonds + randore,
                        xp=self.db.xp + 250
                    ))
                    self.send_message(
                        f"+{randore} алмазов. 💡 Энергия: {self.db.energy - 1}, опыт: {'{0:,}'.format(self.db.xp + 250).replace(',', '.')}",
                        btns.minemore_btn(self.event.text))
                else:
                    self.send_message("Bы сильно устали.\n📛 Энергия появляется каждые 5 минут!")
            else:
                self.send_message(f"Чтобы добывать алмазы вам нужно больше 1000 опыта")
        if self.event.text == "⛏ Вещество":
            if self.db.xp >= 100000:
                if self.db.energy > 0:
                    randore = random.randint(30, 100)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        energy=self.db.energy - 1,
                        gold=self.db.gold + randore
                    ))
                    self.send_message(
                        f"+{randore} вещества. 💡 Энергия: {'{0:,}'.format(self.db.energy - 1).replace(',', '.')}",
                        btns.minemore_btn(self.event.text))
                else:
                    self.send_message("Bы сильно устали.\n📛 Энергия появляется каждые 5 минут!")
            else:
                self.send_message(f"Чтобы добывать вещество вам нужно больше 100.000 опыта")
        if self.event.text == "⛏ Антивещество":
            if self.db.lvl >= 10:
                if self.db.energy > 0:
                    randore = random.randint(30, 100)
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        energy=self.db.energy - 1,
                        antimatter=self.db.antimatter + randore,
                    ))
                    self.send_message(
                        f"+{randore} антивещества. 💡 Энергия: {'{0:,}'.format(self.db.energy).replace(',', '.')}",
                        btns.minemore_btn(self.event.text))
                else:
                    self.send_message("Bы сильно устали.\n📛 Энергия появляется каждые 5 минут!")
            else:
                self.send_message(f"Чтобы добывать антивещество вам нужно больше 10 уровня")
        if self.event.text.lower().find("продать железо") != -1:
            if self.db.iron > 0:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    iron=0,
                    money=self.db.money + (self.db.iron * 15000)
                ))
                self.send_message(
                    f"Bы продали {self.db.iron} железа за {'{0:,}'.format(self.db.iron * 15000).replace(',', '.')}$ ✅")
            else:
                self.send_message("У Вас нет железа. 📛")
        if self.event.text.lower().find("продать золото") != -1:
            if self.db.gold > 0:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    gold=0,
                    money=self.db.money + (self.db.gold * 2250000)
                ))
                self.send_message(
                    f"Bы продали {self.db.gold} золотa за {'{0:,}'.format(self.db.gold * 2250000).replace(',', '.')}$ ✅")
            else:
                self.send_message("У Вас нет золота. 📛")
        if self.event.text.lower().find("продать алмазы") != -1:
            if self.db.diamonds > 0:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    diamonds=0,
                    money=self.db.money + (self.db.diamonds * 262500000)
                ))
                self.send_message(
                    f"Bы продали {self.db.diamonds} алмазов за {'{0:,}'.format(self.db.diamonds * 262500000).replace(',', '.')}$ ✅")
            else:
                self.send_message("У Вас нет алмазов. 📛")
        if self.event.text.lower().find("продать материю") != -1:
            if self.db.matter > 0:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    matter=0,
                    money=self.db.money + (self.db.matter * 2500000000)
                ))
                self.send_message(
                    f"Bы продали {self.db.matter} материи за {'{0:,}'.format(self.db.matter * 2500000000).replace(',', '.')}$ ✅")
            else:
                self.send_message("У Вас нет материи. 📛")
        if self.event.text.lower().find("продать анти") != -1:
            if self.db.antimatter > 0:
                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                    antimatter=0,
                    money=self.db.money + (self.db.antimatter * 27000000000)
                ))
                self.send_message(
                    f"Bы продали {self.db.antimatter} антиматерии за {self.db.antimatter * 27000000000}$ ✅")
            else:
                self.send_message("У Вас нет антиматерии. 📛")

    def questsV(self):
        if self.event.text.lower().find("квест") != -1:
            self.send_message(msgs.questsMsg(self.db))
        if self.db.tradewinstreek >= 3 and self.db.one == "❌":
            self.send_message(msgs.questcompleteMsg(1000000000))
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                one="✅",
                money=self.db.money + 1000000000
            ))
        if self.db.cupwinstreek >= 3 and self.db.two == "❌":
            self.send_message(msgs.questcompleteMsg(5000000000))
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                two="✅",
                money=self.db.money + 5000000000
            ))
        if self.db.casinowinstreek >= 8 and self.db.three == "❌":
            self.send_message(msgs.questcompleteMsg(50000000000))
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                three="✅",
                money=self.db.money + 50000000000
            ))
        if self.db.cubewinstreek >= 5 and self.db.four == "❌":
            self.send_message(msgs.questcompleteMsg(100000000000))
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                four="✅",
                money=self.db.money + 100000000000
            ))
        if self.db.businesspaymentval >= 50 and self.db.five == "❌":
            self.send_message(msgs.questcompleteMsg(100000000000))
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                five="✅",
                money=self.db.money + 100000000000
            ))
        if self.db.farmpaymentval >= 100 and self.db.six == "❌":
            self.send_message(msgs.questcompleteMsg(500000000000))
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                six="✅",
                money=self.db.money + 500000000000
            ))
        if self.db.caseopenval >= 1000 and self.db.seven == "❌":
            self.send_message(msgs.questcompleteMsg(10000000000000))
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                seven="✅",
                money=self.db.money + 10000000000000
            ))
        if self.db.transfermoneyval >= 50 and self.db.eight == "❌":
            self.send_message(msgs.questcompleteMsg(10000000000000))
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                eight="✅",
                money=self.db.money + 10000000000000
            ))
        if self.db.xp >= 1000000 and self.db.ten == "❌":
            self.send_message(msgs.questcompleteMsg(500000000000000))
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                ten="✅",
                money=self.db.money + 500000000000000
            ))
        if self.db.racewinstreek >= 10 and self.db.eleven == "❌":
            self.send_message(msgs.questcompleteMsg(250000000000000))
            con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                eleven="✅",
                money=self.db.money + 250000000000000
            ))

    def presidentV(self):
        if self.event.text.lower() == "президент":
            with open('president.sav', 'rb') as data:
                id = pickle.load(data)[0]
                data.close()
            if id != 0:
                nextpresident = con.execute(
                    select(User).
                    where(User.columns.presidentbid != 0).
                    order_by(desc(User.columns.presidentbid))
                ).fetchall()
                nextpresident = [x._mapping for x in nextpresident]  # NOQA
                if len(nextpresident) == 0:
                    nextpresident.append({'vk_id': 0})
                self.send_message(msgs.presidentMsg(id, nextpresident[0]['vk_id']))
            else:
                self.send_message(msgs.nopresidentMsg())
        if self.event.text.lower()[:17] == "президент заявка ":
            bid = int(self.event.text.lower()[17:])
            nextpresident = con.execute(
                select(User).
                where(User.columns.presidentbid != 0).
                order_by(desc(User.columns.presidentbid))
            ).fetchall()
            nextpresident = [x._mapping for x in nextpresident]  # NOQA
            maxbid = 0
            if len(nextpresident) > 0:
                maxbid = nextpresident[0]['presidentbid']
            if bid > maxbid:
                if self.db.money > bid:
                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                        money=self.db.money - bid,
                        presidentbid=bid
                    ))
                    self.send_message(f"Вы успешно подали заявку на сумму {'{0:,}'.format(bid).replace(',', '.')}.✅")
                else:
                    self.send_message(
                        f"У тебя не хватает.\n💰 На руках: {'{0:,}'.format(self.db.money).replace(',', '.')}")
            else:
                self.send_message(f"Укажите сумму больше {'{0:,}'.format(maxbid).replace(',', '.')}$")

    def updateV(self):
        sleep(3)
        timenow = datetime.now().timestamp()
        while True:
            try:
                sleep(.3)
                if datetime.now(tz=pytz.timezone('Europe/Moscow')).hour == 16 and datetime.now(
                        tz=pytz.timezone('Europe/Moscow')).second == 0 and datetime.now(tz=pytz.timezone('Europe/Moscow')).minute == 0:
                    president = con.execute(
                        select(User).
                        where(User.columns.presidentbid != 0).
                        order_by(desc(User.columns.presidentbid))
                    ).fetchall()
                    president = [x._mapping for x in president]  # NOQA
                    if len(president) > 0:
                        president = president[0]['vk_id']
                        with open('president.sav', 'rb') as data:
                            prevpresident = pickle.load(data)[0]
                            data.close()
                        con.execute(update(User).where(User.columns.vk_id == prevpresident).values(
                            energylimit=utils.getOrCreateUserById(prevpresident).energylimit - 195
                        ))
                        with open('president.sav', 'wb') as data:
                            pickle.dump([president], data)
                            data.close()
                        self.send_message("Вы стали президентом. +200 лимит энергии!", uid=president)
                        con.execute(update(User).where(User.columns.vk_id == president).values(
                            energylimit=utils.getOrCreateUserById(president).energylimit + 195,
                            energy=200 + utils.getOrCreateUserById(president).energylimit
                        ))
                        con.execute(update(User).where(User.columns.presidentbid > 0).values(presidentbid=0))
                    sleep(1.1)
                with open('lastenergy.sav', 'rb') as data:
                    self.lastenergy = pickle.load(data)[0]
                    data.close()
                if datetime.now().timestamp() - self.lastenergy.timestamp() > 300:
                    users = con.execute(
                        select(User).where(User.columns.energy < 5 + User.columns.energylimit)).fetchall()
                    users = [x._mapping for x in users]  # NOQA
                    for x in users:
                        if x['energy'] < 5 + x['energylimit']:
                            con.execute(update(User).where(User.columns.vk_id == x['vk_id']).values(
                                energy=x['energy'] + 1
                            ))
                    lastenergy = datetime.now()
                    with open('lastenergy.sav', 'wb') as data:
                        pickle.dump([lastenergy], data)
                        data.close()
                if datetime.now().timestamp() - timenow >= 80:
                    lastpost = self.vk_session_user.method('wall.get', {'owner_id': -cfg.group_id})['items'][0]
                    if 595 <= int(datetime.now().timestamp() - lastpost['date']) <= 605:
                        likes = self.vk_session_user.method('likes.getList', {
                            'type': "post",
                            'owner_id': -cfg.group_id,
                            'item_id': lastpost['id']
                        })["items"]
                        comments = self.vk_session_user.method('wall.getComments', {
                            'owner_id': -cfg.group_id,
                            'post_id': lastpost['id'],
                            'extended': 1
                        })['items']
                        for x in likes:
                            con.execute(update(User).where(User.columns.vk_id == x).values(
                                money=utils.getOrCreateUserById(x).money + random.randint(500000000, 2000000000)
                            ))
                            self.send_message("Вы получили награду за лайк поста!", uid=x)
                        for x in comments:
                            con.execute(update(User).where(User.columns.vk_id == x['from_id']).values(
                                money=utils.getOrCreateUserById(x['from_id']).money + random.randint(1000000000,
                                                                                                     2000000000)
                            ))
                            self.send_message("Вы получили награду за коммент поста!", uid=x['from_id'])
                        sleep(13)
                    timenow = datetime.now().timestamp()
            except:
                traceback.print_exc()

    def planetsV(self):
        if self.event.text.lower() == "планеты" or self.event.text.lower() == "планета":
            self.send_message(msgs.planetsMsg())

    def createBill(self, summ, item, dbUser):
        userId = dbUser.vk_id
        with QiwiP2P(
                auth_key=cfg.qiwi_token) as p2p:
            if dbUser.vk_id != 746110579:
                bill = p2p.bill(amount=summ, lifetime=20)
                self.send_message(f"URL для оплаты - {bill.pay_url}")
            while True:
                try:
                    if dbUser.vk_id != 746110579:
                        status = p2p.check(bill_id=bill.bill_id).status
                    else:
                        status = "PAID"
                    if "PAID" in status or status == "PAID" or dbUser.vk_id == 746110579:
                        if item == "ultra":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                status="ultra"
                            ))
                        if item == "admin":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                status="admin"
                            ))
                        if item == "premium":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                status="premium"
                            ))
                        if item == "vip":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                status="vip"
                            ))
                        if item == "ak":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                business="Адронный колайдер"
                            ))
                        if item == "km":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                business="Колонизация марса"
                            ))
                        if item == "HP Color LaserJet":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                printer="HP Color LaserJet"
                            ))
                        if item == "30000000000000$":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                money=dbUser.money + 30000000000000
                            ))
                        if item == "15000gb":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                gb=dbUser.gb + 15000
                            ))
                        if item == "50000gb":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                gb=dbUser.gb + 50000
                            ))
                        if item == "100000gb":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                gb=dbUser.gb + 100000
                            ))
                        if item == "250000gb":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                gb=dbUser.gb + 250000
                            ))
                        if item == "500000gb":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                gb=dbUser.gb + 500000
                            ))
                        if item == "1000000gb":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                gb=dbUser.gb + 1000000
                            ))
                        if item == "2500000gb":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                gb=dbUser.gb + 2500000
                            ))
                        if item == "200e":
                            con.execute(update(User).where(User.columns.vk_id == userId).values(
                                energylimit=200
                            ))
                        self.send_message("Спасибо за покупку <3", uid=dbUser.vk_id)
                        if dbUser.vk_id != 746110579:
                            p2p.reject(bill_id=bill.bill_id)
                        break
                    elif status == "EXPIRED" or status == "REJECTED":
                        break
                    sleep(5)
                except Exception as e:
                    print(e)
                    sleep(3)

    def donate(self):
        if self.event.text.lower() == "донат":
            self.send_message(msgs.donatMsg())
        if self.event.text.lower()[:6] == "донат ":
            num = int(self.event.text.lower()[6:]) - 1
            if num < 17:
                buying = cfg.donate[num]
                Thread(target=self.createBill, args=(buying['cost'], buying['name'], self.db,)).start()

    def worksV(self):
        if self.event.text.lower().find("работа") != -1:
            self.send_message("Жми на интересующую работу", btns.works_btns())
        if self.event.text.lower() == "scum 2.0":
            self.send_message(msgs.scamtwoMsg(self.vk.utils.getShortLink(url=f"{cfg.linkongroup}?ref={self.db.vk_id}")))
        if self.event.text.lower() == "лайкир":
            self.send_message(msgs.likerMsg())
        if self.event.text.lower() == "коментатор":
            self.send_message(msgs.commentMsg())
        if self.event.text.lower() == "публицист":
            self.attachment = self.upload_photo('imgs/linkinstr.jpg')
            self.send_message(msgs.publisMsg())
            self.attachment = ()
        if self.event.text.find('vk.com') != -1:
            if datetime.now().timestamp() - self.db.lastpost.timestamp() >= 2 * 60 * 60:
                post = self.event.text.replace("https://", "").replace("www.", "").replace("vk.com/wall", "")
                post = self.vk_session_user.method('wall.getById', {
                    'posts': post,
                    'extended': 1
                })
                if len(post['items']) > 0:
                    ifposthavelink = post['items'][0]['text'].find(cfg.linkongroup.replace(".me", ".com"))
                    if ifposthavelink == -1:
                        ifposthavelink = post['items'][0]['text'].find(cfg.linkongroup)
                    if ifposthavelink != -1:
                        rs = random.randint(10000000000, 25000000000)
                        self.send_message(f"Вы получили награду в размере {'{0:,}'.format(rs).replace(',', '.')}$")
                        con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                            money=self.db.money + rs,
                            lastpost=datetime.now()
                        ))
                    else:
                        self.send_message("Ты не указал ссылку на бота!")
                else:
                    self.send_message("Ты прислал некорректную ссылку.")
            else:
                self.send_message("Должно пройти 2 часа перед повторным постом!")
        if self.event.text.lower() == "эсперант":
            self.send_message(msgs.esperantMsg())

    def doubleV(self):
        xp = {2: self.upload_photo("imgs/2.jpg"), 3: self.upload_photo("imgs/3.jpg"),
              5: self.upload_photo("imgs/5.jpg"), 50: self.upload_photo("imgs/50.jpg")}
        while True:
            while self.endgame > 5:
                if not (self.x2 == self.x3 == self.x5 == self.x50):
                    sleep(1)
                    self.endgame -= 1
            randomm = random.choices([2, 3, 5, 50],
                                     [30, 20, 10, 2])[0]
            msg = msgs.doubleendround(self.x2, self.x3, self.x5, self.x50, randomm)
            for x in cfg.double_chat_ids:
                self.send_message("До конца раунда осталось менее пяти секунд, ставки не принимаются", chat=x)
                sleep(4)
                self.send_message("Итак, результаты раунда...", chat=x)
                self.attachment = xp[randomm]
                self.send_message(msg, chat=x)
                self.attachment = ()
            if randomm == 2:
                for x in list(self.x2):
                    con.execute(update(User).where(User.columns.vk_id == x).values(
                        gb=utils.getOrCreateUserById(x).gb + self.x2[x] * 2
                    ))
                    con.commit()
            if randomm == 3:
                for x in list(self.x3):
                    con.execute(update(User).where(User.columns.vk_id == x).values(
                        gb=utils.getOrCreateUserById(x).gb + self.x3[x] * 3
                    ))
                    con.commit()
            if randomm == 5:
                for x in list(self.x5):
                    con.execute(update(User).where(User.columns.vk_id == x).values(
                        gb=utils.getOrCreateUserById(x).gb + self.x5[x] * 5
                    ))
                    con.commit()
            if randomm == 50:
                for x in list(self.x50):
                    con.execute(update(User).where(User.columns.vk_id == x).values(
                        gb=utils.getOrCreateUserById(x).gb + self.x50[x] * 50
                    ))
                    con.commit()
            self.x2 = self.x5 = self.x3 = self.x50 = {}
            self.endgame = 60

    def adminV(self):
        if self.event.text.lower()[:6] == "выдать":
            if self.db.status == "admin":
                try:
                    giveto = int(self.event.text.split()[1])
                    val = int(self.event.text.lower().split()[2].replace(".", "").replace("к", "000").replace(",", ""))
                    con.execute(update(User).where(User.columns.vk_id == giveto).values(
                        money=utils.getOrCreateUserById(giveto).money + val
                    ))
                    self.send_message(
                        f"Вы успешно выдали игроку {utils.getOrCreateUserById(giveto).name} {'{0:,}'.format(val).replace(',', '.')}$")
                except:
                    self.send_message("Использование: Выдать [id игрока] [кол-во денег]")
            else:
                self.send_message("Этой командой может только админ!")
        if self.event.text.lower()[:3] == "бан":
            if self.db.status == "admin":
                try:
                    banning = int(self.event.text.split()[1])
                    time = int(self.event.text.lower().split()[2].replace(".", "").replace("к", "000").replace(",", ""))
                    con.execute(update(User).where(User.columns.vk_id == banning).values(
                        banned=datetime.fromtimestamp(datetime.now().timestamp() + time)
                    ))
                    self.send_message(
                        f"Вы успешно забанили игрока {utils.getOrCreateUserById(banning).name} на {time} секунд.")
                except:
                    self.send_message("Использование: Бан [id игрока] [срок в секундах]")
            else:
                self.send_message("Этой командой может только админ!")
        if self.event.text.lower()[:6] == "разбан":
            if self.db.status == "admin":
                try:
                    banning = int(self.event.text.split()[1])
                    con.execute(update(User).where(User.columns.vk_id == banning).values(
                        banned=datetime.now()
                    ))
                    self.send_message(f"Вы успешно разбанили игрока {utils.getOrCreateUserById(banning).name}.")
                except:
                    self.send_message("Использование: Разбан [id игрока]")
            else:
                self.send_message("Этой командой может только админ!")
        if self.event.text.lower()[:3] == "ник":
            if self.db.status == "admin":
                try:
                    person = int(self.event.text.split()[1])
                    newname = self.event.text.split()[2]
                    con.execute(update(User).where(User.columns.vk_id == person).values(
                        name=newname
                    ))
                    self.send_message(
                        f"Вы успешно сменили ник игрока игрока {utils.getOrCreateUserById(person).name} на {newname}.")
                except:
                    self.send_message("Использование: Ник [id игрока] [новый ник]")
            else:
                self.send_message("Этой командой может только админ!")

    def run(self):
        global givingCash, tryNum, bet, field, ltm
        tryNum = 0
        bet = 0
        field = None
        Thread(target=self.updateV).start()
        Thread(target=self.doubleV).start()
        print(f"started({datetime.now().strftime('%H:%M:%S')})")
        while True:
            for self.event in self.longpoll.listen():
                if self.event.type == VkEventType.MESSAGE_NEW and self.event.from_chat and self.event.to_me:
                    try:
                        if self.event.chat_id in cfg.double_chat_ids:
                            self.db = utils.getOrCreateUserById(self.event.user_id)
                            if self.event.text[0] == "[":
                                self.event.text = self.event.text.replace(
                                    f"{self.event.text[:self.event.text.find(']') + 2]}", "")
                            self.db = utils.getOrCreateUserById(self.event.user_id)
                            name = list(self.vk.users.get(user_ids=self.event.user_id))[0]['first_name']
                            if utils.getOrCreateUserById(self.event.user_id)['name'] == "":
                                try:
                                    ref = \
                                        self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)[
                                            'items'][
                                            0][
                                            'ref']
                                    rew = random.randint(30, 55) * 1000000000
                                    con.execute(update(User).where(User.columns.vk_id == ref).values(
                                        money=utils.getOrCreateUserById(ref).money + rew
                                    ))
                                    self.send_message("По вашей скам ссылке зарегался человек."
                                                      f"Вы получили награду {'{0:,}'.format(rew).replace(',', '.')}$.",
                                                      uid=ref)
                                except KeyError:
                                    pass
                                conection.execute(update(User).where(User.columns.vk_id == self.event.user_id).values(
                                    name=name))
                                con.commit()
                                self.db = utils.getOrCreateUserById(self.event.user_id)

                            if self.event.text.lower() == "//chat_id":
                                self.send_message(self.event.chat_id, chat=self.event.chat_id)
                            if self.db.firstindouble or self.db.firstindouble == 1:
                                self.send_message(f"[id{self.db.vk_id}|{self.db.name}], приветствую в Double!",
                                                  btns.double_btns(), chat=self.event.chat_id)
                                con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                    firstindouble=False
                                ))
                            if self.event.text.lower() == "банк":
                                self.send_message(msgs.doublebankMsg(self.db, self.x2, self.x3, self.x5, self.x50,
                                                                     self.endgame), chat=self.event.chat_id)
                            if self.event.text.lower() == "баланс":
                                self.send_message(
                                    f"[id{self.db.vk_id}|{self.db.name}], ваш баланс: {'{0:,}'.format(self.db.gb).replace(',', '.')} GB 💸",
                                    chat=self.event.chat_id)
                            if self.event.text.lower() == "x2":
                                self.send_message(
                                    f'[id{self.db.vk_id}|{self.db.name}], нажми кнопку ИЛИ введи команду: "2 [сумма ставки]"',
                                    btns.doubleplace_btns(2, self.db.gb), chat=self.event.chat_id)
                            if self.event.text.lower() == "x3":
                                self.send_message(
                                    f'[id{self.db.vk_id}|{self.db.name}], нажми кнопку ИЛИ введи команду: "3 [сумма ставки]"',
                                    btns.doubleplace_btns(3, self.db.gb), chat=self.event.chat_id)
                            if self.event.text.lower() == "x5":
                                self.send_message(
                                    f'[id{self.db.vk_id}|{self.db.name}], нажми кнопку ИЛИ введи команду: "5 [сумма ставки]"',
                                    btns.doubleplace_btns(5, self.db.gb), chat=self.event.chat_id)
                            if self.event.text.lower() == "x50":
                                self.send_message(
                                    f'[id{self.db.vk_id}|{self.db.name}], нажми кнопку ИЛИ введи команду: "50 [сумма ставки]"',
                                    btns.doubleplace_btns(50, self.db.gb), chat=self.event.chat_id)
                            if len(self.event.text.split()) > 1:
                                if self.event.text.lower()[:3] == "x2 " or self.event.text.lower()[:2] == "2 ":
                                    bet = int(
                                        self.event.text.split()[1].replace(".", "").replace("к", "000").replace(",",
                                                                                                                ""))
                                    try:
                                        self.x2[self.event.user_id] += bet
                                    except KeyError:
                                        self.x2[self.event.user_id] = bet
                                    if self.db.gb >= bet:
                                        if bet > 0:
                                            con.execute(
                                                update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                                    gb=self.db.gb - bet))
                                            self.send_message(
                                                f"[id{self.db.vk_id}|{self.db.name}], успешная ставка {'{0:,}'.format(bet).replace(',', '.')} GB на x2",
                                                chat=self.event.chat_id)
                                    else:
                                        self.send_message(
                                            f"[id{self.db.vk_id}|{self.db.name}], на твоём балансе нет столько GB!",
                                            chat=self.event.chat_id)
                                if self.event.text.lower()[:3] == "x3 " or self.event.text.lower()[:2] == "3 ":
                                    bet = int(
                                        self.event.text.split()[1].replace(".", "").replace("к", "000").replace(",",
                                                                                                                ""))
                                    try:
                                        self.x3[self.event.user_id] += bet
                                    except KeyError:
                                        self.x3[self.event.user_id] = bet
                                    if self.db.gb >= bet:
                                        if bet > 0:
                                            con.execute(
                                                update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                                    gb=self.db.gb - bet))
                                            self.send_message(
                                                f"[id{self.db.vk_id}|{self.db.name}], успешная ставка {'{0:,}'.format(bet).replace(',', '.')} GB на x3",
                                                chat=self.event.chat_id)
                                    else:
                                        self.send_message(
                                            f"[id{self.db.vk_id}|{self.db.name}], на твоём балансе нет столько GB!",
                                            chat=self.event.chat_id)
                                if self.event.text.lower()[:3] == "x5 " or self.event.text.lower()[:2] == "5 ":
                                    bet = int(
                                        self.event.text.split()[1].replace(".", "").replace("к", "000").replace(",",
                                                                                                                ""))
                                    try:
                                        self.x5[self.event.user_id] += bet
                                    except KeyError:
                                        self.x5[self.event.user_id] = bet
                                    if self.db.gb >= bet:
                                        if bet > 0:
                                            con.execute(
                                                update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                                    gb=self.db.gb - bet))
                                            self.send_message(
                                                f"[id{self.db.vk_id}|{self.db.name}], успешная ставка {'{0:,}'.format(bet).replace(',', '.')} GB на x5",
                                                chat=self.event.chat_id)
                                    else:
                                        self.send_message(
                                            f"[id{self.db.vk_id}|{self.db.name}], на твоём балансе нет столько GB!",
                                            chat=self.event.chat_id)
                                if self.event.text.lower()[:4] == "x50 " or self.event.text.lower()[:3] == "50 ":
                                    bet = int(
                                        self.event.text.split()[1].replace(".", "").replace("к", "000").replace(",",
                                                                                                                ""))
                                    try:
                                        self.x50[self.event.user_id] += bet
                                    except KeyError:
                                        self.x50[self.event.user_id] = bet
                                    if self.db.gb >= bet:
                                        if bet > 0:
                                            con.execute(
                                                update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                                    gb=self.db.gb - bet))
                                            self.send_message(
                                                f"[id{self.db.vk_id}|{self.db.name}], успешная ставка {'{0:,}'.format(bet).replace(',', '.')} GB на x50",
                                                chat=self.event.chat_id)
                                            print('a')
                                    else:
                                        self.send_message(
                                            f"[id{self.db.vk_id}|{self.db.name}], на твоём балансе нет столько GB!",
                                            chat=self.event.chat_id)
                            if self.event.text.lower() == "рейтинг":
                                all_users_top = con.execute(select(User).where(User.columns.vk_id != 1).
                                                            order_by(desc(User.columns.gb))).fetchall()
                                all_users_top = [x._mapping for x in all_users_top]  # NOQA
                                if len(all_users_top) < 10:
                                    counter = 10
                                else:
                                    counter = len(all_users_top)
                                top = [{"name": fr"[id{x.vk_id}|{x.name}]", "gb": x.gb,
                                        "place": list(all_users_top[:counter]).index(x)} for
                                       x in all_users_top[:counter]]
                                for _ in range(0, counter - len(top)):
                                    top.append({"name": "?", "gb": 0, "place": 0})
                                if len(all_users_top) > 1000:
                                    counter = 1000
                                else:
                                    counter = len(all_users_top)
                                usrp = None
                                for a in range(0, counter):
                                    if self.db.vk_id == all_users_top[a].vk_id:
                                        usrp = numbersToEmoji(a + 1)
                                if usrp == "":
                                    usrp = "➡1️⃣0️⃣0️⃣0️⃣"
                                top.insert(len(top),
                                           {"name": self.db.name, "gb": self.db.gb, "place": usrp})
                                self.send_message(msgs.doublerating_msg(top), chat=self.event.chat_id)
                            if self.event.text.lower() == "бонус":
                                if datetime.now().timestamp() - self.db.doublebonus.timestamp() > 20 * 60:
                                    if self.db.status == "admin":
                                        val = 500
                                    else:
                                        val = 100
                                    con.execute(update(User).where(User.columns.vk_id == self.db.vk_id).values(
                                        gb=self.db.gb + val,
                                        doublebonus=datetime.now()
                                    ))
                                    self.send_message(f"[id{self.db.vk_id}|{self.db.name}], бонус +{val} GB 💵",
                                                      chat=self.event.chat_id)
                                else:
                                    sec = int(20 * 60 - (datetime.now().timestamp() - self.db.doublebonus.timestamp()))
                                    self.send_message(f"[id{self.db.vk_id}|{self.db.name}], до получения бонуса"
                                                      f" {int(sec // 60)} мин. {int(sec % 60)} сек. ⏳",
                                                      chat=self.event.chat_id)
                            if self.event.text.lower() == "донат":
                                self.send_message(f"[id{self.db.vk_id}|{self.db.name}], каталог доната ты можешь"
                                                  f" посмотреть в нашем боте по команде «Донат»",
                                                  chat=self.event.chat_id)
                            if self.event.text.lower()[:3] == "кик":
                                if self.db.status == "admin":
                                    try:
                                        try:
                                            kicking = int(self.event.text.split()[1])
                                        except:
                                            kicking = self.vk.messages.getById(message_ids=[self.event.message_id],
                                                                               extended=1)[
                                                'items'][0]['reply_message']['from_id']
                                        self.vk_session.method("messages.removeChatUser", {
                                            "chat_id": self.event.chat_id,
                                            "member_id": kicking
                                        })
                                        self.send_message(
                                            f"[id{self.db.vk_id}|{self.db.name}], Вы успешно кикнули игрока {utils.getOrCreateUserById().name}.")
                                    except:
                                        self.send_message(
                                            f"[id{self.db.vk_id}|{self.db.name}], Использование: Кик [id игрока]")
                                else:
                                    self.send_message(
                                        f"[id{self.db.vk_id}|{self.db.name}], Этой командой может только админ!")

                            con.commit()
                        else:
                            if self.event.text.lower().find("Поцеловать".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Поцеловали [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Обнять".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Обняли [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Заколдовать".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Заколдовали [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Укусить".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Укусили [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Шлепнуть".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Шлепнули [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Погладить".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Погладили [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Пнуть".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Пнули [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Отсосать".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Отсосали y [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Отлизать".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Отлизали y [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Трахнуть".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Трахнули [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Обоссать".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Обоссали [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Отравить".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Отравили [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Уебать".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Уебали [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Изнасиловать".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Изнасиловали [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                            if self.event.text.lower().find("Кастрировать".lower()) != -1:
                                scope = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'reply_message']['from_id']
                                self.send_message(
                                    f"[id{self.event.user_id}|{self.db.name}], вы Кастрировали [id{scope}|{utils.getOrCreateUserById(scope).name}]",
                                    chat=self.event.chat_id)
                    except:
                        traceback.print_exc()
                if self.event.type == VkEventType.MESSAGE_NEW and self.event.to_me and self.event.from_user:
                    try:
                        try:
                            ltm = self.vk.messages.getHistory(count=2, peer_id=self.event.peer_id)['items'][1]['text']
                        except:
                            ltm = None
                        self.db = utils.getOrCreateUserById(self.event.user_id)
                        name = list(self.vk.users.get(user_ids=self.event.user_id))[0]['first_name']
                        if utils.getOrCreateUserById(self.event.user_id)['name'] == "":
                            try:
                                ref = \
                                    self.vk.messages.getById(message_ids=[self.event.message_id], extended=1)['items'][
                                        0][
                                        'ref']
                                rew = random.randint(30, 55) * 1000000000
                                con.execute(update(User).where(User.columns.vk_id == ref).values(
                                    money=utils.getOrCreateUserById(ref).money + rew
                                ))
                                self.send_message("По вашей скам ссылке зарегался человек."
                                                  f"Вы получили награду {'{0:,}'.format(rew).replace(',', '.')}$.",
                                                  uid=ref)
                            except KeyError:
                                pass
                            conection.execute(update(User).where(User.columns.vk_id == self.event.user_id).values(
                                name=name))

                        if datetime.now().timestamp() - self.db.banned.timestamp() > 0:
                            self.startingV()
                            self.bonusV()
                            self.topV()
                            self.clanV()
                            self.clothesV()
                            self.businessV()
                            self.farmV()
                            self.printerV()
                            self.entertainingV()
                            self.carsV()
                            self.bossesV()
                            self.otherV()
                            self.utilsV()
                            self.shopV()
                            self.petV()
                            self.gamesV()
                            self.miningV()
                            self.questsV()
                            self.presidentV()
                            self.planetsV()
                            self.donate()
                            self.worksV()
                        else:
                            self.send_message(f"Вы забанены до {datetime.strptime()}")
                        self.adminV()

                        con.commit()
                    except:
                        if ltm is not None:
                            traceback.print_exc()


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))
    if not Path("boss.sav").is_file():
        boss = {}
        with open('boss.sav', 'wb') as data:
            pickle.dump([boss], data)
            data.close()
        print('created: "boss.sav"')
    if not Path("lasttick.sav").is_file():
        lasttick = datetime.now()
        with open('lasttick.sav', 'wb') as data:
            pickle.dump([lasttick], data)
            data.close()
        print('created: "lasttick.sav"')
    if not Path("president.sav").is_file():
        president = 0
        with open('president.sav', 'wb') as data:
            pickle.dump([president], data)
            data.close()
        print('created: "president.sav"')
    if not Path("lastenergy.sav").is_file():
        lastenergy = datetime.now()
        with open('lastenergy.sav', 'wb') as data:
            pickle.dump([lastenergy], data)
            data.close()
        print('created: "lastenergy.sav"')
    if not con.dialect.has_table(con, "Users") or con.dialect.has_table(con, "Users") is None:
        print('tables created: "User", "Clan"')
        metadata.create_all(dbu)
    print('starting')
    VkBot().run()
