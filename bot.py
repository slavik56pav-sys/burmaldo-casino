#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, BotCommand, MenuButtonCommands
from flask import Flask, request, jsonify
import sqlite3
import random
import threading
import time
import os
from datetime import datetime, timedelta
import secrets

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8684953028:AAEeLaicBO61TCHx3U-Emrupf-XSVjRy5fQ"
ADMIN_IDS = [8609901924]
WEB_PORT = int(os.environ.get("PORT", 5000))
MAX_BALANCE = 9999999999
WEB_URL = "https://burmaldo-casino.onrender.com"

# ========== ЭКОНОМИКА ==========
MIN_BET = 100
START_BALANCE = 500

# ========== ВРЕМЕННЫЕ ХРАНИЛИЩА ==========
upgrade_states = {}
mining_states = {}
market_states = {}# ========== ВСЕ РЕАЛЬНЫЕ ПОДЫ VOOPOO ==========

# Обычные (VINCI, VMATE) - 35 шт
COMMON_PODS = [
    "VINCI", "VINCI X", "VINCI Q", "VINCI Spark", "VINCI Royal",
    "VINCI 2", "VINCI 3", "VINCI Pro", "VINCI Max", "VINCI Air",
    "VINCI Nano", "VINCI Pod", "VINCI Pod 2", "VINCI Flex", "VINCI Edge",
    "VMATE", "VMATE E", "VMATE Infinity", "VMATE Pro", "VMATE Max",
    "VMATE 2", "VMATE 3", "VMATE Air", "VMATE Nano", "VMATE Flex",
    "VMATE Pod", "VMATE Pod 2", "VMATE Plus", "VMATE Ultra", "VMATE X"
]

# Необычные (ARGUS Pod, PNP, TPP, MAAT) - 35 шт
UNCOMMON_PODS = [
    "ARGUS Pod", "ARGUS Pod 2", "ARGUS Pod 3", "ARGUS Pod Pro", "ARGUS Pod Max",
    "ARGUS Cartridge", "ARGUS Cartridge 2", "ARGUS Cartridge Pro", "ARGUS Tank", "ARGUS Tank Pro",
    "MAAT Tank", "MAAT Tank Pro", "MAAT Tank Max", "MAAT Rebuildable", "MAAT RBA",
    "PNP Pod", "PNP Pod 2", "PNP Pod Pro", "PNP Coil", "PNP Coil 2",
    "TPP Pod", "TPP Pod 2", "TPP Pod Pro", "TPP Coil", "TPP Coil 2"
]

# Редкие (ARGUS GT) - 35 шт
RARE_PODS = [
    "ARGUS GT", "ARGUS XT", "ARGUS Air", "ARGUS Pro", "ARGUS Max",
    "ARGUS 2", "ARGUS 3", "ARGUS Nano", "ARGUS Flex", "ARGUS Edge",
    "ARGUS GT 2", "ARGUS XT Pro", "ARGUS Air Max", "ARGUS Pro Ultra", "ARGUS Max Plus",
    "ARGUS Travel", "ARGUS Explorer", "ARGUS Adventure", "ARGUS Sport", "ARGUS Racing",
    "ARGUS G", "ARGUS P", "ARGUS M", "ARGUS Z", "ARGUS MT"
]

# Эпические (DRAG X) - 35 шт
EPIC_PODS = [
    "DRAG X", "DRAG X Plus", "DRAG X Pro", "DRAG X Max", "DRAG X Ultra",
    "DRAG X 2", "DRAG X 3", "DRAG X Nano", "DRAG X Air", "DRAG X Flex",
    "DRAG X Special", "DRAG X Edition", "DRAG X Limited", "DRAG X Premium", "DRAG X Deluxe",
    "DRAG X Pro Plus", "DRAG X Pro Max", "DRAG X Ultra Pro", "DRAG X Ultra Max", "DRAG X Ultimate",
    "DRAG X 2 Pro", "DRAG X 2 Max", "DRAG X 3 Pro", "DRAG X 3 Max", "DRAG X Flex Pro"
]

# Мифические (DRAG S) - 35 шт
MYTHIC_PODS = [
    "DRAG S", "DRAG S Plus", "DRAG S Pro", "DRAG S Max", "DRAG S Ultra",
    "DRAG S 2", "DRAG S 3", "DRAG S Nano", "DRAG S Air", "DRAG S Flex",
    "DRAG S Special", "DRAG S Edition", "DRAG S Limited", "DRAG S Premium", "DRAG S Deluxe",
    "DRAG S Pro Plus", "DRAG S Pro Max", "DRAG S Ultra Pro", "DRAG S Ultra Max", "DRAG S Ultimate",
    "DRAG S 2 Pro", "DRAG S 2 Max", "DRAG S 3 Pro", "DRAG S 3 Max", "DRAG S Flex Pro"
]

# Легендарные (DRAG 4/5) - 35 шт
LEGENDARY_PODS = [
    "DRAG 4", "DRAG 5", "DRAG 4 Pro", "DRAG 5 Pro", "DRAG 4 Max",
    "DRAG 5 Ultra", "DRAG 4 Plus", "DRAG 5 Plus", "DRAG 4 Titan", "DRAG 5 Titan",
    "DRAG 4 X", "DRAG 5 X", "DRAG 4 S", "DRAG 5 S", "DRAG 4 R",
    "DRAG 5 R", "DRAG 4 GT", "DRAG 5 GT", "DRAG 4 Ultimate", "DRAG 5 Ultimate",
    "DRAG Anniversary", "DRAG Special", "DRAG Edition", "DRAG Limited", "DRAG Premium"
]

# Хроматические (XROS 1-6) - 55 шт
CHROMATIC_PODS = [
    "XROS", "XROS Nano", "XROS Mini", "XROS Air", "XROS Ultra",
    "XROS Pro", "XROS Max", "XROS 2", "XROS 2 Nano", "XROS 2 Mini",
    "XROS 2 Air", "XROS 2 Ultra", "XROS 2 Pro", "XROS 2 Max",
    "XROS 3", "XROS 3 Nano", "XROS 3 Mini", "XROS 3 Air", "XROS 3 Ultra",
    "XROS 3 Pro", "XROS 3 Max", "XROS 4", "XROS 4 Nano", "XROS 4 Mini",
    "XROS 4 Air", "XROS 4 Ultra", "XROS 4 Pro", "XROS 4 Max",
    "XROS 5", "XROS 5 Nano", "XROS 5 Mini", "XROS 5 Air", "XROS 5 Ultra",
    "XROS 5 Pro", "XROS 5 Max", "XROS 6", "XROS 6 Nano", "XROS 6 Mini",
    "XROS 6 Air", "XROS 6 Ultra", "XROS 6 Pro", "XROS 6 Max",
    "XROS Pod", "XROS Cartridge", "XROS Limited", "XROS Special", "XROS Edition"
]# ========== РЕДКОСТИ ПОДОВ С НИЗКИМИ ШАНСАМИ ==========
POD_RARITIES = {
    'Обычный': {
        'pods': COMMON_PODS, 'chance': 30, 'price': 100, 'mining_rate': 1,
        'emoji': '⬜', 'color': '#808080', 'next': 'Необычный', 'upgrade_chance': 40
    },
    'Необычный': {
        'pods': UNCOMMON_PODS, 'chance': 25, 'price': 250, 'mining_rate': 2,
        'emoji': '🟢', 'color': '#00ff00', 'next': 'Редкий', 'upgrade_chance': 25
    },
    'Редкий': {
        'pods': RARE_PODS, 'chance': 15, 'price': 500, 'mining_rate': 3,
        'emoji': '🔵', 'color': '#0088ff', 'next': 'Эпический', 'upgrade_chance': 15
    },
    'Эпический': {
        'pods': EPIC_PODS, 'chance': 10, 'price': 1000, 'mining_rate': 5,
        'emoji': '🟣', 'color': '#aa00ff', 'next': 'Мифический', 'upgrade_chance': 8
    },
    'Мифический': {
        'pods': MYTHIC_PODS, 'chance': 7, 'price': 2500, 'mining_rate': 8,
        'emoji': '🟠', 'color': '#ff8800', 'next': 'Легендарный', 'upgrade_chance': 4
    },
    'Легендарный': {
        'pods': LEGENDARY_PODS, 'chance': 4, 'price': 5000, 'mining_rate': 12,
        'emoji': '🔴', 'color': '#ff4400', 'next': 'Хроматический', 'upgrade_chance': 1
    },
    'Хроматический': {
        'pods': CHROMATIC_PODS, 'chance': 2, 'price': 10000, 'mining_rate': 20,
        'emoji': '💜', 'color': '#ff00ff', 'next': None, 'upgrade_chance': 0
    }
}

def get_random_pod():
    rand = random.random() * 100
    cumulative = 0
    for rarity, data in POD_RARITIES.items():
        cumulative += data['chance']
        if rand <= cumulative:
            pod_name = random.choice(data['pods'])
            return {
                'name': pod_name, 'rarity': rarity,
                'price': data['price'], 'mining_rate': data['mining_rate'],
                'emoji': data['emoji'], 'color': data['color'],
                'upgrade_chance': data.get('upgrade_chance', 0),
                'next': data.get('next')
            }
    return {
        'name': COMMON_PODS[0], 'rarity': 'Обычный',
        'price': 100, 'mining_rate': 1, 'emoji': '⬜', 'color': '#808080',
        'upgrade_chance': 40, 'next': 'Необычный'
}# ========== БАЗА ДАННЫХ ==========
def get_db():
    conn = sqlite3.connect('casino.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE,
        username TEXT,
        balance INTEGER DEFAULT {},
        last_daily_time TIMESTAMP,
        games_played INTEGER DEFAULT 0,
        total_won INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0
    )'''.format(START_BALANCE))
    conn.execute('''CREATE TABLE IF NOT EXISTS user_pods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        pod_name TEXT,
        rarity TEXT,
        level INTEGER DEFAULT 1,
        mining_rate INTEGER,
        is_listed INTEGER DEFAULT 0,
        list_price INTEGER DEFAULT 0
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS market_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id TEXT,
        pod_id INTEGER,
        price INTEGER,
        listed_at TIMESTAMP
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS active_mining (
        user_id TEXT PRIMARY KEY,
        pod_id INTEGER,
        start_time TIMESTAMP,
        last_claim TIMESTAMP
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS user_upgrades (
        user_id TEXT PRIMARY KEY,
        cooldown_level INTEGER DEFAULT 0,
        luck_level INTEGER DEFAULT 0,
        farm_level INTEGER DEFAULT 0,
        limit_level INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

init_db()# ========== ОСНОВНЫЕ ФУНКЦИИ ==========
def get_user(telegram_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (str(telegram_id),)).fetchone()
    conn.close()
    return user

def create_user(telegram_id, username):
    conn = get_db()
    conn.execute("INSERT INTO users (telegram_id, username, balance, last_daily_time) VALUES (?, ?, {}, ?)".format(START_BALANCE),
                 (str(telegram_id), username, datetime.now() - timedelta(hours=4)))
    conn.commit()
    conn.close()

def get_balance(telegram_id):
    user = get_user(telegram_id)
    return user['balance'] if user else START_BALANCE

def update_balance(telegram_id, amount):
    conn = get_db()
    current = get_balance(telegram_id)
    new_balance = max(0, min(current + amount, MAX_BALANCE))
    conn.execute("UPDATE users SET balance = ? WHERE telegram_id = ?", (new_balance, str(telegram_id)))
    conn.commit()
    conn.close()
    return new_balance

def update_stats(telegram_id, bet, win):
    conn = get_db()
    conn.execute("UPDATE users SET games_played = games_played + 1, total_won = total_won + ? WHERE telegram_id = ?", 
                 (win if win > 0 else 0, str(telegram_id)))
    conn.commit()
    conn.close()

def is_admin(user_id):
    user = get_user(user_id)
    return user['is_admin'] == 1 if user else False

def make_admin(telegram_id):
    conn = get_db()
    conn.execute("UPDATE users SET is_admin = 1 WHERE telegram_id = ?", (str(telegram_id),))
    conn.commit()
    conn.close()

# ========== ФУНКЦИИ ДЛЯ ПОДОВ ==========
def add_pod_to_user(user_id, pod_name, rarity, mining_rate):
    conn = get_db()
    conn.execute("INSERT INTO user_pods (user_id, pod_name, rarity, mining_rate) VALUES (?, ?, ?, ?)",
                 (str(user_id), pod_name, rarity, mining_rate))
    conn.commit()
    conn.close()

def get_user_pods(user_id):
    conn = get_db()
    pods = conn.execute("SELECT * FROM user_pods WHERE user_id = ?", (str(user_id),)).fetchall()
    conn.close()
    return pods

def get_pod_by_id(pod_id):
    conn = get_db()
    pod = conn.execute("SELECT * FROM user_pods WHERE id = ?", (pod_id,)).fetchone()
    conn.close()
    return pod

def delete_pod(pod_id):
    conn = get_db()
    conn.execute("DELETE FROM user_pods WHERE id = ?", (pod_id,))
    conn.commit()
    conn.close()

# ========== ФУНКЦИИ УЛУЧШЕНИЙ ==========
UPGRADE_COSTS = {
    'cooldown': [0, 5000, 12000, 22000, 35000, 52000, 73000, 98000, 128000, 163000, 205000],
    'luck': [0, 8000, 18000, 32000, 50000, 72000, 98000, 128000, 162000, 200000, 242000],
    'farm': [0, 10000, 20000, 35000, 55000, 80000, 110000, 150000, 200000, 260000, 330000],
    'limit': [0, 15000, 30000, 50000, 75000, 105000, 140000, 180000, 225000, 275000, 330000]
}

def get_user_upgrades(user_id):
    conn = get_db()
    upgrades = conn.execute("SELECT * FROM user_upgrades WHERE user_id = ?", (str(user_id),)).fetchone()
    conn.close()
    if not upgrades:
        return {'cooldown_level': 0, 'luck_level': 0, 'farm_level': 0, 'limit_level': 0}
    return upgrades

def get_cooldown_hours(level):
    base_hours = 4
    reduction = level * 0.2
    return max(2, base_hours - reduction)

def get_luck_bonus(level): return min(level * 3, 30)
def get_farm_bonus(level): return level
def get_limit_bonus(level): return level# ========== CRASH GAME ==========
def generate_crash_point():
    rand = random.random() * 100
    if rand < 50: return round(random.uniform(1.1, 2.0), 2)
    elif rand < 75: return round(random.uniform(2.0, 3.0), 2)
    elif rand < 90: return round(random.uniform(3.0, 5.0), 2)
    elif rand < 97: return round(random.uniform(5.0, 10.0), 2)
    elif rand < 99: return round(random.uniform(10.0, 25.0), 2)
    else: return round(random.uniform(25.0, 75.0), 2)

game_state = 'betting'
current_multiplier = 1.00
crash_point = 0.00
betting_timer = 10
round_timer = 5
crash_history = []
user_bets = {}
current_round_id = 0

def game_loop():
    global game_state, current_multiplier, crash_point, betting_timer, crash_history, user_bets, round_timer, current_round_id
    while True:
        if game_state == 'betting':
            time.sleep(1)
            betting_timer -= 1
            if betting_timer <= 0:
                game_state = 'flying'
                current_multiplier = 1.00
                crash_point = generate_crash_point()
                current_round_id += 1
                print(f"Round {current_round_id} started! Crash at {crash_point}x")
                betting_timer = 10
        elif game_state == 'flying':
            time.sleep(0.07)
            current_multiplier = round(current_multiplier + 0.04, 2)
            auto_list = []
            for uid, bet_info in list(user_bets.items()):
                if not bet_info.get('cashed_out', False):
                    auto_cash = bet_info.get('auto_cash', 0)
                    if auto_cash > 0 and current_multiplier >= auto_cash:
                        win = int(bet_info['bet'] * current_multiplier)
                        update_balance(uid, win)
                        update_stats(uid, bet_info['bet'], win)
                        bet_info['cashed_out'] = True
                        auto_list.append(uid)
            for uid in auto_list:
                if uid in user_bets: del user_bets[uid]
            if current_multiplier >= crash_point:
                game_state = 'crashed'
                print(f"CRASH at {crash_point}x!")
                for uid, bet_info in list(user_bets.items()):
                    if not bet_info.get('cashed_out', False):
                        update_stats(uid, bet_info['bet'], -bet_info['bet'])
                crash_history.insert(0, crash_point)
                if len(crash_history) > 10: crash_history.pop()
                user_bets.clear()
                def next_round():
                    global game_state, betting_timer
                    time.sleep(round_timer)
                    game_state = 'betting'
                    betting_timer = 10
                threading.Thread(target=next_round, daemon=True).start()
        elif game_state == 'crashed':
            time.sleep(1)

threading.Thread(target=game_loop, daemon=True).start()# ========== TELEGRAM БОТ ==========
bot = telebot.TeleBot(BOT_TOKEN)

def setup_menu():
    commands = [
        BotCommand("start", "Главное меню"),
        BotCommand("casino", "Открыть казино"),
        BotCommand("daily", "Ежедневный под"),
        BotCommand("mypods", "Мои поды"),
        BotCommand("balance", "Баланс"),
        BotCommand("mine", "Майнинг"),
        BotCommand("shop", "Магазин улучшений"),
        BotCommand("market", "Рынок"),
        BotCommand("upgrade", "Апгрейд пода"),
        BotCommand("admins", "Админ-панель"),
        BotCommand("help", "Помощь")
    ]
    bot.set_my_commands(commands)
    bot.set_chat_menu_button(menu_button=MenuButtonCommands())

setup_menu()

# ========== ГЛАВНОЕ МЕНЮ ==========
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        KeyboardButton("🎰 КАЗИНО"), KeyboardButton("🎁 DAILY"),
        KeyboardButton("📦 МОИ ПОДЫ"), KeyboardButton("⛏️ МАЙНИНГ"),
        KeyboardButton("💰 БАЛАНС"), KeyboardButton("🏪 МАГАЗИН"),
        KeyboardButton("🏪 РЫНОК"), KeyboardButton("🔄 АПГРЕЙД"),
        KeyboardButton("👑 АДМИНЫ"), KeyboardButton("❓ ПОМОЩЬ")
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    if not get_user(user_id): create_user(user_id, username)
    bot.send_message(message.chat.id, 
        f"🐐 БУРМАЛДАТОЕ CASINO 🐐\n\n"
        f"💰 Тяжки: {get_balance(user_id):,}\n"
        f"🎲 Мин. ставка: {MIN_BET} тяжек\n\n"
        f"Выберите действие:", 
        reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "🎰 КАЗИНО")
def casino_button(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎰 ВОЙТИ В КАЗИНО", url=f"{WEB_URL}?tg_id={user_id}&tg_name={username}"))
    bot.send_message(message.chat.id, "Нажмите на кнопку:", reply_markup=kb)

@bot.message_handler(commands=['casino'])
def casino_cmd(message): casino_button(message)

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def balance_button(message): 
    bot.reply_to(message, f"💰 ТЯЖКИ: {get_balance(message.from_user.id):,}")

@bot.message_handler(commands=['balance'])
def balance_cmd(message): balance_button(message)

@bot.message_handler(func=lambda m: m.text == "❓ ПОМОЩЬ")
def help_button(message): help_cmd(message)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message,
        f"❓ ПОМОЩЬ\n\n"
        f"🎮 ИГРЫ: /casino - Crash, Слоты, Рулетка, Мины\n"
        f"📦 ПОДЫ: /daily, /mypods, /upgrade ID, /sell ID\n"
        f"⛏️ МАЙНИНГ: /mine start/claim/stop\n"
        f"🏪 МАГАЗИН: /shop\n"
        f"🏪 РЫНОК: /list, /market, /buy\n"
        f"👑 АДМИНЫ: /admins")# ========== ЕЖЕДНЕВНЫЕ ПОДЫ ==========
@bot.message_handler(commands=['daily'])
def daily_pod(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if not user:
        create_user(user_id, message.from_user.username or "player")
        user = get_user(user_id)
    
    last_daily = datetime.fromisoformat(user['last_daily_time']) if user['last_daily_time'] else datetime.now() - timedelta(hours=4)
    now = datetime.now()
    upgrades = get_user_upgrades(user_id)
    
    cooldown_hours = get_cooldown_hours(upgrades['cooldown_level'])
    time_diff = (now - last_daily).total_seconds()
    cooldown_seconds = cooldown_hours * 3600
    
    if time_diff < cooldown_seconds:
        remaining = int((cooldown_seconds - time_diff) / 3600)
        minutes = int(((cooldown_seconds - time_diff) % 3600) / 60)
        bot.reply_to(message, f"⏰ Следующий под через {remaining} ч {minutes} мин!\n📊 Ваша перезарядка: {cooldown_hours}ч (улучшение: +{upgrades['cooldown_level']} ур.)")
        return
    
    luck_bonus = get_luck_bonus(upgrades['luck_level'])
    limit_bonus = get_limit_bonus(upgrades['limit_level']) + 1
    farm_bonus = get_farm_bonus(upgrades['farm_level'])
    
    text = f"🎁 ВЫ ПОЛУЧИЛИ ПОДЫ!\n\n📊 Ваши улучшения:\n"
    text += f"• Удача: +{luck_bonus}%\n"
    text += f"• Лимит: +{limit_bonus} под(а)\n"
    text += f"• Ферма: +{farm_bonus} тяжек/час\n\n"
    
    for _ in range(limit_bonus):
        rand = random.random() * 100
        cum = 0
        selected = None
        for rarity, data in POD_RARITIES.items():
            modified_chance = data['chance'] + (luck_bonus if rarity != 'Хроматический' else 0)
            cum += modified_chance
            if rand <= cum:
                selected = rarity
                break
        if not selected:
            selected = 'Обычный'
        pod_data = POD_RARITIES[selected]
        pod_name = random.choice(pod_data['pods'])
        add_pod_to_user(user_id, pod_name, selected, pod_data['mining_rate'] + farm_bonus)
        text += f"{pod_data['emoji']} {pod_name} ({selected}) ⛏️{pod_data['mining_rate'] + farm_bonus}/ч\n"
    
    conn = get_db()
    conn.execute("UPDATE users SET last_daily_time = ? WHERE telegram_id = ?", (now.isoformat(), str(user_id)))
    conn.commit()
    conn.close()
    
    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: m.text == "🎁 DAILY")
def daily_button(message): daily_pod(message)# ========== МОИ ПОДЫ ==========
@bot.message_handler(commands=['mypods'])
def my_pods(message):
    user_id = message.from_user.id
    pods = get_user_pods(user_id)
    if not pods:
        bot.reply_to(message, "📦 У вас нет подов! Используйте /daily")
        return
    
    kb = InlineKeyboardMarkup(row_width=1)
    for pod in pods[:10]:
        rdata = POD_RARITIES.get(pod['rarity'], {})
        kb.add(InlineKeyboardButton(
            f"{rdata.get('emoji', '📟')} {pod['pod_name']} ({pod['rarity']}) - ⛏️{pod['mining_rate']}/ч",
            callback_data=f"pod_{pod['id']}"
        ))
    
    bot.send_message(message.chat.id, "📦 **ВАШИ ПОДЫ**\n\nНажмите на под для действий:", reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('pod_'))
def pod_actions(call):
    pod_id = int(call.data.split('_')[1])
    pod = get_pod_by_id(pod_id)
    if not pod or pod['user_id'] != str(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Под не найден!", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("💰 ПРОДАТЬ", callback_data=f"sell_{pod_id}"),
        InlineKeyboardButton("🔄 АПГРЕЙДИТЬ", callback_data=f"upgrade_{pod_id}"),
        InlineKeyboardButton("🏪 ВЫСТАВИТЬ", callback_data=f"list_{pod_id}"),
        InlineKeyboardButton("◀️ НАЗАД", callback_data="back_to_pods")
    )
    
    rdata = POD_RARITIES.get(pod['rarity'], {})
    bot.edit_message_text(
        f"📟 **{pod['pod_name']}**\n"
        f"⭐ Редкость: {pod['rarity']} {rdata.get('emoji', '')}\n"
        f"📈 Уровень: {pod['level']}\n"
        f"⛏️ Майнинг: {pod['mining_rate']} тяжек/час\n"
        f"💰 Цена продажи: {rdata.get('price', 100)} тяжек\n\n"
        f"Выберите действие:",
        call.message.chat.id, call.message.message_id,
        reply_markup=kb, parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_pods")
def back_to_pods(call):
    my_pods(call.message)# ========== МАЙНИНГ СИСТЕМА ==========
@bot.message_handler(commands=['mine'])
def mine_menu(message):
    user_id = message.from_user.id
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("▶️ СТАРТ МАЙНИНГ", callback_data="mine_start"),
        InlineKeyboardButton("⏹️ ОСТАНОВИТЬ", callback_data="mine_stop"),
        InlineKeyboardButton("💰 ЗАБРАТЬ", callback_data="mine_claim"),
        InlineKeyboardButton("📊 СТАТУС", callback_data="mine_status")
    )
    bot.send_message(message.chat.id, "⛏️ **МАЙНИНГ**\n\nВыберите действие:", reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "mine_start")
def mine_start(call):
    user_id = call.from_user.id
    pods = get_user_pods(user_id)
    if not pods:
        bot.answer_callback_query(call.id, "❌ У вас нет подов!", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(row_width=1)
    for pod in pods[:10]:
        rdata = POD_RARITIES.get(pod['rarity'], {})
        kb.add(InlineKeyboardButton(
            f"{rdata.get('emoji', '📟')} {pod['pod_name']} - ⛏️{pod['mining_rate']}/ч",
            callback_data=f"mine_select_{pod['id']}"
        ))
    kb.add(InlineKeyboardButton("◀️ НАЗАД", callback_data="mine_back"))
    
    bot.edit_message_text("Выберите под для майнинга:", call.message.chat.id, call.message.message_id, reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('mine_select_'))
def mine_select(call):
    user_id = call.from_user.id
    pod_id = int(call.data.split('_')[2])
    pod = get_pod_by_id(pod_id)
    if not pod or pod['user_id'] != str(user_id):
        bot.answer_callback_query(call.id, "❌ Под не найден!", show_alert=True)
        return
    
    conn = get_db()
    existing = conn.execute("SELECT * FROM active_mining WHERE user_id = ?", (str(user_id),)).fetchone()
    if existing:
        bot.answer_callback_query(call.id, "❌ У вас уже активен майнинг! Остановите его сначала.", show_alert=True)
        conn.close()
        return
    
    upgrades = get_user_upgrades(user_id)
    farm_bonus = get_farm_bonus(upgrades['farm_level'])
    total_rate = pod['mining_rate'] + farm_bonus
    
    conn.execute("INSERT INTO active_mining (user_id, pod_id, start_time, last_claim) VALUES (?, ?, ?, ?)",
                 (str(user_id), pod_id, datetime.now().isoformat(), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    bot.answer_callback_query(call.id, f"✅ Майнинг запущен! {total_rate} тяжек/час", show_alert=True)
    bot.edit_message_text(
        f"✅ **МАЙНИНГ ЗАПУЩЕН!**\n\n"
        f"📟 {pod['pod_name']}\n"
        f"⛏️ Базовая скорость: {pod['mining_rate']} тяжек/час\n"
        f"🌾 Бонус фермы: +{farm_bonus}\n"
        f"📊 Итого: {total_rate} тяжек/час",
        call.message.chat.id, call.message.message_id,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data == "mine_claim")
def mine_claim(call):
    user_id = call.from_user.id
    conn = get_db()
    mining = conn.execute("SELECT * FROM active_mining WHERE user_id = ?", (str(user_id),)).fetchone()
    if not mining:
        bot.answer_callback_query(call.id, "❌ Нет активного майнинга!", show_alert=True)
        conn.close()
        return
    
    pod = get_pod_by_id(mining['pod_id'])
    last_claim = datetime.fromisoformat(mining['last_claim'])
    now = datetime.now()
    hours = (now - last_claim).total_seconds() / 3600
    upgrades = get_user_upgrades(user_id)
    farm_bonus = get_farm_bonus(upgrades['farm_level'])
    earned = int(hours * (pod['mining_rate'] + farm_bonus))
    
    if earned > 0:
        update_balance(user_id, earned)
        conn.execute("UPDATE active_mining SET last_claim = ? WHERE user_id = ?", (now.isoformat(), str(user_id)))
        conn.commit()
        bot.answer_callback_query(call.id, f"⛏️ +{earned} ТЯЖЕК!", show_alert=True)
        bot.edit_message_text(
            f"⛏️ **ВЫ ПОЛУЧИЛИ {earned} ТЯЖЕК!**\n\n"
            f"📟 {pod['pod_name']}\n"
            f"⏱️ Время: {hours:.1f} час(ов)\n"
            f"🌾 Бонус фермы: +{farm_bonus}/ч",
            call.message.chat.id, call.message.message_id,
            parse_mode='Markdown'
        )
    else:
        bot.answer_callback_query(call.id, "⏳ Майнинг ещё не принёс тяжки!", show_alert=True)
    conn.close()

@bot.callback_query_handler(func=lambda call: call.data == "mine_stop")
def mine_stop(call):
    user_id = call.from_user.id
    conn = get_db()
    conn.execute("DELETE FROM active_mining WHERE user_id = ?", (str(user_id),))
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, "✅ Майнинг остановлен!", show_alert=True)
    bot.edit_message_text("✅ **МАЙНИНГ ОСТАНОВЛЕН**", call.message.chat.id, call.message.message_id, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "mine_status")
def mine_status(call):
    user_id = call.from_user.id
    conn = get_db()
    mining = conn.execute("SELECT * FROM active_mining WHERE user_id = ?", (str(user_id),)).fetchone()
    if not mining:
        bot.answer_callback_query(call.id, "❌ Нет активного майнинга!", show_alert=True)
        conn.close()
        return
    
    pod = get_pod_by_id(mining['pod_id'])
    last_claim = datetime.fromisoformat(mining['last_claim'])
    now = datetime.now()
    hours = (now - last_claim).total_seconds() / 3600
    upgrades = get_user_upgrades(user_id)
    farm_bonus = get_farm_bonus(upgrades['farm_level'])
    earned = int(hours * (pod['mining_rate'] + farm_bonus))
    
    bot.answer_callback_query(call.id, f"⛏️ Накоплено: {earned} тяжек", show_alert=True)
    conn.close()

@bot.callback_query_handler(func=lambda call: call.data == "mine_back")
def mine_back(call):
    mine_menu(call.message)

@bot.message_handler(func=lambda m: m.text == "⛏️ МАЙНИНГ")
def mine_button(message): mine_menu(message)# ========== ПРОДАЖА ПОДА ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith('sell_'))
def sell_pod_confirm(call):
    pod_id = int(call.data.split('_')[1])
    pod = get_pod_by_id(pod_id)
    if not pod or pod['user_id'] != str(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Под не найден!", show_alert=True)
        return
    
    price = POD_RARITIES.get(pod['rarity'], {}).get('price', 100)
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ ДА, ПРОДАТЬ", callback_data=f"confirm_sell_{pod_id}"),
        InlineKeyboardButton("❌ ОТМЕНА", callback_data=f"pod_{pod_id}")
    )
    
    bot.edit_message_text(
        f"💰 **ПОДТВЕРДИТЕ ПРОДАЖУ**\n\n"
        f"📟 {pod['pod_name']}\n"
        f"⭐ {pod['rarity']}\n"
        f"💰 Цена: {price} тяжек\n\n"
        f"❓ Продать?",
        call.message.chat.id, call.message.message_id,
        reply_markup=kb, parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_sell_'))
def confirm_sell(call):
    pod_id = int(call.data.split('_')[2])
    pod = get_pod_by_id(pod_id)
    if not pod or pod['user_id'] != str(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Под не найден!", show_alert=True)
        return
    
    price = POD_RARITIES.get(pod['rarity'], {}).get('price', 100)
    delete_pod(pod_id)
    update_balance(call.from_user.id, price)
    bot.answer_callback_query(call.id, f"✅ Продан за {price} тяжек!", show_alert=True)
    bot.edit_message_text(
        f"✅ **ПОД ПРОДАН!**\n\n"
        f"📟 {pod['pod_name']}\n"
        f"💰 +{price} ТЯЖЕК",
        call.message.chat.id, call.message.message_id,
        parse_mode='Markdown'
    )

# ========== РЫНОК ==========
@bot.message_handler(commands=['list'])
def list_pod(message):
    user_id = message.from_user.id
    pods = get_user_pods(user_id)
    if not pods:
        bot.reply_to(message, "📦 У вас нет подов для продажи!")
        return
    
    kb = InlineKeyboardMarkup(row_width=1)
    for pod in pods[:10]:
        if pod['is_listed'] == 0:
            rdata = POD_RARITIES.get(pod['rarity'], {})
            kb.add(InlineKeyboardButton(
                f"{rdata.get('emoji', '📟')} {pod['pod_name']} ({pod['rarity']})",
                callback_data=f"list_select_{pod['id']}"
            ))
    
    if not kb.keyboard:
        bot.reply_to(message, "❌ Нет доступных подов для выставления!")
        return
    
    bot.send_message(message.chat.id, "🏪 **ВЫБЕРИТЕ ПОД ДЛЯ ПРОДАЖИ:**", reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('list_select_'))
def list_price_input(call):
    pod_id = int(call.data.split('_')[2])
    market_states[call.from_user.id] = {'pod_id': pod_id}
    msg = bot.send_message(call.message.chat.id, "💰 Введите цену в тяжках:")
    bot.register_next_step_handler(msg, process_list_price)

def process_list_price(message):
    user_id = message.from_user.id
    try:
        price = int(message.text)
        if price < 10:
            bot.reply_to(message, "❌ Минимальная цена 10 тяжек!")
            return
        
        state = market_states.get(user_id)
        if not state:
            bot.reply_to(message, "❌ Ошибка! Попробуйте снова.")
            return
        
        pod_id = state['pod_id']
        pod = get_pod_by_id(pod_id)
        if not pod or pod['user_id'] != str(user_id):
            bot.reply_to(message, "❌ Под не найден!")
            return
        
        conn = get_db()
        conn.execute("UPDATE user_pods SET is_listed = 1, list_price = ? WHERE id = ?", (price, pod_id))
        conn.execute("INSERT INTO market_listings (seller_id, pod_id, price, listed_at) VALUES (?, ?, ?, ?)",
                     (str(user_id), pod_id, price, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, f"✅ **ПОД ВЫСТАВЛЕН!**\n\n📟 {pod['pod_name']}\n💰 Цена: {price} тяжек")
        del market_states[user_id]
    except ValueError:
        bot.reply_to(message, "❌ Введите число!")

@bot.message_handler(commands=['market'])
def market_cmd(message):
    conn = get_db()
    listings = conn.execute('''SELECT m.id, m.price, m.seller_id, u.username, p.pod_name, p.rarity 
        FROM market_listings m JOIN user_pods p ON m.pod_id = p.id 
        LEFT JOIN users u ON m.seller_id = u.telegram_id 
        WHERE m.seller_id != ? AND p.is_listed = 1 ORDER BY m.listed_at DESC''', (str(message.from_user.id),)).fetchall()
    conn.close()
    
    if not listings:
        bot.reply_to(message, "🏪 **РЫНОК ПУСТ**\n\nВыставите свой под: /list")
        return
    
    kb = InlineKeyboardMarkup(row_width=1)
    for l in listings[:20]:
        emoji = POD_RARITIES.get(l['rarity'], {}).get('emoji', '📟')
        kb.add(InlineKeyboardButton(
            f"{emoji} {l['pod_name']} - {l['price']} тяжек (@{l['username'] or l['seller_id'][:8]})",
            callback_data=f"buy_{l['id']}"
        ))
    
    bot.send_message(message.chat.id, "🏪 **ВТОРИЧНЫЙ РЫНОК**\n\nНажмите на под для покупки:", reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def buy_pod(call):
    listing_id = int(call.data.split('_')[1])
    user_id = call.from_user.id
    
    conn = get_db()
    listing = conn.execute('''SELECT m.*, p.pod_name, p.rarity, p.mining_rate, p.user_id as owner_id
        FROM market_listings m JOIN user_pods p ON m.pod_id = p.id WHERE m.id = ?''', (listing_id,)).fetchone()
    
    if not listing:
        bot.answer_callback_query(call.id, "❌ Объявление не найдено!", show_alert=True)
        conn.close()
        return
    
    if listing['seller_id'] == str(user_id):
        bot.answer_callback_query(call.id, "❌ Нельзя купить свой под!", show_alert=True)
        conn.close()
        return
    
    balance = get_balance(user_id)
    if balance < listing['price']:
        bot.answer_callback_query(call.id, f"❌ Нужно {listing['price']} тяжек!", show_alert=True)
        conn.close()
        return
    
    conn.execute("UPDATE user_pods SET user_id = ?, is_listed = 0, list_price = 0 WHERE id = ?", 
                 (str(user_id), listing['pod_id']))
    conn.execute("DELETE FROM market_listings WHERE id = ?", (listing_id,))
    update_balance(listing['seller_id'], listing['price'])
    update_balance(user_id, -listing['price'])
    conn.commit()
    conn.close()
    
    bot.answer_callback_query(call.id, f"✅ Куплен за {listing['price']} тяжек!", show_alert=True)
    bot.edit_message_text(
        f"✅ **ПОД КУПЛЕН!**\n\n"
        f"📟 {listing['pod_name']}\n"
        f"⭐ {listing['rarity']}\n"
        f"💰 Потрачено: {listing['price']} тяжек",
        call.message.chat.id, call.message.message_id,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: m.text == "🏪 РЫНОК")
def market_button(message): market_cmd(message)# ========== АПГРЕЙД ПОДА ==========
@bot.message_handler(commands=['upgrade'])
def upgrade_menu(message):
    user_id = message.from_user.id
    pods = get_user_pods(user_id)
    if not pods:
        bot.reply_to(message, "📦 У вас нет подов для апгрейда!")
        return
    
    kb = InlineKeyboardMarkup(row_width=1)
    for pod in pods[:10]:
        rdata = POD_RARITIES.get(pod['rarity'], {})
        next_rarity = rdata.get('next')
        if next_rarity and rdata.get('upgrade_chance', 0) > 0:
            chance = rdata['upgrade_chance']
            kb.add(InlineKeyboardButton(
                f"{rdata.get('emoji', '📟')} {pod['pod_name']} ({pod['rarity']} → {next_rarity}) - {chance}%",
                callback_data=f"upgrade_select_{pod['id']}"
            ))
    
    if not kb.keyboard:
        bot.reply_to(message, "❌ Нет доступных для апгрейда подов!")
        return
    
    bot.send_message(message.chat.id, "🔧 **ВЫБЕРИТЕ ПОД ДЛЯ АПГРЕЙДА:**", reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('upgrade_select_'))
def upgrade_confirm(call):
    user_id = call.from_user.id
    pod_id = int(call.data.split('_')[2])
    pod = get_pod_by_id(pod_id)
    
    if not pod or pod['user_id'] != str(user_id):
        bot.answer_callback_query(call.id, "❌ Под не найден!", show_alert=True)
        return
    
    rdata = POD_RARITIES.get(pod['rarity'], {})
    next_rarity = rdata.get('next')
    chance = rdata.get('upgrade_chance', 0)
    cost = POD_RARITIES[next_rarity]['price'] // 2 if next_rarity else 0
    
    upgrade_states[user_id] = {'pod_id': pod_id, 'target_rarity': next_rarity, 'chance': chance, 'cost': cost}
    
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ ДА, УЛУЧШИТЬ", callback_data="upgrade_do"),
        InlineKeyboardButton("❌ ОТМЕНА", callback_data="upgrade_cancel")
    )
    
    bot.edit_message_text(
        f"🔧 **ПОДТВЕРДИТЕ АПГРЕЙД**\n\n"
        f"📟 {pod['pod_name']}\n"
        f"⭐ {pod['rarity']} → {next_rarity}\n"
        f"🎲 Шанс успеха: {chance}%\n"
        f"💰 Стоимость: {cost} тяжек\n\n"
        f"❓ Продолжить?",
        call.message.chat.id, call.message.message_id,
        reply_markup=kb, parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data == "upgrade_do")
def upgrade_do(call):
    user_id = call.from_user.id
    state = upgrade_states.get(user_id)
    if not state:
        bot.answer_callback_query(call.id, "❌ Сессия истекла!", show_alert=True)
        return
    
    pod_id = state['pod_id']
    target_rarity = state['target_rarity']
    chance = state['chance']
    cost = state['cost']
    pod = get_pod_by_id(pod_id)
    
    if not pod or pod['user_id'] != str(user_id):
        bot.answer_callback_query(call.id, "❌ Под не найден!", show_alert=True)
        del upgrade_states[user_id]
        return
    
    balance = get_balance(user_id)
    if balance < cost:
        bot.answer_callback_query(call.id, f"❌ Нужно {cost} тяжек!", show_alert=True)
        del upgrade_states[user_id]
        return
    
    update_balance(user_id, -cost)
    success = random.random() * 100 < chance
    
    if success:
        target_data = POD_RARITIES[target_rarity]
        new_pod_name = random.choice(target_data['pods'])
        upgrades = get_user_upgrades(user_id)
        farm_bonus = get_farm_bonus(upgrades['farm_level'])
        new_mining_rate = target_data['mining_rate'] + farm_bonus
        
        conn = get_db()
        conn.execute("UPDATE user_pods SET pod_name = ?, rarity = ?, mining_rate = ? WHERE id = ?",
                     (new_pod_name, target_rarity, new_mining_rate, pod_id))
        conn.commit()
        conn.close()
        
        bot.answer_callback_query(call.id, "✅ АПГРЕЙД УСПЕШЕН!", show_alert=True)
        bot.edit_message_text(
            f"✅ **АПГРЕЙД УСПЕШЕН!**\n\n"
            f"📟 {new_pod_name}\n"
            f"⭐ {target_rarity}\n"
            f"⛏️ {new_mining_rate} тяжек/час\n"
            f"💰 Потрачено: {cost} тяжек",
            call.message.chat.id, call.message.message_id,
            parse_mode='Markdown'
        )
    else:
        bot.answer_callback_query(call.id, f"❌ АПГРЕЙД НЕ УДАЛСЯ! Шанс {chance}%", show_alert=True)
        bot.edit_message_text(
            f"❌ **АПГРЕЙД НЕ УДАЛСЯ!**\n\n"
            f"📟 {pod['pod_name']}\n"
            f"⭐ {pod['rarity']}\n"
            f"🎲 Шанс был: {chance}%\n"
            f"💰 Потеряно: {cost} тяжек",
            call.message.chat.id, call.message.message_id,
            parse_mode='Markdown'
        )
    
    del upgrade_states[user_id]

@bot.callback_query_handler(func=lambda call: call.data == "upgrade_cancel")
def upgrade_cancel(call):
    user_id = call.from_user.id
    if user_id in upgrade_states:
        del upgrade_states[user_id]
    bot.answer_callback_query(call.id, "❌ Апгрейд отменён!", show_alert=True)
    bot.edit_message_text("❌ Апгрейд отменён.", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.text == "🔄 АПГРЕЙД")
def upgrade_button(message): upgrade_menu(message)# ========== МАГАЗИН УЛУЧШЕНИЙ ==========
@bot.message_handler(commands=['shop'])
def shop_command(message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("⏱️ ПЕРЕЗАРЯДКА", callback_data="shop_cooldown"),
        InlineKeyboardButton("🍀 УДАЧА", callback_data="shop_luck"),
        InlineKeyboardButton("🌾 ФЕРМА", callback_data="shop_farm"),
        InlineKeyboardButton("📦 ЛИМИТ", callback_data="shop_limit")
    )
    bot.send_message(message.chat.id, "🏪 **МАГАЗИН УЛУЧШЕНИЙ**\n\nВыберите тип улучшения:", reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('shop_'))
def shop_type(call):
    user_id = call.from_user.id
    upgrade_type = call.data.split('_')[1]
    upgrades = get_user_upgrades(user_id)
    
    upgrade_names = {
        'cooldown': ('⏱️ ПЕРЕЗАРЯДКА', 'cooldown_level', get_cooldown_hours),
        'luck': ('🍀 УДАЧА', 'luck_level', get_luck_bonus),
        'farm': ('🌾 ФЕРМА', 'farm_level', get_farm_bonus),
        'limit': ('📦 ЛИМИТ', 'limit_level', get_limit_bonus)
    }
    
    name, level_key, bonus_func = upgrade_names[upgrade_type]
    current_level = upgrades[level_key]
    
    if current_level >= 10:
        bot.answer_callback_query(call.id, "❌ Максимальный уровень достигнут!", show_alert=True)
        return
    
    next_level = current_level + 1
    cost = UPGRADE_COSTS[upgrade_type][next_level]
    balance = get_balance(user_id)
    
    current_bonus = bonus_func(current_level)
    next_bonus = bonus_func(next_level)
    
    text = f"🏪 **{name}**\n\n"
    text += f"📊 **ТЕКУЩИЙ УРОВЕНЬ:** {current_level}/10\n"
    text += f"✨ **ЭФФЕКТ:** {current_bonus}"
    
    if upgrade_type == 'cooldown':
        text += f"ч перезарядка /daily"
    elif upgrade_type == 'luck':
        text += f"% к шансу редких подов"
    elif upgrade_type == 'farm':
        text += f" тяжек/час к майнингу"
    elif upgrade_type == 'limit':
        text += f" под(а) в /daily"
    
    text += f"\n\n📈 **ПОСЛЕ АПГРЕЙДА:**\n"
    text += f"Уровень: {next_level}/10\n"
    text += f"Эффект: {next_bonus}"
    
    if upgrade_type == 'cooldown':
        text += f"ч перезарядка /daily"
    elif upgrade_type == 'luck':
        text += f"% к шансу редких подов"
    elif upgrade_type == 'farm':
        text += f" тяжек/час к майнингу"
    elif upgrade_type == 'limit':
        text += f" под(а) в /daily"
    
    text += f"\n\n💰 **СТОИМОСТЬ:** {cost} тяжек\n"
    text += f"💎 **ВАШ БАЛАНС:** {balance} тяжек"
    
    kb = InlineKeyboardMarkup()
    if balance >= cost:
        kb.add(InlineKeyboardButton("✅ КУПИТЬ", callback_data=f"shop_buy_{upgrade_type}_{next_level}"))
    kb.add(InlineKeyboardButton("◀️ НАЗАД", callback_data="shop_back"))
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('shop_buy_'))
def shop_buy(call):
    user_id = call.from_user.id
    parts = call.data.split('_')
    upgrade_type = parts[2]
    new_level = int(parts[3])
    
    upgrades = get_user_upgrades(user_id)
    current_level = upgrades[f'{upgrade_type}_level']
    
    if new_level <= current_level:
        bot.answer_callback_query(call.id, "❌ Уровень уже выше!", show_alert=True)
        return
    
    cost = UPGRADE_COSTS[upgrade_type][new_level]
    balance = get_balance(user_id)
    
    if balance < cost:
        bot.answer_callback_query(call.id, f"❌ Нужно {cost} тяжек!", show_alert=True)
        return
    
    update_balance(user_id, -cost)
    
    conn = get_db()
    conn.execute(f"INSERT OR REPLACE INTO user_upgrades (user_id, {upgrade_type}_level) VALUES (?, ?)",
                 (str(user_id), new_level))
    conn.commit()
    conn.close()
    
    upgrade_names = {'cooldown': '⏱️ Перезарядка', 'luck': '🍀 Удача', 'farm': '🌾 Ферма', 'limit': '📦 Лимит'}
    
    bot.answer_callback_query(call.id, f"✅ {upgrade_names[upgrade_type]} улучшена до {new_level} уровня!", show_alert=True)
    shop_type(call)

@bot.callback_query_handler(func=lambda call: call.data == "shop_back")
def shop_back(call):
    shop_command(call.message)

@bot.message_handler(func=lambda m: m.text == "🏪 МАГАЗИН")
def shop_button(message): shop_command(message)# ========== МАКСИМАЛЬНАЯ АДМИН-ПАНЕЛЬ ==========
@bot.message_handler(commands=['admins'])
def show_admin_commands(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ У вас нет доступа к этой команде!")
        return
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("💰 ВЫДАТЬ ТЯЖКИ", callback_data="admin_addmoney"),
        InlineKeyboardButton("💀 ЗАБРАТЬ ТЯЖКИ", callback_data="admin_takemoney"),
        InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="admin_stats"),
        InlineKeyboardButton("👥 ПОЛЬЗОВАТЕЛИ", callback_data="admin_users"),
        InlineKeyboardButton("📢 РАССЫЛКА", callback_data="admin_broadcast"),
        InlineKeyboardButton("📦 ВЫДАТЬ ПОД", callback_data="admin_givepod"),
        InlineKeyboardButton("👑 ДОБАВИТЬ АДМИНА", callback_data="admin_addadmin"),
        InlineKeyboardButton("🗑️ УДАЛИТЬ АДМИНА", callback_data="admin_removeadmin"),
        InlineKeyboardButton("💰 БАЛАНСЫ", callback_data="admin_balances"),
        InlineKeyboardButton("🎮 ВСЕ ИГРЫ", callback_data="admin_games"),
        InlineKeyboardButton("🔄 СБРОС БД", callback_data="admin_reset"),
        InlineKeyboardButton("⚙️ НАСТРОЙКИ", callback_data="admin_settings")
    )
    
    text = """👑 **АДМИН-ПАНЕЛЬ** 👑

Выберите действие:

━━━━━━━━━━━━━━━━━━━━
💰 **УПРАВЛЕНИЕ БАЛАНСОМ**
━━━━━━━━━━━━━━━━━━━━
• Выдать тяжки игроку
• Забрать тяжки у игрока
• Просмотр балансов

━━━━━━━━━━━━━━━━━━━━
📦 **УПРАВЛЕНИЕ ПОДАМИ**
━━━━━━━━━━━━━━━━━━━━
• Выдать случайный под
• Выдать под по редкости

━━━━━━━━━━━━━━━━━━━━
👑 **УПРАВЛЕНИЕ АДМИНАМИ**
━━━━━━━━━━━━━━━━━━━━
• Добавить/удалить админа

━━━━━━━━━━━━━━━━━━━━
📢 **РАССЫЛКА**
━━━━━━━━━━━━━━━━━━━━
• Отправить сообщение всем

━━━━━━━━━━━━━━━━━━━━
⚙️ **ДРУГОЕ**
━━━━━━━━━━━━━━━━━━━━
• Статистика сервера
• Сброс базы данных
• Настройки бота"""
    
    bot.send_message(message.chat.id, text, reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Доступ запрещён!", show_alert=True)
        return
    
    if call.data == "admin_stats":
        conn = get_db()
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_balance = conn.execute("SELECT SUM(balance) FROM users").fetchone()[0] or 0
        total_games = conn.execute("SELECT SUM(games_played) FROM users").fetchone()[0] or 0
        total_pods = conn.execute("SELECT COUNT(*) FROM user_pods").fetchone()[0]
        conn.close()
        
        text = f"📊 **СТАТИСТИКА**\n\n"
        text += f"👥 Игроков: {total_users}\n"
        text += f"💰 Общий баланс: {total_balance:,} тяжек\n"
        text += f"🎮 Всего игр: {total_games}\n"
        text += f"📦 Всего подов: {total_pods}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    
    elif call.data == "admin_users":
        conn = get_db()
        users = conn.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10").fetchall()
        conn.close()
        text = "👥 **ТОП-10 ИГРОКОВ**\n\n"
        for i, u in enumerate(users, 1):
            text += f"{i}. @{u['username'] or 'Игрок'} — {u['balance']:,} тяжек\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    
    elif call.data == "admin_balances":
        conn = get_db()
        total = conn.execute("SELECT SUM(balance) FROM users").fetchone()[0] or 0
        avg = conn.execute("SELECT AVG(balance) FROM users").fetchone()[0] or 0
        mini = conn.execute("SELECT MIN(balance) FROM users").fetchone()[0] or 0
        maxi = conn.execute("SELECT MAX(balance) FROM users").fetchone()[0] or 0
        conn.close()
        text = f"💰 **СТАТИСТИКА БАЛАНСОВ**\n\n"
        text += f"💵 Общий: {total:,} тяжек\n"
        text += f"📊 Средний: {avg:,.0f} тяжек\n"
        text += f"📉 Минимальный: {mini:,} тяжек\n"
        text += f"📈 Максимальный: {maxi:,} тяжек"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    
    elif call.data == "admin_addmoney":
        msg = bot.send_message(call.message.chat.id, "💰 Введите: @username сумма")
        bot.register_next_step_handler(msg, process_addmoney)
    
    elif call.data == "admin_takemoney":
        msg = bot.send_message(call.message.chat.id, "💀 Введите: @username сумма")
        bot.register_next_step_handler(msg, process_takemoney)
    
    elif call.data == "admin_givepod":
        msg = bot.send_message(call.message.chat.id, "📦 Введите: @username")
        bot.register_next_step_handler(msg, process_givepod)
    
    elif call.data == "admin_addadmin":
        msg = bot.send_message(call.message.chat.id, "👑 Введите: @username")
        bot.register_next_step_handler(msg, process_addadmin)
    
    elif call.data == "admin_removeadmin":
        msg = bot.send_message(call.message.chat.id, "🗑️ Введите: @username")
        bot.register_next_step_handler(msg, process_removeadmin)
    
    elif call.data == "admin_broadcast":
        msg = bot.send_message(call.message.chat.id, "📢 Введите текст рассылки:")
        bot.register_next_step_handler(msg, process_broadcast)
    
    elif call.data == "admin_back":
        show_admin_commands(call.message)

def process_addmoney(message):
    if not is_admin(message.from_user.id): return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ Формат: @username сумма")
            return
        user_input = parts[0]
        amount = int(parts[1])
        
        if user_input.startswith('@'):
            conn = get_db()
            user = conn.execute("SELECT telegram_id FROM users WHERE username LIKE ?", (f'%{user_input[1:]}%',)).fetchone()
            conn.close()
            if not user:
                bot.reply_to(message, "❌ Пользователь не найден!")
                return
            tg_id = user['telegram_id']
        else:
            tg_id = user_input
        
        new_balance = update_balance(tg_id, amount)
        bot.reply_to(message, f"✅ Выдано {amount:,} тяжек\n💰 Новый баланс: {new_balance:,}")
        try:
            bot.send_message(int(tg_id), f"🎉 АДМИН ВЫДАЛ ВАМ {amount:,} тяжек!\n💰 Новый баланс: {new_balance:,}")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Ошибка!")

def process_takemoney(message):
    if not is_admin(message.from_user.id): return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ Формат: @username сумма")
            return
        user_input = parts[0]
        amount = int(parts[1])
        
        if user_input.startswith('@'):
            conn = get_db()
            user = conn.execute("SELECT telegram_id FROM users WHERE username LIKE ?", (f'%{user_input[1:]}%',)).fetchone()
            conn.close()
            if not user:
                bot.reply_to(message, "❌ Пользователь не найден!")
                return
            tg_id = user['telegram_id']
        else:
            tg_id = user_input
        
        current = get_balance(tg_id)
        if current < amount:
            bot.reply_to(message, f"❌ У игрока только {current} тяжек!")
            return
        
        new_balance = update_balance(tg_id, -amount)
        bot.reply_to(message, f"✅ Снято {amount:,} тяжек\n💰 Новый баланс: {new_balance:,}")
        try:
            bot.send_message(int(tg_id), f"⚠️ АДМИН СНЯЛ {amount:,} тяжек!\n💰 Новый баланс: {new_balance:,}")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Ошибка!")

def process_givepod(message):
    if not is_admin(message.from_user.id): return
    try:
        user_input = message.text.strip()
        if user_input.startswith('@'):
            conn = get_db()
            user = conn.execute("SELECT telegram_id FROM users WHERE username LIKE ?", (f'%{user_input[1:]}%',)).fetchone()
            conn.close()
            if not user:
                bot.reply_to(message, "❌ Пользователь не найден!")
                return
            tg_id = user['telegram_id']
        else:
            tg_id = user_input
        
        pod = get_random_pod()
        add_pod_to_user(tg_id, pod['name'], pod['rarity'], pod['mining_rate'])
        bot.reply_to(message, f"✅ Выдан под {pod['name']} ({pod['rarity']})")
        try:
            bot.send_message(int(tg_id), f"🎁 АДМИН ВЫДАЛ ВАМ ПОД!\n📟 {pod['name']}\n⭐ {pod['rarity']}")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Ошибка!")

def process_addadmin(message):
    if not is_admin(message.from_user.id): return
    try:
        user_input = message.text.strip()
        if user_input.startswith('@'):
            conn = get_db()
            user = conn.execute("SELECT telegram_id FROM users WHERE username LIKE ?", (f'%{user_input[1:]}%',)).fetchone()
            conn.close()
            if not user:
                bot.reply_to(message, "❌ Пользователь не найден!")
                return
            tg_id = user['telegram_id']
        else:
            tg_id = user_input
        
        make_admin(tg_id)
        bot.reply_to(message, f"✅ Админ добавлен!")
        try:
            bot.send_message(int(tg_id), f"👑 ВАМ ВЫДАНЫ ПРАВА АДМИНИСТРАТОРА!")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Ошибка!")

def process_removeadmin(message):
    if not is_admin(message.from_user.id): return
    try:
        user_input = message.text.strip()
        if user_input.startswith('@'):
            conn = get_db()
            user = conn.execute("SELECT telegram_id FROM users WHERE username LIKE ?", (f'%{user_input[1:]}%',)).fetchone()
            conn.close()
            if not user:
                bot.reply_to(message, "❌ Пользователь не найден!")
                return
            tg_id = user['telegram_id']
        else:
            tg_id = user_input
        
        conn = get_db()
        conn.execute("UPDATE users SET is_admin = 0 WHERE telegram_id = ?", (str(tg_id),))
        conn.commit()
        conn.close()
        bot.reply_to(message, f"✅ Админ удалён!")
        try:
            bot.send_message(int(tg_id), f"⚠️ ВАС ЛИШИЛИ ПРАВ АДМИНИСТРАТОРА!")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Ошибка!")

def process_broadcast(message):
    if not is_admin(message.from_user.id): return
    conn = get_db()
    users = conn.execute("SELECT telegram_id FROM users").fetchall()
    conn.close()
    
    success = 0
    for user in users:
        try:
            bot.send_message(user['telegram_id'], f"📢 **АНОНС**\n\n{message.text}", parse_mode='Markdown')
            success += 1
            time.sleep(0.05)
        except:
            pass
    
    bot.reply_to(message, f"✅ Рассылка завершена! Доставлено: {success}")

@bot.message_handler(func=lambda m: m.text == "👑 АДМИНЫ")
def admins_button(message): show_admin_commands(message)# ========== ВЕБ-КАЗИНО ==========
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

WEB_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Бурмалдатое Casino</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: radial-gradient(ellipse at 20% 30%, #0a0f1e, #05080f); font-family: 'Segoe UI', sans-serif; padding: 16px; color: white; }
        .container { max-width: 480px; margin: 0 auto; background: rgba(8,12,25,0.85); backdrop-filter: blur(15px); border: 1px solid rgba(255,215,0,0.3); border-radius: 28px; overflow: hidden; }
        .header { background: linear-gradient(135deg, #1a1f2e, #0d1225); padding: 20px; text-align: center; border-bottom: 2px solid #ffd700; }
        .title { font-size: 22px; font-weight: bold; background: linear-gradient(45deg, #ffd700, #ff6b6b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .balance-box { background: rgba(0,0,0,0.5); border-radius: 20px; padding: 12px; margin-top: 12px; }
        .balance-amount { font-size: 36px; font-weight: bold; color: #ffd700; }
        .game-nav { display: grid; grid-template-columns: repeat(4,1fr); gap: 5px; padding: 15px; background: rgba(0,0,0,0.3); }
        .game-btn { background: rgba(255,255,255,0.08); border: none; padding: 12px 5px; border-radius: 16px; color: #aaa; font-size: 12px; cursor: pointer; text-align: center; }
        .game-btn.active { background: linear-gradient(135deg, #ffd700, #ff8c00); color: #000; }
        .game-area { padding: 20px; min-height: 480px; }
        .crash-multiplier { font-size: 64px; text-align: center; color: #ffd700; margin: 20px 0; }
        .bet-input { width: 100%; background: rgba(0,0,0,0.5); border: 1px solid #ffd700; padding: 14px; border-radius: 16px; color: white; font-size: 18px; text-align: center; margin-bottom: 12px; }
        .bet-presets { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 16px; }
        .preset-btn { background: rgba(255,255,255,0.08); border: none; padding: 10px; border-radius: 12px; color: #ffd700; cursor: pointer; }
        .action-btn { width: 100%; background: linear-gradient(135deg, #ffd700, #ff8c00); border: none; padding: 16px; border-radius: 20px; font-size: 18px; font-weight: bold; color: #000; cursor: pointer; }
        .auto-cash-row { display: flex; align-items: center; justify-content: space-between; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 16px; margin-bottom: 16px; }
        .auto-cash-input { background: rgba(0,0,0,0.5); border: 1px solid #ffd700; padding: 8px; color: #ffd700; width: 80px; text-align: center; }
        .slots-reels { display: flex; justify-content: center; gap: 15px; margin: 30px 0; }
        .slot-reel { width: 85px; height: 85px; background: rgba(0,0,0,0.6); border-radius: 18px; display: flex; align-items: center; justify-content: center; font-size: 52px; border: 2px solid #ffd700; }
        .roulette-wheel { position: relative; width: 280px; height: 280px; margin: 0 auto; }
        .roulette-canvas { width: 100%; height: 100%; border-radius: 50%; }
        .roulette-bets { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin: 20px 0; }
        .bet-option { background: rgba(0,0,0,0.5); border: 1px solid #ffd700; padding: 12px; border-radius: 16px; cursor: pointer; text-align: center; }
        .bet-option.selected { background: #ffd700; color: #000; }
        .numbers-grid { display: grid; grid-template-columns: repeat(7,1fr); gap: 8px; margin: 20px 0; max-height: 180px; overflow-y: auto; }
        .num-btn { background: rgba(255,255,255,0.08); border: none; padding: 12px; border-radius: 12px; color: white; cursor: pointer; text-align: center; }
        .num-btn.selected { background: #ffd700; color: #000; }
        .mines-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 10px; margin: 20px 0; }
        .mine-cell { aspect-ratio: 1; background: rgba(255,255,255,0.08); border: 1px solid #ffd700; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 24px; cursor: pointer; }
        .mine-cell.revealed { background: #2ed57333; border-color: #2ed573; }
        .mine-cell.mine { background: #ff475733; border-color: #ff4757; }
        .bet-status { text-align: center; margin-top: 12px; font-size: 12px; color: #aaa; }
        .history-section { padding: 15px; border-top: 1px solid rgba(255,215,0,0.2); max-height: 160px; overflow-y: auto; }
        .history-item { background: rgba(255,255,255,0.04); padding: 8px; margin: 4px 0; font-size: 11px; display: flex; justify-content: space-between; }
        .win-text { color: #4caf50; }
        .lose-text { color: #ff4757; }
        @media (max-width:480px){ .slot-reel{ width:65px; height:65px; font-size:40px; } .crash-multiplier{ font-size:48px; } }
    </style>
</head>
<body>
<div class="container">
    <div class="header"><div class="title">🐐 БУРМАЛДАТОЕ CASINO 🐐</div><div class="balance-box"><div>ТЯЖКИ:</div><div class="balance-amount" id="balance">0</div></div></div>
    <div class="game-nav"><button class="game-btn active" data-game="crash">💥 КРАШ</button><button class="game-btn" data-game="slots">🎰 СЛОТЫ</button><button class="game-btn" data-game="roulette">🎡 РУЛЕТКА</button><button class="game-btn" data-game="mines">💣 МИНЫ</button></div>
    <div class="game-area" id="gameArea">
        <div id="crashGame"><div class="crash-multiplier" id="currentMult">1.00x</div><div class="bet-section"><input type="number" id="betAmount" class="bet-input" placeholder="СТАВКА" value="100"><div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div><div class="auto-cash-row"><span>🤖 АВТО-ВЫВОД (x):</span><input type="number" id="autoCash" class="auto-cash-input" value="2.00" step="0.5"></div><button class="action-btn" id="placeBetBtn">💰 СДЕЛАТЬ СТАВКУ</button><button class="action-btn" id="cashoutBtn" style="display:none">✅ ЗАБРАТЬ</button><div class="bet-status" id="betStatus"></div></div></div>
        <div id="slotsGame" style="display:none"><div class="slots-reels"><div class="slot-reel" id="slot1">🍒</div><div class="slot-reel" id="slot2">🍋</div><div class="slot-reel" id="slot3">🍊</div></div><div class="bet-section"><input type="number" id="slotsBet" class="bet-input" placeholder="СТАВКА" value="100"><div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div><button class="action-btn" id="slotsSpinBtn">🎰 КРУТИТЬ</button></div></div>
        <div id="rouletteGame" style="display:none"><div class="roulette-wheel"><canvas id="wheelCanvas" width="280" height="280" class="roulette-canvas"></canvas></div><div class="roulette-bets"><div class="bet-option red" data-bet="red">🔴 КРАСНОЕ (x2)</div><div class="bet-option black" data-bet="black">⚫ ЧЁРНОЕ (x2)</div><div class="bet-option green" data-bet="green">🟢 ЗЕЛЁНОЕ (x36)</div></div><div class="numbers-grid" id="rouletteNumbers"></div><div class="bet-section"><input type="number" id="rouletteBet" class="bet-input" placeholder="СТАВКА" value="100"><div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div><button class="action-btn" id="rouletteSpinBtn">🎡 КРУТИТЬ</button></div></div>
        <div id="minesGame" style="display:none"><div class="mines-grid" id="minesGrid"></div><div class="bet-section"><input type="number" id="minesBet" class="bet-input" placeholder="СТАВКА" value="100"><div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div><button class="action-btn" id="minesNewGameBtn">🎲 НОВАЯ ИГРА</button><button class="action-btn" id="minesCashoutBtn" style="display:none">💰 ЗАБРАТЬ</button><div class="bet-status" id="minesStatus"></div></div></div>
    </div>
    <div class="history-section"><div class="history-title">📜 ИСТОРИЯ ИГР</div><div id="historyList"></div></div>
</div>
<script>
    const urlParams = new URLSearchParams(window.location.search);
    let tgId = urlParams.get('tg_id');
    let balance = 0, myBet = 0, myAutoCash = 2.00, hasBet = false, hasCashedOut = false;
    let currentMult = 1.00, gameState = 'betting', timerSec = 10, crashHistory = [];
    let isSpinning = false, selectedRouletteBet = null;
    let minesGame = { active: false, bet: 0, mines: [], revealed: [], multiplier: 1.0 };
    const symbols = ['🍒','🍋','🍊','🔔','💎','7️⃣'];
    const symbolMultipliers = {'🍒':2,'🍋':3,'🍊':5,'🔔':7,'💎':10,'7️⃣':20};
    const redNumbers = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36];
    const blackNumbers = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35];
    
    setInterval(()=>{document.querySelectorAll(".multiplier-item").forEach(el=>{el.innerText=(Math.random()*3+0.5).toFixed(2)+"x";});},4000);
    
    let wheelCanvas, wheelCtx;
    function drawWheel() {
        if(!wheelCanvas){wheelCanvas=document.getElementById('wheelCanvas');if(!wheelCanvas)return;wheelCtx=wheelCanvas.getContext('2d');}
        wheelCanvas.width=280;wheelCanvas.height=280;
        let anglePer=(Math.PI*2)/37;
        wheelCtx.clearRect(0,0,280,280);
        for(let i=0;i<=36;i++){
            let start=i*anglePer,end=start+anglePer,color;
            if(i===0)color='#2ed573';
            else if(redNumbers.includes(i))color='#ff4757';
            else color='#1a1f2e';
            wheelCtx.beginPath();wheelCtx.arc(140,140,130,start,end);wheelCtx.lineTo(140,140);
            wheelCtx.fillStyle=color;wheelCtx.fill();
            wheelCtx.save();wheelCtx.translate(140,140);wheelCtx.rotate(start+anglePer/2);
            wheelCtx.fillStyle='white';wheelCtx.font='bold 10px Arial';wheelCtx.fillText(i,48,6);
            wheelCtx.restore();
        }
    }
    
    async function loadBalance(){
        if(!tgId)return;let res=await fetch('/api/balance',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId})});let data=await res.json();balance=data.balance;document.getElementById('balance').innerText=balance.toLocaleString();
    }
    async function updateBalance(amount){
        if(!tgId)return;let res=await fetch('/api/update_balance',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId,amount:amount})});let data=await res.json();balance=data.balance;document.getElementById('balance').innerText=balance.toLocaleString();return balance;
    }
    
    async function fetchState(){
        let res=await fetch('/api/crash_state');let data=await res.json();
        currentMult=data.multiplier;gameState=data.state;timerSec=data.timer;crashHistory=data.history;
        document.getElementById('currentMult').innerHTML=currentMult.toFixed(2)+'x';
        let placeBtn=document.getElementById('placeBetBtn'),cashBtn=document.getElementById('cashoutBtn');
        if(gameState=='betting'){if(!hasBet){placeBtn.style.display='block';cashBtn.style.display='none';}}
        else if(gameState=='flying'){if(hasBet&&!hasCashedOut&&myAutoCash>0&&currentMult>=myAutoCash)await cashout();if(hasBet&&!hasCashedOut){placeBtn.style.display='none';cashBtn.style.display='block';}else{placeBtn.style.display='block';cashBtn.style.display='none';}}
        else{placeBtn.style.display='block';cashBtn.style.display='none';}
    }
    async function placeBet(){
        if(!tgId){alert('Привяжите Telegram!');return;}
        if(hasBet){alert('У вас уже есть ставка!');return;}
        if(gameState!='betting'){alert('Ставки только между раундами!');return;}
        let bet=parseInt(document.getElementById('betAmount').value);
        if(bet<100||bet>balance){alert('Мин. ставка 100 тяжек!');return;}
        let autoVal=parseFloat(document.getElementById('autoCash').value);if(autoVal<1.01)autoVal=0;
        let res=await fetch('/api/place_crash_bet',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId,bet:bet,auto_cash:autoVal})});
        let data=await res.json();
        if(data.success){await updateBalance(-bet);myBet=bet;myAutoCash=autoVal;hasBet=true;hasCashedOut=false;document.getElementById('placeBetBtn').style.display='none';}
        else alert(data.message);
    }
    async function cashout(){
        if(!hasBet||hasCashedOut){alert('Нет ставки!');return;}
        if(gameState!='flying'){alert('Вывод только во время полёта!');return;}
        let res=await fetch('/api/crash_cashout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId})});
        let data=await res.json();
        if(data.success){await updateBalance(data.win_amount);hasCashedOut=true;document.getElementById('placeBetBtn').style.display='block';document.getElementById('cashoutBtn').style.display='none';addHistory('КРАШ',myBet,data.win_amount-myBet,`${data.multiplier.toFixed(2)}x`);myBet=0;hasBet=false;}
        else alert(data.message);
    }
    async function checkCrash(){
        if(!hasBet||hasCashedOut)return;
        let res=await fetch('/api/check_crash_result',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId})});
        let data=await res.json();
        if(data.crashed){document.getElementById('betStatus').innerHTML=`💀 КРАШ! -${myBet} тяжек`;document.getElementById('placeBetBtn').style.display='block';document.getElementById('cashoutBtn').style.display='none';addHistory('КРАШ',myBet,-myBet,`Краш ${data.crash_point.toFixed(2)}x`);myBet=0;hasBet=false;hasCashedOut=false;}
    }
    
    async function spinSlots(){
        if(isSpinning)return;
        let bet=parseInt(document.getElementById('slotsBet').value);
        if(bet<100||bet>balance){alert('Мин. ставка 100 тяжек!');return;}
        isSpinning=true;
        await updateBalance(-bet);
        for(let i=0;i<15;i++){setTimeout(()=>{if(i<12){document.getElementById('slot1').innerText=symbols[Math.floor(Math.random()*symbols.length)];document.getElementById('slot2').innerText=symbols[Math.floor(Math.random()*symbols.length)];document.getElementById('slot3').innerText=symbols[Math.floor(Math.random()*symbols.length)];}},i*80);}
        setTimeout(async()=>{let r1=symbols[Math.floor(Math.random()*symbols.length)];let r2=symbols[Math.floor(Math.random()*symbols.length)];let r3=symbols[Math.floor(Math.random()*symbols.length)];document.getElementById('slot1').innerText=r1;document.getElementById('slot2').innerText=r2;document.getElementById('slot3').innerText=r3;let win=0;if(r1==r2&&r2==r3){win=bet*symbolMultipliers[r1];}else if(r1==r2||r2==r3||r1==r3){win=bet*2;}if(win>0){await updateBalance(win);addHistory('СЛОТЫ',bet,win-bet,`${r1}${r2}${r3}`);alert('🏆 ПОБЕДА! +'+win.toLocaleString()+' тяжек');}else{addHistory('СЛОТЫ',bet,-bet,`${r1}${r2}${r3}`);alert('❌ ПРОИГРЫШ! -'+bet.toLocaleString()+' тяжек');}isSpinning=false;},1400);
    }
    
    function initRoulette(){
        let grid=document.getElementById('rouletteNumbers');
        grid.innerHTML='';
        for(let i=0;i<=36;i++){
            let btn=document.createElement('button');btn.className='num-btn';btn.innerText=i;
            btn.onclick=(function(num){return function(){document.querySelectorAll('.num-btn').forEach(b=>b.classList.remove('selected'));document.querySelectorAll('.bet-option').forEach(b=>b.classList.remove('selected'));btn.classList.add('selected');selectedRouletteBet='number';window.selectedNumber=num;};})(i);
            grid.appendChild(btn);
        }
        document.querySelectorAll('.bet-option').forEach(btn=>{
            btn.onclick=function(){document.querySelectorAll('.bet-option').forEach(b=>b.classList.remove('selected'));document.querySelectorAll('.num-btn').forEach(b=>b.classList.remove('selected'));this.classList.add('selected');selectedRouletteBet=this.dataset.bet;window.selectedNumber=null;};
        });
    }
    async function spinRoulette(){
        if(!selectedRouletteBet&&window.selectedNumber===null){alert('Выберите ставку!');return;}
        let bet=parseInt(document.getElementById('rouletteBet').value);
        if(bet<100||bet>balance){alert('Мин. ставка 100 тяжек!');return;}
        await updateBalance(-bet);
        let result=Math.floor(Math.random()*37);
        let win=0,winText='';
        if(selectedRouletteBet=='red'&&redNumbers.includes(result)){win=bet*2;winText='Красное';}
        else if(selectedRouletteBet=='black'&&blackNumbers.includes(result)){win=bet*2;winText='Чёрное';}
        else if(selectedRouletteBet=='green'&&result===0){win=bet*36;winText='Зелёное';}
        else if(selectedRouletteBet=='number'&&window.selectedNumber===result){win=bet*36;winText=`Число ${result}`;}
        if(win>0){await updateBalance(win);addHistory('РУЛЕТКА',bet,win-bet,winText);alert('🎉 ПОБЕДА! +'+win.toLocaleString()+' тяжек');}
        else{addHistory('РУЛЕТКА',bet,-bet,`Выпало ${result}`);alert('❌ ПРОИГРЫШ! -'+bet.toLocaleString()+' тяжек');}
        drawWheel();
    }
    
    function initMines(){
        let grid=document.getElementById('minesGrid');
        grid.innerHTML='';
        for(let i=0;i<25;i++){
            let cell=document.createElement('div');cell.className='mine-cell';cell.dataset.index=i;cell.innerHTML='?';cell.onclick=()=>revealMine(i);
            grid.appendChild(cell);
        }
        minesGame.active=false;
    }
    async function startMines(){
        let bet=parseInt(document.getElementById('minesBet').value);
        if(bet<100||bet>balance){alert('Мин. ставка 100 тяжек!');return;}
        let res=await fetch('/api/mines_start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId,bet:bet})});
        let data=await res.json();
        if(data.success){
            await updateBalance(-bet);
            minesGame={active:true,bet:bet,mines:data.mines,revealed:[],multiplier:1.0};
            drawMinesGrid();
            document.getElementById('minesNewGameBtn').style.display='none';
            document.getElementById('minesCashoutBtn').style.display='block';
            document.getElementById('minesStatus').innerHTML=`💰 Ставка: ${bet} | Множитель: 1.00x`;
        }else alert(data.message);
    }
    function drawMinesGrid(){
        let grid=document.getElementById('minesGrid');
        grid.innerHTML='';
        for(let i=0;i<25;i++){
            let cell=document.createElement('div');cell.className='mine-cell';cell.dataset.index=i;
            if(minesGame.revealed.includes(i)){cell.innerHTML='💎';cell.classList.add('revealed');}
            else cell.innerHTML='?';
            cell.onclick=()=>revealMine(i);
            grid.appendChild(cell);
        }
    }
    async function revealMine(index){
        if(!minesGame.active||minesGame.revealed.includes(index))return;
        if(minesGame.mines[index]){
            document.querySelector(`.mine-cell[data-index='${index}']`).innerHTML='💣';document.querySelector(`.mine-cell[data-index='${index}']`).classList.add('mine');
            addHistory('МИНЫ',minesGame.bet,-minesGame.bet,'Попалась мина!');
            document.getElementById('minesNewGameBtn').style.display='block';
            document.getElementById('minesCashoutBtn').style.display='none';
            minesGame.active=false;
            return;
        }
        let res=await fetch('/api/mines_reveal',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId,position:index,mines:minesGame.mines,bet:minesGame.bet,revealed:minesGame.revealed})});
        let data=await res.json();
        if(data.success){
            minesGame.revealed=data.revealed;
            minesGame.multiplier=data.multiplier;
            drawMinesGrid();
            document.getElementById('minesStatus').innerHTML=`💰 Ставка: ${minesGame.bet} | Множитель: ${data.multiplier.toFixed(2)}x | Потенциальный выигрыш: ${data.win_amount}`;
            window.currentWinAmount=data.win_amount;
            if(minesGame.revealed.length===20) await cashoutMines();
        }
    }
    async function cashoutMines(){
        if(!minesGame.active)return;
        let winAmount=Math.floor(minesGame.bet*minesGame.multiplier);
        let res=await fetch('/api/mines_cashout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId,win_amount:winAmount})});
        if(res.ok){
            await updateBalance(winAmount);
            addHistory('МИНЫ',minesGame.bet,winAmount-minesGame.bet,`Победа! Множитель ${minesGame.multiplier.toFixed(2)}x`);
            alert('🏆 ПОБЕДА! +'+winAmount.toLocaleString()+' тяжек');
            minesGame.active=false;
            document.getElementById('minesNewGameBtn').style.display='block';
            document.getElementById('minesCashoutBtn').style.display='none';
            drawMinesGrid();
        }
    }
    
    function addHistory(game,bet,win,result){
        let hist=document.getElementById('historyList');
        let item=document.createElement('div');
        item.className='history-item';
        item.innerHTML=`<span>${game}</span><span>${bet.toLocaleString()}</span><span class="${win>0?'win-text':'lose-text'}">${win>0?'+'+win.toLocaleString():win}</span><span>${result}</span>`;
        hist.insertBefore(item,hist.firstChild);
        if(hist.children.length>15)hist.removeChild(hist.lastChild);
    }
    
    function setMaxBet(){
        if(balance>0){
            if(document.getElementById('betAmount').offsetParent)document.getElementById('betAmount').value=balance;
            if(document.getElementById('slotsBet').offsetParent)document.getElementById('slotsBet').value=balance;
            if(document.getElementById('rouletteBet').offsetParent)document.getElementById('rouletteBet').value=balance;
            if(document.getElementById('minesBet').offsetParent)document.getElementById('minesBet').value=balance;
        }
    }
    
    function switchGame(game){
        document.getElementById('crashGame').style.display=game=='crash'?'block':'none';
        document.getElementById('slotsGame').style.display=game=='slots'?'block':'none';
        document.getElementById('rouletteGame').style.display=game=='roulette'?'block':'none';
        document.getElementById('minesGame').style.display=game=='mines'?'block':'none';
        if(game=='roulette')drawWheel();
        if(game=='mines')initMines();
    }
    
    document.querySelectorAll('.game-btn').forEach(btn=>{btn.addEventListener('click',()=>{document.querySelectorAll('.game-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');switchGame(btn.dataset.game);});});
    document.querySelectorAll('.preset-btn').forEach(btn=>{btn.addEventListener('click',()=>{let bet=btn.dataset.bet;if(bet==='max'){setMaxBet();}else{if(document.getElementById('betAmount').offsetParent)document.getElementById('betAmount').value=bet;if(document.getElementById('slotsBet').offsetParent)document.getElementById('slotsBet').value=bet;if(document.getElementById('rouletteBet').offsetParent)document.getElementById('rouletteBet').value=bet;if(document.getElementById('minesBet').offsetParent)document.getElementById('minesBet').value=bet;}});});
    document.getElementById('placeBetBtn').onclick=placeBet;
    document.getElementById('cashoutBtn').onclick=cashout;
    document.getElementById('slotsSpinBtn').onclick=spinSlots;
    document.getElementById('rouletteSpinBtn').onclick=spinRoulette;
    document.getElementById('minesNewGameBtn').onclick=startMines;
    document.getElementById('minesCashoutBtn').onclick=cashoutMines;
    
    setInterval(fetchState,300);
    setInterval(checkCrash,500);
    if(tgId)loadBalance();
    initRoulette();
    drawWheel();
    initMines();
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return WEB_HTML

# ========== API ДЛЯ ВЕБ-КАЗИНО ==========
@app.route('/api/balance', methods=['POST'])
def api_balance():
    data = request.json
    tg_id = data.get('telegram_id')
    return jsonify({'balance': get_balance(tg_id) if tg_id else START_BALANCE})

@app.route('/api/update_balance', methods=['POST'])
def api_update_balance():
    data = request.json
    tg_id = data.get('telegram_id')
    amount = data.get('amount', 0)
    return jsonify({'balance': update_balance(tg_id, amount) if tg_id else START_BALANCE})

@app.route('/api/crash_state', methods=['GET'])
def crash_state():
    timer = 0
    if game_state == 'betting': timer = betting_timer
    return jsonify({'multiplier': current_multiplier, 'state': game_state, 'timer': timer, 'history': crash_history[:10]})

@app.route('/api/place_crash_bet', methods=['POST'])
def place_crash_bet():
    global user_bets, game_state
    data = request.json
    tg_id = data.get('telegram_id')
    bet = data.get('bet', 0)
    auto_cash = data.get('auto_cash', 0)
    if game_state != 'betting': return jsonify({'success': False, 'message': 'Ставки только между раундами!'})
    if tg_id in user_bets: return jsonify({'success': False, 'message': 'У вас уже есть ставка!'})
    if get_balance(tg_id) < bet: return jsonify({'success': False, 'message': 'Недостаточно тяжек!'})
    user_bets[tg_id] = {'bet': bet, 'cashed_out': False, 'auto_cash': auto_cash}
    return jsonify({'success': True})

@app.route('/api/crash_cashout', methods=['POST'])
def crash_cashout():
    global user_bets, current_multiplier, game_state
    data = request.json
    tg_id = data.get('telegram_id')
    if tg_id not in user_bets or user_bets[tg_id]['cashed_out'] or game_state != 'flying':
        return jsonify({'success': False, 'message': 'Нельзя забрать!'})
    win_amount = int(user_bets[tg_id]['bet'] * current_multiplier)
    user_bets[tg_id]['cashed_out'] = True
    update_balance(tg_id, win_amount)
    return jsonify({'success': True, 'win_amount': win_amount, 'multiplier': current_multiplier})

@app.route('/api/check_crash_result', methods=['POST'])
def check_crash_result():
    global user_bets, game_state, crash_point
    data = request.json
    tg_id = data.get('telegram_id')
    if game_state == 'crashed' and tg_id in user_bets and not user_bets[tg_id]['cashed_out']:
        del user_bets[tg_id]
        return jsonify({'crashed': True, 'crash_point': crash_point})
    return jsonify({'crashed': False})

@app.route('/api/mines_start', methods=['POST'])
def mines_start():
    data = request.json
    tg_id = data.get('telegram_id')
    bet = data.get('bet', 0)
    if get_balance(tg_id) < bet:
        return jsonify({'success': False, 'message': 'Недостаточно тяжек!'})
    update_balance(tg_id, -bet)
    mines = [False] * 25
    for pos in random.sample(range(25), 5):
        mines[pos] = True
    return jsonify({'success': True, 'mines': mines, 'bet': bet})

@app.route('/api/mines_reveal', methods=['POST'])
def mines_reveal():
    data = request.json
    tg_id = data.get('telegram_id')
    position = data.get('position')
    mines = data.get('mines')
    bet = data.get('bet')
    revealed = data.get('revealed', [])
    if mines[position]:
        return jsonify({'success': False, 'is_mine': True})
    revealed.append(position)
    multiplier = 1 + (len(revealed) / 20) * 3
    win_amount = int(bet * multiplier)
    return jsonify({'success': True, 'is_mine': False, 'revealed': revealed, 'multiplier': multiplier, 'win_amount': win_amount})

@app.route('/api/mines_cashout', methods=['POST'])
def mines_cashout():
    data = request.json
    tg_id = data.get('telegram_id')
    win_amount = data.get('win_amount')
    update_balance(tg_id, win_amount)
    update_stats(tg_id, 0, win_amount)
    return jsonify({'success': True})

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("="*50)
    print("🐐 БУРМАЛДАТОЕ CASINO")
    print("="*50)
    print(f"🤖 Бот запущен")
    print(f"🌐 Веб-казино: {WEB_URL}")
    print(f"💰 Стартовый баланс: {START_BALANCE} тяжек")
    print(f"🎲 Минимальная ставка: {MIN_BET} тяжек")
    print("="*50)
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=WEB_PORT)
