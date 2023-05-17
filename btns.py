# -*- coding: utf-8 -*-
from vk_api.keyboard import VkKeyboard


def back():
    kb = VkKeyboard()
    kb.add_button("Назад")
    return kb


def start_btn():
    kb = VkKeyboard(inline=True)
    kb.add_openlink_button("Добавить бота в беседу", "https://www.vk.com")
    kb1 = VkKeyboard()
    kb1.add_button("🎁 Бонус", color="positive")
    kb1.add_button("🏆 Топ", color="positive")
    kb1.add_line()
    kb1.add_button("⚔ Клан", color="primary")
    kb1.add_button("👔 Одежда", color="primary")
    kb1.add_button("💼 Бизнес", color="primary")
    kb1.add_line()
    kb1.add_button("💾 Ферма", color="primary")
    kb1.add_button("🐴 Машина", color="primary")
    kb1.add_button("⚒ Работа", color="primary")
    kb1.add_line()
    kb1.add_button("Босс", color="negative")
    kb1.add_button("Помощь")
    return [kb, kb1]


def help_btns():
    kb = VkKeyboard(inline=True)
    kb.add_button("Развлекательное", color='positive')
    kb.add_button("Разное", color='positive')
    kb.add_button("Игры", color='positive')
    return kb


def top_btn():
    kb = VkKeyboard(inline=True)
    kb.add_button("⚔ ТОП кланов", color="primary")
    return kb


def baseUp_btn():
    kb = VkKeyboard(inline=True)
    kb.add_button("Клан улучшить", color='positive')
    return kb


def clothes_btns():
    kb = VkKeyboard(inline=True)
    kb.add_button('Прическа', color='positive')
    kb.add_button('Тату', color='positive')
    kb.add_button('Голова', color='positive')
    kb.add_line()
    kb.add_button('Футболка', color='positive')
    kb.add_button('Костюм', color='positive')
    kb.add_button('Обувь', color='positive')
    kb.add_line()
    kb.add_button('Аксессуары', color='positive')
    return kb


def backToClothes_btn():
    kb = VkKeyboard(inline=True)
    kb.add_button("Одежда")
    return kb


def business_btns(upgrade):
    kb = VkKeyboard(inline=True)
    kb.add_button("💰 Бизнес снять", color='primary')
    if not upgrade:
        kb.add_button("⬆ Бизнес улучшить", color='primary')
    return kb


def printer_btns():
    kb = VkKeyboard(inline=True)
    kb.add_button("💰 Принтер снять", color='positive')
    kb.add_button("🎨 Принтер заправить", color='primary')
    return kb


def car_btns():
    kb = VkKeyboard(inline=True)
    kb.add_button("⬆ Машина улучшить", color='primary')
    kb.add_button("🏆 ТОП гонщиков", color='negative')
    kb.add_button("🏁 Гонка", color='positive')
    return kb


def boss_btns():
    kb = VkKeyboard(inline=True)
    kb.add_button("👊 Босс сила", color='positive')
    kb.add_button("🔨 Босс атака", color='negative')
    return kb


def case_btns(db):
    kb = VkKeyboard(inline=True)
    if db.scase != 0:
        kb.add_button("📦 Сюрприз Кейс", color='primary')
    if db.pcase != 0:
        kb.add_button("📦 Платинум Кейс", color='negative')
    if db.dcase != 0:
        kb.add_button("📦 Донат Кейс", color='positive')
    if db.scase != 0 or db.dcase != 0 or db.pcase != 0:
        return kb
    else:
        return None


def potions_btns():
    kb = VkKeyboard()
    kb.add_button("Зелье Удачи", color='primary')
    kb.add_button("Зелье Шахтера", color='primary')
    kb.add_button("Зелье Неудачи", color='primary')
    kb.add_button("Зелье Энергии", color='primary')
    kb.add_button("Молоко", color='negative')
    return kb


def pet_btns():
    kb = VkKeyboard(inline=True)
    kb.add_button("🥕 Питомец покормить", color='primary')
    kb.add_button("🎮 Питомец поиграть", color='primary')
    kb.add_line()
    kb.add_button("🌳 Питомец поход", color='positive')
    return kb


def casinoAgain_btns(bet, c):
    kb = VkKeyboard(inline=True)
    kb.add_button(f"Казино {bet // 2}", color=c)
    kb.add_button(f"Казино {bet}", color=c)
    kb.add_button(f"Казино {bet * 2}", color=c)
    return kb


def safe_btns(r):
    kb = VkKeyboard(inline=True)
    kb.add_button(f"Сейф {r}")
    return kb


def mine_btns(db):
    kb = VkKeyboard(inline=True)
    kb.add_button("⛏ Железо")
    if db.xp >= 300:
        kb.add_button("⛏ Золото")
    if db.xp < 300:
        kb.add_button("⛏ Золото", color="negative")
    if db.xp >= 1000:
        kb.add_button("⛏ Алмазы")
    if db.xp < 1000:
        kb.add_button("⛏ Алмазы", color="negative")
    kb.add_line()
    if db.xp >= 10000:
        kb.add_button("⛏ Вещество")
    if db.xp < 10000:
        kb.add_button("⛏ Вещество", color="negative")
    if db.lvl >= 10:
        kb.add_button("⛏ Антивещество")
    else:
        kb.add_button("⛏ Антивещество", color="negative")
    return kb


def minemore_btn(mining):
    kb = VkKeyboard(inline=True)
    kb.add_button(mining)
    return kb


def hike_btns():
    kb = VkKeyboard(inline=True)
    kb.add_button("⬅️ Налево")
    kb.add_button("⬆️ Прямо")
    kb.add_button("➡️ Направо")
    return kb


def federal_btns():
    kb = VkKeyboard()
    kb.add_button("Получить слово", color='positive')
    kb.add_button("Топ федералов", color='primary')
    kb.add_line()
    kb.add_button("🚪 Выйти", color='negative')
    return kb


def correctword_btns():
    kb = VkKeyboard()
    kb.add_button("Федерал", color='primary')
    kb.add_button("Получить слово", color='positive')
    return kb


def word_btns():
    kb = VkKeyboard()
    kb.add_button("❌ Отмена", color='negative')
    kb.add_button("Сменить слово", color='primary')
    return kb


def dive_btns():
    kb = VkKeyboard(inline=True)
    kb.add_button("🐟 Подводное плавание")
    return kb


def works_btns():
    kb = VkKeyboard(inline=True)
    kb.add_button("scum 2.0", color="positive")
    kb.add_button("лайкир")
    kb.add_line()
    kb.add_button("коментатор")
    kb.add_button("публицист")
    kb.add_line()
    kb.add_button("эсперант")
    kb.add_button("кладовщик")
    return kb


def double_btns():
    kb = VkKeyboard()
    kb.add_button("Банк", color="positive")
    kb.add_button("Баланс", color="positive")
    kb.add_line()
    kb.add_button("x2", color="primary")
    kb.add_button("x3", color="primary")
    kb.add_button("x5", color="primary")
    kb.add_line()
    kb.add_button("x50", color="positive")
    kb.add_line()
    kb.add_button("Рейтинг", color="negative")
    kb.add_button("Донат")
    kb.add_button("Бонус")
    return kb


def doubleplace_btns(x, m):
    kb = VkKeyboard(inline=True)
    kb.add_button(f"x{x} {int(m/4)}")
    kb.add_button(f"x{x} {int(m/2)}")
    kb.add_button(f"x{x} {m}")
    return kb


def gonum_btn():
    kb = VkKeyboard(inline=True)
    kb.add_button("🎫 Сменить госномер")
    kb.add_button("💼 Чемодан")
    return kb


def putgonum():
    kb = VkKeyboard(inline=True)
    kb.add_button("Положить госномер", color='positive')
    return kb
