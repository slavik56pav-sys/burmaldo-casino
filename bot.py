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

# ========== ВАЛЮТА ==========
# ВСЕГДА ТОЛЬКО ТЯЖКИ (единая валюта)# ========== ВСЕ ПОДЫ VOOPOO (200+ штук) ==========

XSLIM_PODS = [
    "XSLIM Pro", "XSLIM Nano", "XSLIM Air", "XSLIM Ultra", "XSLIM Max",
    "XSLIM Mini", "XSLIM Edge", "XSLIM Plus", "XSLIM Lite", "XSLIM Flex",
    "XSLIM Twist", "XSLIM Curve", "XSLIM Flat", "XSLIM Round", "XSLIM Square",
    "XSLIM 2.0", "XSLIM 3.0", "XSLIM X", "XSLIM S", "XSLIM R",
    "XSLIM Pro Max", "XSLIM Ultra Lite", "XSLIM Air Plus", "XSLIM Nano Pro", "XSLIM Flex Edge",
    "XSLIM Twist Pro", "XSLIM Curve Max", "XSLIM Flat Ultra", "XSLIM Round Plus", "XSLIM Square Pro"
]

VINCI_PODS = [
    "VINCI", "VINCI X", "VINCI Royal", "VINCI Spark", "VINCI Q",
    "VINCI Pod", "VINCI 2", "VINCI 3", "VINCI Pro", "VINCI Max",
    "VINCI Air", "VINCI Nano", "VINCI Ultra", "VINCI Flex", "VINCI Twist",
    "VINCI Edge", "VINCI Plus", "VINCI Lite", "VINCI X Pro", "VINCI X Max",
    "VINCI Royal Pro", "VINCI Spark Pro", "VINCI Q Max", "VINCI Pod 2", "VINCI 2 Pro",
    "VINCI 3 Max", "VINCI Pro Max", "VINCI Air Plus", "VINCI Nano Pro", "VINCI Ultra Max"
]

ARGUS_PODS = [
    "ARGUS GT", "ARGUS XT", "ARGUS Air", "ARGUS Pod", "ARGUS Pro",
    "ARGUS 2", "ARGUS 3", "ARGUS Max", "ARGUS Ultra", "ARGUS Flex",
    "ARGUS G", "ARGUS P", "ARGUS M", "ARGUS Z", "ARGUS MT",
    "ARGUS GT 2", "ARGUS XT Pro", "ARGUS Air Max", "ARGUS Pod Pro", "ARGUS Pro Max",
    "ARGUS 2 Pro", "ARGUS 3 Max", "ARGUS Ultra Plus", "ARGUS Flex Edge", "ARGUS G Pro",
    "ARGUS P Max", "ARGUS M Plus", "ARGUS Z Pro", "ARGUS MT Max", "ARGUS GT Max"
]

DRAGX_PODS = [
    "DRAG X", "DRAG X Plus", "DRAG X Pro", "DRAG X Max", "DRAG X Ultra",
    "DRAG X 2", "DRAG X 3", "DRAG X Nano", "DRAG X Air", "DRAG X Flex",
    "DRAG X Pro Max", "DRAG X Ultra Plus", "DRAG X 2 Pro", "DRAG X 3 Max", "DRAG X Nano Pro",
    "DRAG X Air Plus", "DRAG X Flex Edge", "DRAG X Pro Ultra", "DRAG X Max Plus", "DRAG X 2 Ultra",
    "DRAG X 3 Pro", "DRAG X Nano Max", "DRAG X Air Pro", "DRAG X Flex Pro", "DRAG X Ultra Pro"
]

DRAGS_PODS = [
    "DRAG S", "DRAG S Plus", "DRAG S Pro", "DRAG S Max", "DRAG S Ultra",
    "DRAG S 2", "DRAG S 3", "DRAG S Nano", "DRAG S Air", "DRAG S Flex",
    "DRAG S Pro Max", "DRAG S Ultra Plus", "DRAG S 2 Pro", "DRAG S 3 Max", "DRAG S Nano Pro",
    "DRAG S Air Plus", "DRAG S Flex Edge", "DRAG S Pro Ultra", "DRAG S Max Plus", "DRAG S 2 Ultra"
]

LEGENDARY_PODS = [
    "DRAG 4", "DRAG 5", "DRAG 4 Pro", "DRAG 5 Pro", "DRAG 4 Max",
    "DRAG 5 Ultra", "DRAG 4 Plus", "DRAG 5 Plus", "DRAG 4 Titan", "DRAG 5 Titan",
    "DRAG 4 X", "DRAG 5 X", "DRAG 4 S", "DRAG 5 S", "DRAG 4 R",
    "DRAG 5 R", "DRAG 4 GT", "DRAG 5 GT", "DRAG 4 Ultimate", "DRAG 5 Ultimate"
]

CHROMATIC_PODS = [
    "DRAG 3", "DRAG 3 Pro", "DRAG 3 Max", "DRAG 3 Ultra", "DRAG 3 Plus",
    "DRAG 3 X", "DRAG 3 S", "DRAG 3 R", "DRAG 3 GT", "DRAG 3 Titan",
    "DRAG 3 Legend", "DRAG 3 Mythic", "DRAG 3 Godly", "DRAG 3 Eternal", "DRAG 3 Infinity",
    "DRAG 3 Chroma", "DRAG 3 Prism", "DRAG 3 Spectrum", "DRAG 3 Rainbow", "DRAG 3 Aurora"
]

ARCANA_PODS = [
    "XROS", "XROS 2", "XROS 3", "XROS 4", "XROS Pro",
    "XROS Nano", "XROS Mini", "XROS Air", "XROS Ultra", "XROS Max",
    "XROS X", "XROS S", "XROS R", "XROS GT", "XROS Titan",
    "XROS Legend", "XROS Mythic", "XROS Godly", "XROS Eternal", "XROS Infinity",
    "XROS Arcana", "XROS Mystic", "XROS Oracle", "XROS Prophet", "XROS Seer"
]

# ========== КЛАССЫ РЕДКОСТИ ==========
POD_RARITIES = {
    'Шерпотреб': {'pods': XSLIM_PODS, 'chance': 35, 'price': 100, 'mining_rate': 1, 'emoji': '⬜'},
    'Комонка': {'pods': VINCI_PODS, 'chance': 25, 'price': 250, 'mining_rate': 2, 'emoji': '🟢'},
    'Редкий': {'pods': ARGUS_PODS, 'chance': 15, 'price': 500, 'mining_rate': 3, 'emoji': '🔵'},
    'Епический': {'pods': DRAGX_PODS, 'chance': 10, 'price': 1000, 'mining_rate': 5, 'emoji': '🟣'},
    'Мифический': {'pods': DRAGS_PODS, 'chance': 7, 'price': 2500, 'mining_rate': 8, 'emoji': '🟠'},
    'Легендарный': {'pods': LEGENDARY_PODS, 'chance': 4, 'price': 5000, 'mining_rate': 12, 'emoji': '🔴'},
    'Хроматический': {'pods': CHROMATIC_PODS, 'chance': 2, 'price': 10000, 'mining_rate': 20, 'emoji': '💜'},
    'Аркана': {'pods': ARCANA_PODS, 'chance': 2, 'price': 25000, 'mining_rate': 35, 'emoji': '👑'}
}

def get_random_pod():
    rand = random.random() * 100
    cumulative = 0
    for rarity, data in POD_RARITIES.items():
        cumulative += data['chance']
        if rand <= cumulative:
            pod_name = random.choice(data['pods'])
            return {'name': pod_name, 'rarity': rarity, 'price': data['price'], 'mining_rate': data['mining_rate']}
    return {'name': XSLIM_PODS[0], 'rarity': 'Шерпотреб', 'price': 100, 'mining_rate': 1}# ========== БАЗА ДАННЫХ ==========
def get_db():
    conn = sqlite3.connect('casino.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    # Таблица пользователей - ТОЛЬКО ТЯЖКИ (единая валюта)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE,
        username TEXT,
        balance INTEGER DEFAULT 5000,
        last_daily_time TIMESTAMP,
        games_played INTEGER DEFAULT 0,
        total_won INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0
    )''')
    
    # Таблица подов игроков
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
    
    # Таблица рынка
    conn.execute('''CREATE TABLE IF NOT EXISTS market_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id TEXT,
        pod_id INTEGER,
        price INTEGER,
        listed_at TIMESTAMP
    )''')
    
    # Таблица активного майнинга
    conn.execute('''CREATE TABLE IF NOT EXISTS active_mining (
        user_id TEXT PRIMARY KEY,
        pod_id INTEGER,
        start_time TIMESTAMP,
        last_claim TIMESTAMP
    )''')
    
    # Таблица улучшений игрока
    conn.execute('''CREATE TABLE IF NOT EXISTS user_upgrades (
        user_id TEXT PRIMARY KEY,
        drop_chance_level INTEGER DEFAULT 0,
        cooldown_level INTEGER DEFAULT 0,
        rarity_luck_level INTEGER DEFAULT 0
    )''')
    
    conn.commit()
    conn.close()

init_db()

# ========== ОСНОВНЫЕ ФУНКЦИИ (ТОЛЬКО ТЯЖКИ) ==========
def get_user(telegram_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (str(telegram_id),)).fetchone()
    conn.close()
    return user

def create_user(telegram_id, username):
    conn = get_db()
    conn.execute("INSERT INTO users (telegram_id, username, balance, last_daily_time) VALUES (?, ?, 5000, ?)", 
                 (str(telegram_id), username, datetime.now() - timedelta(hours=24)))
    conn.commit()
    conn.close()

def get_balance(telegram_id):
    user = get_user(telegram_id)
    return user['balance'] if user else 5000

def update_balance(telegram_id, amount):
    conn = get_db()
    current = get_balance(telegram_id)
    new_balance = max(0, min(current + amount, MAX_BALANCE))
    conn.execute("UPDATE users SET balance = ? WHERE telegram_id = ?", (new_balance, str(telegram_id)))
    conn.commit()
    conn.close()
    return new_balance

def is_admin(user_id):
    user = get_user(user_id)
    return user['is_admin'] == 1 if user else False

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

def add_pod_to_user(user_id, pod_name, rarity, mining_rate):
    conn = get_db()
    conn.execute("INSERT INTO user_pods (user_id, pod_name, rarity, mining_rate) VALUES (?, ?, ?, ?)",
                 (str(user_id), pod_name, rarity, mining_rate))
    conn.commit()
    conn.close()

def delete_pod(pod_id):
    conn = get_db()
    conn.execute("DELETE FROM user_pods WHERE id = ?", (pod_id,))
    conn.commit()
    conn.close()

# ========== ФУНКЦИИ УЛУЧШЕНИЙ ==========
UPGRADE_COSTS = {
    'drop_chance': [0, 10000, 20000, 35000, 55000, 80000, 110000, 150000, 200000, 260000, 330000],
    'cooldown': [0, 5000, 12000, 22000, 35000, 52000, 73000, 98000, 128000, 163000, 205000],
    'rarity_luck': [0, 8000, 18000, 32000, 50000, 72000, 98000, 128000, 162000, 200000, 242000]
}

def get_user_upgrades(user_id):
    conn = get_db()
    upgrades = conn.execute("SELECT * FROM user_upgrades WHERE user_id = ?", (str(user_id),)).fetchone()
    conn.close()
    if not upgrades:
        return {'drop_chance_level': 0, 'cooldown_level': 0, 'rarity_luck_level': 0}
    return upgrades

def get_drop_chance_bonus(level):
    return min(level * 4, 40)

def get_cooldown_reduction(level):
    return min(level * 2, 20)

def get_rarity_luck_bonus(level):
    return min(level * 3, 30)# ========== ГЕНЕРАЦИЯ КРАША ==========
def generate_crash_point():
    rand = random.random() * 100
    if rand < 50:
        return round(random.uniform(1.1, 2.0), 2)
    elif rand < 75:
        return round(random.uniform(2.0, 3.0), 2)
    elif rand < 90:
        return round(random.uniform(3.0, 5.0), 2)
    elif rand < 97:
        return round(random.uniform(5.0, 10.0), 2)
    elif rand < 99:
        return round(random.uniform(10.0, 25.0), 2)
    else:
        return round(random.uniform(25.0, 75.0), 2)

# ========== CRASH GAME STATE ==========
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
                print(f"🚀 РАУНД {current_round_id} НАЧАЛСЯ! Краш на {crash_point}x")
                betting_timer = 10
        
        elif game_state == 'flying':
            time.sleep(0.07)
            current_multiplier = round(current_multiplier + 0.04, 2)
            
            auto_cashout_list = []
            for uid, bet_info in list(user_bets.items()):
                if not bet_info.get('cashed_out', False):
                    auto_cash = bet_info.get('auto_cash', 0)
                    if auto_cash > 0 and current_multiplier >= auto_cash:
                        win_amount = int(bet_info['bet'] * current_multiplier)
                        update_balance(uid, win_amount)
                        bet_info['cashed_out'] = True
                        auto_cashout_list.append(uid)
                        print(f"🤖 Авто-вывод {uid}: {win_amount} на {current_multiplier}x")
            
            for uid in auto_cashout_list:
                if uid in user_bets:
                    del user_bets[uid]
            
            if current_multiplier >= crash_point:
                game_state = 'crashed'
                print(f"💥 РАУНД {current_round_id} КРАШ на {crash_point}x!")
                crash_history.insert(0, crash_point)
                if len(crash_history) > 10:
                    crash_history.pop()
                user_bets.clear()
                
                def next_round():
                    global game_state, betting_timer
                    time.sleep(round_timer)
                    game_state = 'betting'
                    betting_timer = 10
                    print(f"🎲 НОВЫЙ РАУНД! Ставки принимаются {betting_timer} сек")
                
                threading.Thread(target=next_round, daemon=True).start()
        
        elif game_state == 'crashed':
            time.sleep(1)

threading.Thread(target=game_loop, daemon=True).start()# ========== TELEGRAM БОТ ==========
bot = telebot.TeleBot(BOT_TOKEN)

def setup_menu():
    commands = [
        BotCommand("start", "🏠 Главное меню"),
        BotCommand("casino", "🎰 Открыть казино"),
        BotCommand("daily", "🎁 Ежедневный под"),
        BotCommand("mypods", "📦 Мои поды"),
        BotCommand("balance", "💰 Баланс тяжек"),
        BotCommand("mine", "⛏️ Майнинг"),
        BotCommand("shop", "🏪 Магазин улучшений"),
        BotCommand("market", "🏪 Рынок подов"),
        BotCommand("help", "❓ Помощь")
    ]
    bot.set_my_commands(commands)
    bot.set_chat_menu_button(menu_button=MenuButtonCommands())

setup_menu()

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    if not get_user(user_id):
        create_user(user_id, username)
    
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("🎰 КАЗИНО"), KeyboardButton("🎁 DAILY"))
    keyboard.add(KeyboardButton("📦 МОИ ПОДЫ"), KeyboardButton("⛏️ МАЙНИНГ"))
    keyboard.add(KeyboardButton("💰 ТЯЖКИ"), KeyboardButton("🏪 МАГАЗИН"))
    keyboard.add(KeyboardButton("🏪 РЫНОК"), KeyboardButton("❓ ПОМОЩЬ"))
    
    bot.send_message(message.chat.id,
        f"🐐 **БУРМАЛДАТОЕ CASINO** 🐐\n\n"
        f"💰 Тяжки: {get_balance(user_id):,}\n\n"
        f"Выберите действие:",
        reply_markup=keyboard, parse_mode='Markdown')

@bot.message_handler(commands=['daily'])
def daily_pod(message):
    user_id = message.from_user.id
    
    last_daily = get_user(user_id)['last_daily_time'] if get_user(user_id) else datetime.now() - timedelta(hours=24)
    last_daily = datetime.fromisoformat(last_daily) if isinstance(last_daily, str) else last_daily
    now = datetime.now()
    time_diff = (now - last_daily).total_seconds()
    
    upgrades = get_user_upgrades(user_id)
    cooldown_hours = 24 - get_cooldown_reduction(upgrades['cooldown_level'])
    
    if time_diff < cooldown_hours * 3600:
        remaining = int((cooldown_hours * 3600 - time_diff) / 3600)
        bot.reply_to(message, f"⏰ Следующий под через {remaining} часов!")
        return
    
    drop_bonus = get_drop_chance_bonus(upgrades['drop_chance_level'])
    
    rand = random.random() * 100
    cumulative = 0
    selected_rarity = None
    for rarity, data in POD_RARITIES.items():
        modified_chance = data['chance'] + (drop_bonus if rarity != 'Аркана' else 0)
        cumulative += modified_chance
        if rand <= cumulative:
            selected_rarity = rarity
            break
    
    if not selected_rarity:
        selected_rarity = 'Шерпотреб'
    
    pod_data = POD_RARITIES[selected_rarity]
    pod_name = random.choice(pod_data['pods'])
    
    add_pod_to_user(user_id, pod_name, selected_rarity, pod_data['mining_rate'])
    
    conn = get_db()
    conn.execute("UPDATE users SET last_daily_time = ? WHERE telegram_id = ?", (now.isoformat(), str(user_id)))
    conn.commit()
    conn.close()
    
    bot.reply_to(message,
        f"🎁 **ВЫ ПОЛУЧИЛИ ПОД!** 🎁\n\n"
        f"{pod_data['emoji']} **{pod_name}**\n"
        f"⭐ Редкость: {selected_rarity}\n"
        f"💰 Цена продажи: {pod_data['price']} тяжек\n"
        f"⛏️ Майнинг: {pod_data['mining_rate']} тяжек/час\n\n"
        f"📊 Ваши улучшения:\n"
        f"• Шанс выпадения: +{drop_bonus}%\n"
        f"• Перезарядка: {cooldown_hours}ч",
        parse_mode='Markdown')

@bot.message_handler(commands=['mypods'])
def my_pods(message):
    user_id = message.from_user.id
    pods = get_user_pods(user_id)
    
    if not pods:
        bot.reply_to(message, "📦 У вас нет подов! Используйте /daily")
        return
    
    text = "📦 **ВАША КОЛЛЕКЦИЯ ПОДОВ** 📦\n\n"
    for pod in pods:
        rarity_data = POD_RARITIES.get(pod['rarity'], {})
        text += f"🆔 `{pod['id']}` | {rarity_data.get('emoji', '📟')} {pod['pod_name']}\n"
        text += f"   ⭐ {pod['rarity']} | Ур.{pod['level']} | ⛏️ {pod['mining_rate']} тяжек/ч\n"
        text += f"   💰 Цена: {rarity_data.get('price', 100)} тяжек\n\n"
    
    text += "💡 `/upgrade id` - улучшить под\n"
    text += "💡 `/sell id` - продать под\n"
    text += "💡 `/list id цена` - выставить на рынок"
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['balance'])
def balance_cmd(message):
    bot.reply_to(message, f"💰 **ТЯЖКИ:** {get_balance(message.from_user.id):,}", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message,
        f"❓ **ПОМОЩЬ** ❓\n\n"
        f"🎰 **КАЗИНО:** /casino\n"
        f"🎁 **ЕЖЕДНЕВНЫЙ ПОД:** /daily\n"
        f"📦 **МОИ ПОДЫ:** /mypods\n"
        f"⛏️ **МАЙНИНГ:** /mine start ID | /mine claim | /mine stop\n"
        f"🏪 **МАГАЗИН УЛУЧШЕНИЙ:** /shop\n"
        f"🏪 **РЫНОК ПОДОВ:** /market\n"
        f"💰 **БАЛАНС:** /balance\n\n"
        f"👑 **АДМИН-КОМАНДЫ:**\n"
        f"• /addmoney @user сумма - выдать тяжки\n"
        f"• /givepod @user - выдать случайный под", parse_mode='Markdown')# ========== МАЙНИНГ ==========
@bot.message_handler(commands=['mine'])
def mine_command(message):
    args = message.text.split()
    user_id = message.from_user.id
    
    if len(args) < 2:
        bot.reply_to(message, "⛏️ `/mine start ID` - начать майнинг\n⛏️ `/mine claim` - забрать\n⛏️ `/mine stop` - остановить", parse_mode='Markdown')
        return
    
    action = args[1]
    
    if action == 'start':
        if len(args) < 3:
            bot.reply_to(message, "❌ Укажите ID пода: `/mine start 1`", parse_mode='Markdown')
            return
        
        pod_id = int(args[2])
        pod = get_pod_by_id(pod_id)
        
        if not pod or pod['user_id'] != str(user_id):
            bot.reply_to(message, "❌ Под не найден!")
            return
        
        conn = get_db()
        existing = conn.execute("SELECT * FROM active_mining WHERE user_id = ?", (str(user_id),)).fetchone()
        if existing:
            bot.reply_to(message, "❌ У вас уже активен майнинг! Используйте /mine stop")
            conn.close()
            return
        
        conn.execute("INSERT INTO active_mining (user_id, pod_id, start_time, last_claim) VALUES (?, ?, ?, ?)",
                     (str(user_id), pod_id, datetime.now().isoformat(), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, f"✅ **МАЙНИНГ ЗАПУЩЕН!**\n\n📟 {pod['pod_name']}\n⛏️ {pod['mining_rate']} тяжек/час", parse_mode='Markdown')
    
    elif action == 'claim':
        conn = get_db()
        mining = conn.execute("SELECT * FROM active_mining WHERE user_id = ?", (str(user_id),)).fetchone()
        if not mining:
            bot.reply_to(message, "❌ Нет активного майнинга!")
            conn.close()
            return
        
        pod = get_pod_by_id(mining['pod_id'])
        last_claim = datetime.fromisoformat(mining['last_claim'])
        now = datetime.now()
        hours = (now - last_claim).total_seconds() / 3600
        earned = int(hours * pod['mining_rate'])
        
        if earned > 0:
            update_balance(user_id, earned)
            conn.execute("UPDATE active_mining SET last_claim = ? WHERE user_id = ?", (now.isoformat(), str(user_id)))
            conn.commit()
            bot.reply_to(message, f"⛏️ **ВЫ ПОЛУЧИЛИ {earned} ТЯЖЕК!**", parse_mode='Markdown')
        else:
            bot.reply_to(message, "⏳ Майнинг ещё не принёс тяжки!", parse_mode='Markdown')
        conn.close()
    
    elif action == 'stop':
        conn = get_db()
        conn.execute("DELETE FROM active_mining WHERE user_id = ?", (str(user_id),))
        conn.commit()
        conn.close()
        bot.reply_to(message, "✅ **МАЙНИНГ ОСТАНОВЛЕН**", parse_mode='Markdown')

# ========== ПРОДАЖА ПОДА ==========
@bot.message_handler(commands=['sell'])
def sell_pod(message):
    args = message.text.split()
    user_id = message.from_user.id
    
    if len(args) < 2:
        bot.reply_to(message, "❌ `/sell pod_id`", parse_mode='Markdown')
        return
    
    pod_id = int(args[1])
    pod = get_pod_by_id(pod_id)
    
    if not pod or pod['user_id'] != str(user_id):
        bot.reply_to(message, "❌ Под не найден!")
        return
    
    rarity_data = POD_RARITIES.get(pod['rarity'], {})
    price = rarity_data.get('price', 100)
    
    delete_pod(pod_id)
    update_balance(user_id, price)
    
    bot.reply_to(message, f"✅ **ПРОДАНО!**\n\n📟 {pod['pod_name']}\n💰 +{price} ТЯЖЕК\n💰 Баланс: {get_balance(user_id):,}", parse_mode='Markdown')

# ========== УЛУЧШЕНИЕ ПОДА ==========
@bot.message_handler(commands=['upgrade'])
def upgrade_pod(message):
    args = message.text.split()
    user_id = message.from_user.id
    
    if len(args) < 2:
        bot.reply_to(message, "❌ `/upgrade pod_id`", parse_mode='Markdown')
        return
    
    pod_id = int(args[1])
    pod = get_pod_by_id(pod_id)
    
    if not pod or pod['user_id'] != str(user_id):
        bot.reply_to(message, "❌ Под не найден!")
        return
    
    cost = pod['level'] * 100
    balance = get_balance(user_id)
    
    if balance < cost:
        bot.reply_to(message, f"❌ Нужно {cost} тяжек!", parse_mode='Markdown')
        return
    
    chance = max(5, min(95, 80 / pod['level']))
    success = random.random() * 100 < chance
    
    if success:
        new_rate = int(pod['mining_rate'] * 1.5)
        conn = get_db()
        conn.execute("UPDATE user_pods SET level = level + 1, mining_rate = ? WHERE id = ?", (new_rate, pod_id))
        conn.commit()
        conn.close()
        update_balance(user_id, -cost)
        bot.reply_to(message, f"✅ **АПГРЕЙД УСПЕШЕН!**\n\n📟 {pod['pod_name']}\n📈 Уровень {pod['level']+1}\n⛏️ {new_rate} тяжек/час", parse_mode='Markdown')
    else:
        update_balance(user_id, -cost)
        bot.reply_to(message, f"❌ **АПГРЕЙД НЕ УДАЛСЯ!**\n\nШанс был {chance:.1f}%\n💰 Потеряно: {cost} тяжек", parse_mode='Markdown')

# ========== МАГАЗИН УЛУЧШЕНИЙ ==========
@bot.message_handler(commands=['shop'])
def shop_command(message):
    user_id = message.from_user.id
    upgrades = get_user_upgrades(user_id)
    balance = get_balance(user_id)
    
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(f"🎲 Шанс выпадения (ур.{upgrades['drop_chance_level']}/10) - {UPGRADE_COSTS['drop_chance'][upgrades['drop_chance_level']+1] if upgrades['drop_chance_level'] < 10 else 'MAX'} тяжек", 
                             callback_data=f"buy_drop_{upgrades['drop_chance_level']+1}"),
        InlineKeyboardButton(f"⏱️ Перезарядка подов (ур.{upgrades['cooldown_level']}/10) - {UPGRADE_COSTS['cooldown'][upgrades['cooldown_level']+1] if upgrades['cooldown_level'] < 10 else 'MAX'} тяжек", 
                             callback_data=f"buy_cooldown_{upgrades['cooldown_level']+1}"),
        InlineKeyboardButton(f"🍀 Удача на редкость (ур.{upgrades['rarity_luck_level']}/10) - {UPGRADE_COSTS['rarity_luck'][upgrades['rarity_luck_level']+1] if upgrades['rarity_luck_level'] < 10 else 'MAX'} тяжек", 
                             callback_data=f"buy_luck_{upgrades['rarity_luck_level']+1}")
    )
    
    text = f"🏪 **МАГАЗИН УЛУЧШЕНИЙ** 🏪\n\n"
    text += f"💰 Ваши тяжки: {balance:,}\n\n"
    text += f"📊 **ТЕКУЩИЕ УРОВНИ:**\n"
    text += f"• Шанс выпадения: {upgrades['drop_chance_level']}/10 (+{get_drop_chance_bonus(upgrades['drop_chance_level'])}%)\n"
    text += f"• Перезарядка: {upgrades['cooldown_level']}/10 (-{get_cooldown_reduction(upgrades['cooldown_level'])}ч)\n"
    text += f"• Удача: {upgrades['rarity_luck_level']}/10 (+{get_rarity_luck_bonus(upgrades['rarity_luck_level'])}%)\n\n"
    text += f"📈 **МАКСИМАЛЬНЫЕ БОНУСЫ (10 ур.):**\n"
    text += f"• +40% к шансу выпадения\n"
    text += f"• Перезарядка 4ч (вместо 24ч)\n"
    text += f"• +30% к шансу редких подов"
    
    bot.send_message(message.chat.id, text, reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def buy_upgrade(call):
    user_id = call.from_user.id
    data = call.data.split('_')
    upgrade_type = data[1]
    new_level = int(data[2])
    
    upgrades = get_user_upgrades(user_id)
    current_level = upgrades[f'{upgrade_type}_level']
    
    if new_level <= current_level:
        bot.answer_callback_query(call.id, "У вас уже есть этот уровень!", show_alert=True)
        return
    
    if new_level > 10:
        bot.answer_callback_query(call.id, "Максимальный уровень достигнут!", show_alert=True)
        return
    
    cost = UPGRADE_COSTS[upgrade_type][new_level]
    balance = get_balance(user_id)
    
    if balance < cost:
        bot.answer_callback_query(call.id, f"Не хватает {cost} тяжек!", show_alert=True)
        return
    
    update_balance(user_id, -cost)
    
    conn = get_db()
    conn.execute(f"INSERT OR REPLACE INTO user_upgrades (user_id, {upgrade_type}_level) VALUES (?, ?)",
                 (str(user_id), new_level))
    conn.commit()
    conn.close()
    
    upgrade_names = {'drop': 'Шанс выпадения', 'cooldown': 'Перезарядка', 'luck': 'Удача'}
    bot.answer_callback_query(call.id, f"✅ {upgrade_names[upgrade_type]} улучшен до {new_level} уровня!", show_alert=True)
    
    shop_command(call.message)

# ========== РЫНОК ПОДОВ ==========
@bot.message_handler(commands=['list'])
def list_pod(message):
    args = message.text.split()
    user_id = message.from_user.id
    
    if len(args) < 3:
        bot.reply_to(message, "❌ `/list pod_id цена`", parse_mode='Markdown')
        return
    
    pod_id = int(args[1])
    price = int(args[2])
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
    
    bot.reply_to(message, f"✅ **ПОД ВЫСТАВЛЕН НА РЫНОК!**\n\n📟 {pod['pod_name']}\n💰 Цена: {price} тяжек", parse_mode='Markdown')

@bot.message_handler(commands=['market'])
def market_command(message):
    conn = get_db()
    listings = conn.execute('''
        SELECT m.id, m.price, m.seller_id, u.username, p.pod_name, p.rarity 
        FROM market_listings m 
        JOIN user_pods p ON m.pod_id = p.id 
        LEFT JOIN users u ON m.seller_id = u.telegram_id 
        WHERE m.seller_id != ? AND p.is_listed = 1
        ORDER BY m.listed_at DESC
    ''', (str(message.from_user.id),)).fetchall()
    conn.close()
    
    if not listings:
        bot.reply_to(message, "🏪 **РЫНОК ПУСТ**\n\nВыставите свой под: `/list pod_id цена`", parse_mode='Markdown')
        return
    
    text = "🏪 **ВТОРИЧНЫЙ РЫНОК** 🏪\n\n"
    for listing in listings[:20]:
        rarity_data = POD_RARITIES.get(listing['rarity'], {})
        text += f"🆔 `{listing['id']}` | {rarity_data.get('emoji', '📟')} {listing['pod_name']}\n"
        text += f"   ⭐ {listing['rarity']} | 👤 @{listing['username'] or listing['seller_id'][:8]}\n"
        text += f"   💰 {listing['price']} тяжек\n\n"
    
    text += "💡 Купить: `/buy listing_id`"
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['buy'])
def buy_pod(message):
    args = message.text.split()
    user_id = message.from_user.id
    
    if len(args) < 2:
        bot.reply_to(message, "❌ `/buy listing_id`", parse_mode='Markdown')
        return
    
    listing_id = int(args[1])
    
    conn = get_db()
    listing = conn.execute('''
        SELECT m.*, p.pod_name, p.rarity, p.mining_rate, p.user_id as owner_id
        FROM market_listings m 
        JOIN user_pods p ON m.pod_id = p.id 
        WHERE m.id = ?
    ''', (listing_id,)).fetchone()
    
    if not listing:
        bot.reply_to(message, "❌ Объявление не найдено!")
        conn.close()
        return
    
    if listing['seller_id'] == str(user_id):
        bot.reply_to(message, "❌ Нельзя купить свой под!")
        conn.close()
        return
    
    balance = get_balance(user_id)
    
    if balance < listing['price']:
        bot.reply_to(message, f"❌ Нужно {listing['price']} тяжек!", parse_mode='Markdown')
        conn.close()
        return
    
    # Передача пода
    conn.execute("UPDATE user_pods SET user_id = ?, is_listed = 0, list_price = 0 WHERE id = ?", 
                 (str(user_id), listing['pod_id']))
    conn.execute("DELETE FROM market_listings WHERE id = ?", (listing_id,))
    
    # Перевод денег продавцу
    update_balance(listing['seller_id'], listing['price'])
    update_balance(user_id, -listing['price'])
    
    conn.commit()
    conn.close()
    
    bot.reply_to(message,
        f"✅ **ПОД КУПЛЕН!**\n\n"
        f"📟 {listing['pod_name']}\n"
        f"⭐ {listing['rarity']}\n"
        f"💰 Потрачено: {listing['price']} тяжек\n\n"
        f"💰 Ваш баланс: {get_balance(user_id):,} тяжек", parse_mode='Markdown')# ========== КНОПКИ КЛАВИАТУРЫ ==========
@bot.message_handler(func=lambda m: m.text == "🎰 КАЗИНО")
def casino_button(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎰 ВОЙТИ В КАЗИНО", url=f"{WEB_URL}?tg_id={user_id}&tg_name={username}"))
    bot.send_message(message.chat.id, "Нажмите на кнопку:", reply_markup=kb)

@bot.message_handler(commands=['casino'])
def casino_cmd(message):
    casino_button(message)

@bot.message_handler(func=lambda m: m.text == "🎁 DAILY")
def daily_button(message):
    daily_pod(message)

@bot.message_handler(func=lambda m: m.text == "📦 МОИ ПОДЫ")
def mypods_button(message):
    my_pods(message)

@bot.message_handler(func=lambda m: m.text == "⛏️ МАЙНИНГ")
def mine_button(message):
    mine_command(message)

@bot.message_handler(func=lambda m: m.text == "💰 ТЯЖКИ")
def balance_button(message):
    balance_cmd(message)

@bot.message_handler(func=lambda m: m.text == "🏪 МАГАЗИН")
def shop_button(message):
    shop_command(message)

@bot.message_handler(func=lambda m: m.text == "🏪 РЫНОК")
def market_button(message):
    market_command(message)

@bot.message_handler(func=lambda m: m.text == "❓ ПОМОЩЬ")
def help_button(message):
    help_cmd(message)

# ========== АДМИН-КОМАНДЫ ==========
@bot.message_handler(commands=['addmoney'])
def add_money(message):
    if not is_admin(message.from_user.id):
        return
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ /addmoney @user 1000")
            return
        user_input = parts[1]
        amount = int(parts[2])
        telegram_id = None
        if user_input.startswith('@'):
            conn = get_db()
            user = conn.execute("SELECT telegram_id FROM users WHERE username LIKE ?", (f'%{user_input[1:]}%',)).fetchone()
            conn.close()
            if user:
                telegram_id = user['telegram_id']
        else:
            telegram_id = user_input
        if not telegram_id:
            bot.reply_to(message, "❌ Пользователь не найден!")
            return
        new_balance = update_balance(telegram_id, amount)
        bot.reply_to(message, f"✅ Выдано {amount:,} тяжек\n💰 Новый баланс: {new_balance:,}")
    except:
        bot.reply_to(message, "❌ Ошибка!")

@bot.message_handler(commands=['givepod'])
def give_pod(message):
    if not is_admin(message.from_user.id):
        return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ /givepod @user")
            return
        user_input = parts[1]
        telegram_id = None
        if user_input.startswith('@'):
            conn = get_db()
            user = conn.execute("SELECT telegram_id FROM users WHERE username LIKE ?", (f'%{user_input[1:]}%',)).fetchone()
            conn.close()
            if user:
                telegram_id = user['telegram_id']
        else:
            telegram_id = user_input
        if not telegram_id:
            bot.reply_to(message, "❌ Пользователь не найден!")
            return
        pod = get_random_pod()
        add_pod_to_user(telegram_id, pod['name'], pod['rarity'], pod['mining_rate'])
        bot.reply_to(message, f"✅ Выдан под {pod['name']} ({pod['rarity']})")
    except:
        bot.reply_to(message, "❌ Ошибка!")# ========== FLASK ВЕБ-СЕРВЕР (ДИЗАЙН PHONEGET) ==========
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

WEB_HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Бурмалдатое Casino</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background: linear-gradient(135deg, #0a0f1e 0%, #0f1629 100%);
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
            padding: 12px;
        }

        /* Главный контейнер - как на скриншоте */
        .casino-container {
            max-width: 500px;
            margin: 0 auto;
            background: rgba(10, 15, 30, 0.85);
            backdrop-filter: blur(20px);
            border-radius: 28px;
            border: 1px solid rgba(255, 215, 0, 0.25);
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }

        /* Шапка как на скриншоте */
        .header {
            background: linear-gradient(135deg, #1a1f2e 0%, #0d1225 100%);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #ffd700;
        }

        .casino-title {
            font-size: 24px;
            font-weight: bold;
            background: linear-gradient(45deg, #ffd700, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 1px;
        }

        .balance-box {
            background: rgba(0,0,0,0.5);
            border-radius: 20px;
            padding: 12px;
            margin-top: 12px;
        }

        .balance-label {
            font-size: 12px;
            color: #888;
            letter-spacing: 1px;
        }

        .balance-amount {
            font-size: 36px;
            font-weight: bold;
            color: #ffd700;
            text-shadow: 0 0 10px rgba(255,215,0,0.3);
        }

        /* Ряд коэффициентов как на скриншоте */
        .multipliers-row {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 8px;
            padding: 15px;
            background: rgba(0,0,0,0.3);
            text-align: center;
        }

        .multiplier-item {
            background: rgba(255,255,255,0.08);
            padding: 8px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: bold;
            color: #ffd700;
        }

        /* Навигация по играм - 5 кнопок */
        .game-nav {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 5px;
            padding: 15px;
            background: rgba(0,0,0,0.3);
        }

        .game-btn {
            background: rgba(255,255,255,0.08);
            border: none;
            padding: 12px 5px;
            border-radius: 16px;
            color: #aaa;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
        }

        .game-btn span:first-child {
            font-size: 22px;
        }

        .game-btn.active {
            background: linear-gradient(135deg, #ffd700, #ff8c00);
            color: #000;
            box-shadow: 0 4px 12px rgba(255,215,0,0.3);
        }

        .game-area {
            padding: 20px;
            min-height: 450px;
        }

        /* CRASH игра */
        .crash-container {
            background: linear-gradient(180deg, #1a1f2e 0%, #0d1225 100%);
            border-radius: 24px;
            overflow: hidden;
        }

        .crash-header {
            background: #00000033;
            padding: 25px;
            text-align: center;
        }

        .crash-multiplier {
            font-size: 64px;
            font-weight: 800;
            color: #ffd700;
            text-shadow: 0 0 20px rgba(255,215,0,0.5);
            font-family: monospace;
            letter-spacing: 4px;
        }

        .crash-status {
            text-align: center;
            font-size: 14px;
            padding: 8px;
            border-radius: 20px;
            margin-top: 10px;
        }

        .status-betting { background: #ff8c00; color: #000; }
        .status-flying { background: #2ed573; color: #000; animation: pulse 0.5s infinite; }
        .status-crashed { background: #ff4757; color: #fff; }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .timer-section {
            background: #00000033;
            padding: 15px;
            text-align: center;
            margin: 15px;
            border-radius: 20px;
        }

        .timer-value {
            font-size: 28px;
            font-weight: bold;
            color: #ffd700;
        }

        .crash-history {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
            margin: 15px;
            padding: 10px;
            background: #00000033;
            border-radius: 20px;
        }

        .history-crash-item {
            background: rgba(255,255,255,0.1);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }

        /* Блок ставок */
        .bet-section {
            padding: 16px;
        }

        .bet-input {
            width: 100%;
            background: rgba(0,0,0,0.5);
            border: 1px solid rgba(255,215,0,0.3);
            padding: 14px;
            border-radius: 16px;
            color: white;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 12px;
        }

        .bet-presets {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 16px;
        }

        .preset-btn {
            background: rgba(255,255,255,0.08);
            border: none;
            padding: 10px;
            border-radius: 12px;
            color: #ffd700;
            font-weight: bold;
            cursor: pointer;
            font-size: 14px;
        }

        .auto-cash-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #00000033;
            padding: 12px;
            border-radius: 16px;
            margin-bottom: 16px;
        }

        .auto-cash-input {
            background: rgba(0,0,0,0.5);
            border: 1px solid #ffd700;
            padding: 8px 12px;
            border-radius: 12px;
            color: #ffd700;
            font-size: 16px;
            width: 80px;
            text-align: center;
        }

        .action-btn {
            width: 100%;
            background: linear-gradient(135deg, #ffd700, #ff8c00);
            border: none;
            padding: 16px;
            border-radius: 20px;
            font-size: 18px;
            font-weight: bold;
            color: #000;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .action-btn:active {
            transform: scale(0.98);
        }

        .bet-status {
            text-align: center;
            margin-top: 12px;
            font-size: 12px;
            color: #aaa;
        }

        /* Слоты */
        .slots-reels {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 30px 0;
        }

        .slot-reel {
            width: 85px;
            height: 85px;
            background: rgba(0,0,0,0.6);
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 52px;
            border: 2px solid #ffd700;
            box-shadow: 0 0 15px rgba(255,215,0,0.2);
        }

        /* Рулетка с колесом */
        .roulette-container {
            text-align: center;
        }

        .roulette-wheel {
            position: relative;
            width: 280px;
            height: 280px;
            margin: 0 auto;
        }

        .roulette-canvas {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            box-shadow: 0 0 20px rgba(255,215,0,0.3);
        }

        .roulette-ball {
            position: absolute;
            width: 12px;
            height: 12px;
            background: white;
            border-radius: 50%;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            box-shadow: 0 0 8px white;
            transition: all 0.05s linear;
            z-index: 10;
        }

        .roulette-bets {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 20px 0;
        }

        .bet-option {
            background: rgba(0,0,0,0.5);
            border: 1px solid #ffd700;
            padding: 12px;
            border-radius: 16px;
            cursor: pointer;
            text-align: center;
            font-weight: bold;
            transition: all 0.2s;
        }

        .bet-option.selected {
            background: #ffd700;
            color: #000;
        }

        .bet-option.red { border-color: #ff4757; color: #ff4757; }
        .bet-option.black { border-color: #aaa; color: #aaa; }
        .bet-option.green { border-color: #2ed573; color: #2ed573; }
        .bet-option.selected { background: #ffd700; color: #000; }

        .numbers-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
            margin: 20px 0;
            max-height: 180px;
            overflow-y: auto;
        }

        .num-btn {
            background: rgba(255,255,255,0.08);
            border: none;
            padding: 12px;
            border-radius: 12px;
            color: white;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
        }

        .num-btn.selected {
            background: #ffd700;
            color: #000;
        }

        /* Игра МИНЫ */
        .mines-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin: 20px 0;
        }

        .mine-cell {
            aspect-ratio: 1;
            background: rgba(255,255,255,0.08);
            border: 1px solid #ffd700;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .mine-cell.revealed {
            background: #2ed57333;
            border-color: #2ed573;
        }

        .mine-cell.mine {
            background: #ff475733;
            border-color: #ff4757;
        }

        /* История игр */
        .history-section {
            padding: 15px;
            border-top: 1px solid rgba(255,215,0,0.2);
            max-height: 160px;
            overflow-y: auto;
        }

        .history-title {
            font-size: 11px;
            color: #666;
            margin-bottom: 8px;
        }

        .history-item {
            background: rgba(255,255,255,0.04);
            padding: 8px 12px;
            margin: 4px 0;
            border-radius: 10px;
            font-size: 11px;
            display: flex;
            justify-content: space-between;
        }

        .win-text { color: #4caf50; font-weight: bold; }
        .lose-text { color: #ff4757; font-weight: bold; }

        /* Промо блок */
        .promo-block {
            text-align: center;
            padding: 40px 20px;
        }

        .promo-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }

        /* Адаптив */
        @media (max-width: 480px) {
            .slot-reel { width: 65px; height: 65px; font-size: 40px; }
            .crash-multiplier { font-size: 48px; }
            .roulette-wheel { width: 240px; height: 240px; }
            .game-btn { font-size: 11px; }
            .game-btn span:first-child { font-size: 18px; }
        }
    </style>
</head>
<body>
<div class="casino-container">
    <div class="header">
        <div class="casino-title">🐐 БУРМАЛДАТОЕ CASINO 🐐</div>
        <div class="balance-box">
            <div class="balance-label">ТЯЖКИ:</div>
            <div class="balance-amount" id="balance">0</div>
        </div>
    </div>

    <!-- Ряд коэффициентов как на скриншоте -->
    <div class="multipliers-row" id="multipliersRow">
        <div class="multiplier-item">1.56x</div>
        <div class="multiplier-item">1.45x</div>
        <div class="multiplier-item">2.01x</div>
        <div class="multiplier-item">1.00x</div>
        <div class="multiplier-item">2.90x</div>
    </div>

    <div class="game-nav">
        <button class="game-btn active" data-game="crash"><span>💥</span><span>КРАШ</span></button>
        <button class="game-btn" data-game="slots"><span>🎰</span><span>СЛОТЫ</span></button>
        <button class="game-btn" data-game="roulette"><span>🎡</span><span>РУЛЕТКА</span></button>
        <button class="game-btn" data-game="mines"><span>💣</span><span>МИНЫ</span></button>
        <button class="game-btn" data-game="promo"><span>🎁</span><span>ПРОМО</span></button>
    </div>

    <div class="game-area" id="gameArea">
        <!-- CRASH ИГРА -->
        <div id="crashGame">
            <div class="crash-container">
                <div class="crash-header">
                    <div class="crash-multiplier" id="currentMult">1.00x</div>
                    <div class="crash-status status-betting" id="crashStatus">🎲 ПРИЁМ СТАВОК</div>
                </div>
                <div class="timer-section">
                    <div>⏱️ ДО ПОЛЁТА</div>
                    <div class="timer-value" id="timerValue">10</div>
                </div>
                <div class="crash-history" id="crashHistory"></div>
                <div class="bet-section">
                    <input type="number" id="betAmount" class="bet-input" placeholder="СТАВКА" value="100">
                    <div class="bet-presets">
                        <button class="preset-btn" data-bet="100">Min</button>
                        <button class="preset-btn" data-bet="1000">1K</button>
                        <button class="preset-btn" data-bet="5000">5K</button>
                        <button class="preset-btn" data-bet="max">Max</button>
                    </div>
                    <div class="auto-cash-row">
                        <span>🤖 АВТО-ВЫВОД (x):</span>
                        <input type="number" id="autoCash" class="auto-cash-input" value="2.00" step="0.5">
                    </div>
                    <button class="action-btn" id="placeBetBtn">💰 СДЕЛАТЬ СТАВКУ</button>
                    <button class="action-btn" id="cashoutBtn" style="display:none">✅ ЗАБРАТЬ</button>
                    <div class="bet-status" id="betStatus"></div>
                </div>
            </div>
        </div>

        <!-- СЛОТЫ -->
        <div id="slotsGame" style="display:none">
            <div class="slots-reels">
                <div class="slot-reel" id="slot1">🍒</div>
                <div class="slot-reel" id="slot2">🍋</div>
                <div class="slot-reel" id="slot3">🍊</div>
            </div>
            <div class="bet-section">
                <input type="number" id="slotsBet" class="bet-input" placeholder="СТАВКА" value="100">
                <div class="bet-presets">
                    <button class="preset-btn" data-bet="100">Min</button>
                    <button class="preset-btn" data-bet="1000">1K</button>
                    <button class="preset-btn" data-bet="5000">5K</button>
                    <button class="preset-btn" data-bet="max">Max</button>
                </div>
                <button class="action-btn" id="slotsSpinBtn">🎰 КРУТИТЬ</button>
            </div>
        </div>

        <!-- РУЛЕТКА -->
        <div id="rouletteGame" style="display:none">
            <div class="roulette-container">
                <div class="roulette-wheel">
                    <canvas id="wheelCanvas" width="280" height="280" class="roulette-canvas"></canvas>
                    <div class="roulette-ball" id="ball" style="display:none;"></div>
                </div>
                <div class="roulette-bets">
                    <div class="bet-option red" data-bet="red">🔴 КРАСНОЕ (x2)</div>
                    <div class="bet-option black" data-bet="black">⚫ ЧЁРНОЕ (x2)</div>
                    <div class="bet-option green" data-bet="green">🟢 ЗЕЛЁНОЕ (x36)</div>
                </div>
                <div class="numbers-grid" id="rouletteNumbers"></div>
                <div class="bet-section">
                    <input type="number" id="rouletteBet" class="bet-input" placeholder="СТАВКА" value="100">
                    <div class="bet-presets">
                        <button class="preset-btn" data-bet="100">Min</button>
                        <button class="preset-btn" data-bet="1000">1K</button>
                        <button class="preset-btn" data-bet="5000">5K</button>
                        <button class="preset-btn" data-bet="max">Max</button>
                    </div>
                    <button class="action-btn" id="rouletteSpinBtn">🎡 КРУТИТЬ</button>
                </div>
            </div>
        </div>

        <!-- МИНЫ -->
        <div id="minesGame" style="display:none">
            <div style="text-align:center; font-size:12px; color:#aaa; margin-bottom:15px;">
                💣 Открывайте клетки. Найдёте мину - проиграете ставку! 💣
            </div>
            <div class="mines-grid" id="minesGrid"></div>
            <div class="bet-section">
                <input type="number" id="minesBet" class="bet-input" placeholder="СТАВКА" value="100">
                <div class="bet-presets">
                    <button class="preset-btn" data-bet="100">Min</button>
                    <button class="preset-btn" data-bet="1000">1K</button>
                    <button class="preset-btn" data-bet="5000">5K</button>
                    <button class="preset-btn" data-bet="max">Max</button>
                </div>
                <button class="action-btn" id="minesNewGameBtn">🎲 НОВАЯ ИГРА</button>
                <div class="bet-status" id="minesStatus"></div>
            </div>
        </div>

        <!-- ПРОМО -->
        <div id="promoGame" style="display:none">
            <div class="promo-block">
                <div class="promo-icon">🎁</div>
                <div style="font-size:18px; font-weight:bold;">ЕЖЕДНЕВНЫЙ БОНУС</div>
                <div style="font-size:12px; color:#aaa; margin:10px 0;">от 100 до 100 000 тяжек каждые 10 минут</div>
                <button class="action-btn" id="promoBonusBtn">🎁 ПОЛУЧИТЬ БОНУС</button>
            </div>
        </div>
    </div>

    <div class="history-section">
        <div class="history-title">📜 ИСТОРИЯ ИГР</div>
        <div id="historyList"></div>
    </div>
</div>

<script>
    const urlParams = new URLSearchParams(window.location.search);
    let tgId = urlParams.get('tg_id');
    let currentBalance = 0;
    let myBet = 0, myAutoCash = 2.00, hasBet = false, hasCashedOut = false;
    let currentMult = 1.00, gameState = 'betting', timerSec = 10, crashHistory = [];
    let isSpinning = false;
    let selectedRouletteBet = null;
    let minesGame = { active: false, bet: 0, totalCells: 25, mineCount: 5, revealed: [], isMine: [], multiplier: 1.0 };

    const symbols = ['🍒', '🍋', '🍊', '🔔', '💎', '7️⃣'];
    const symbolMultipliers = {'🍒':2, '🍋':3, '🍊':5, '🔔':7, '💎':10, '7️⃣':20};
    const redNumbers = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36];
    const blackNumbers = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35];

    // Анимация ряда коэффициентов
    setInterval(() => {
        document.querySelectorAll('.multiplier-item').forEach(el => {
            el.innerText = (Math.random() * 3 + 0.5).toFixed(2) + 'x';
        });
    }, 4000);

    // Рулетка колесо
    let wheelCanvas, wheelCtx, wheelNumbers = [];
    for(let i = 0; i <= 36; i++) wheelNumbers.push(i);

    function drawWheel() {
        if(!wheelCanvas) {
            wheelCanvas = document.getElementById('wheelCanvas');
            if(!wheelCanvas) return;
            wheelCtx = wheelCanvas.getContext('2d');
        }
        let anglePer = (Math.PI * 2) / 37;
        wheelCtx.clearRect(0, 0, 280, 280);
        for(let i = 0; i <= 36; i++) {
            let start = i * anglePer;
            let end = start + anglePer;
            let color;
            if(i === 0) color = '#2ed573';
            else if(redNumbers.includes(i)) color = '#ff4757';
            else color = '#1a1f2e';
            wheelCtx.beginPath();
            wheelCtx.arc(140, 140, 130, start, end);
            wheelCtx.lineTo(140, 140);
            wheelCtx.fillStyle = color;
            wheelCtx.fill();
            wheelCtx.save();
            wheelCtx.translate(140, 140);
            wheelCtx.rotate(start + anglePer / 2);
            wheelCtx.fillStyle = 'white';
            wheelCtx.font = 'bold 11px Arial';
            wheelCtx.fillText(i, 48, 6);
            wheelCtx.restore();
        }
    }

    async function loadBalance() {
        if(!tgId) return;
        let res = await fetch('/api/balance', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({telegram_id:tgId})});
        let data = await res.json();
        currentBalance = data.balance;
        document.getElementById('balance').innerText = currentBalance.toLocaleString();
    }

    async function updateBalance(amount) {
        if(!tgId) return;
        let res = await fetch('/api/update_balance', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({telegram_id:tgId, amount:amount})});
        let data = await res.json();
        currentBalance = data.balance;
        document.getElementById('balance').innerText = currentBalance.toLocaleString();
        return currentBalance;
    }

    // CRASH
    async function fetchState() {
        try {
            let res = await fetch('/api/crash_state');
            let data = await res.json();
            currentMult = data.multiplier;
            gameState = data.state;
            timerSec = data.timer;
            crashHistory = data.history;
            document.getElementById('currentMult').innerHTML = currentMult.toFixed(2) + 'x';
            document.getElementById('timerValue').innerHTML = timerSec;
            let historyDiv = document.getElementById('crashHistory');
            historyDiv.innerHTML = '';
            crashHistory.slice(0,8).forEach(p => {
                let col = p < 2 ? '#ff4755' : (p < 5 ? '#ffaa00' : '#4caf50');
                historyDiv.innerHTML += `<div class="history-crash-item" style="background:${col}33; color:${col}">${p.toFixed(2)}x</div>`;
            });
            let statusDiv = document.getElementById('crashStatus');
            let placeBtn = document.getElementById('placeBetBtn');
            let cashBtn = document.getElementById('cashoutBtn');
            if(gameState == 'betting') {
                statusDiv.innerHTML = '🎲 ПРИЁМ СТАВОК';
                statusDiv.className = 'crash-status status-betting';
                if(!hasBet) { placeBtn.style.display = 'block'; cashBtn.style.display = 'none'; }
            } else if(gameState == 'flying') {
                statusDiv.innerHTML = '✈️ ПОЛЁТ... ЗАБЕРИТЕ!';
                statusDiv.className = 'crash-status status-flying';
                if(hasBet && !hasCashedOut && myAutoCash > 0 && currentMult >= myAutoCash) await cashout();
                if(hasBet && !hasCashedOut) { placeBtn.style.display = 'none'; cashBtn.style.display = 'block'; }
                else { placeBtn.style.display = 'block'; cashBtn.style.display = 'none'; }
            } else {
                statusDiv.innerHTML = '💥 КРАШ!';
                statusDiv.className = 'crash-status status-crashed';
                placeBtn.style.display = 'block'; cashBtn.style.display = 'none';
            }
        } catch(e) {}
    }

    async function placeBet() {
        if(!tgId) { alert('Привяжите Telegram!'); return; }
        if(hasBet) { alert('У вас уже есть ставка!'); return; }
        if(gameState != 'betting') { alert('❌ СТАВКИ ТОЛЬКО МЕЖДУ РАУНДАМИ!'); return; }
        let bet = parseInt(document.getElementById('betAmount').value);
        if(bet < 10) { alert('Минимальная ставка 10 тяжек'); return; }
        if(bet > currentBalance) { alert('Не хватает тяжек! Баланс: ' + currentBalance.toLocaleString()); return; }
        let autoVal = parseFloat(document.getElementById('autoCash').value);
        if(autoVal < 1.01) autoVal = 0;
        let res = await fetch('/api/place_crash_bet', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({telegram_id:tgId, bet:bet, auto_cash:autoVal})});
        let data = await res.json();
        if(data.success) {
            await updateBalance(-bet);
            myBet = bet; myAutoCash = autoVal; hasBet = true; hasCashedOut = false;
            document.getElementById('betStatus').innerHTML = `✅ Ставка ${bet.toLocaleString()} тяжек принята!`;
            document.getElementById('placeBetBtn').style.display = 'none';
        } else { alert(data.message); }
    }

    async function cashout() {
        if(!hasBet || hasCashedOut) { alert('Нет активной ставки!'); return; }
        if(gameState != 'flying') { alert('Вывод только во время полёта!'); return; }
        let res = await fetch('/api/crash_cashout', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({telegram_id:tgId})});
        let data = await res.json();
        if(data.success) {
            await updateBalance(data.win_amount);
            hasCashedOut = true;
            document.getElementById('betStatus').innerHTML = `🎉 ВЫИГРЫШ! ${data.multiplier.toFixed(2)}x = ${data.win_amount.toLocaleString()} тяжек`;
            document.getElementById('placeBetBtn').style.display = 'block';
            document.getElementById('cashoutBtn').style.display = 'none';
            addHistory('КРАШ', myBet, data.win_amount - myBet, `${data.multiplier.toFixed(2)}x`);
            myBet = 0; hasBet = false;
        } else { alert(data.message); }
    }

    async function checkCrash() {
        if(!hasBet || hasCashedOut) return;
        let res = await fetch('/api/check_crash_result', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({telegram_id:tgId})});
        let data = await res.json();
        if(data.crashed) {
            document.getElementById('betStatus').innerHTML = `💀 КРАШ! -${myBet.toLocaleString()} тяжек`;
            document.getElementById('placeBetBtn').style.display = 'block';
            document.getElementById('cashoutBtn').style.display = 'none';
            addHistory('КРАШ', myBet, -myBet, `Краш ${data.crash_point.toFixed(2)}x`);
            myBet = 0; hasBet = false; hasCashedOut = false;
        }
    }

    // СЛОТЫ
    async function spinSlots() {
        if(isSpinning) return;
        let bet = parseInt(document.getElementById('slotsBet').value);
        if(bet < 10 || bet > currentBalance) { alert('Ошибка ставки! Минимум 10 тяжек'); return; }
        isSpinning = true;
        await updateBalance(-bet);
        for(let i = 0; i < 12; i++) {
            setTimeout(() => {
                if(i < 10) {
                    document.getElementById('slot1').innerText = symbols[Math.floor(Math.random() * symbols.length)];
                    document.getElementById('slot2').innerText = symbols[Math.floor(Math.random() * symbols.length)];
                    document.getElementById('slot3').innerText = symbols[Math.floor(Math.random() * symbols.length)];
                }
            }, i * 80);
        }
        setTimeout(async () => {
            let r1 = symbols[Math.floor(Math.random() * symbols.length)];
            let r2 = symbols[Math.floor(Math.random() * symbols.length)];
            let r3 = symbols[Math.floor(Math.random() * symbols.length)];
            document.getElementById('slot1').innerText = r1;
            document.getElementById('slot2').innerText = r2;
            document.getElementById('slot3').innerText = r3;
            let win = 0;
            if(r1 == r2 && r2 == r3) win = bet * symbolMultipliers[r1];
            else if(r1 == r2 || r2 == r3 || r1 == r3) win = bet * 2;
            if(win > 0) {
                await updateBalance(win);
                addHistory('СЛОТЫ', bet, win - bet, `${r1}${r2}${r3}`);
                alert('🏆 ПОБЕДА! +' + win.toLocaleString() + ' тяжек');
            } else {
                addHistory('СЛОТЫ', bet, -bet, `${r1}${r2}${r3}`);
                alert('❌ ПРОИГРЫШ! -' + bet.toLocaleString() + ' тяжек');
            }
            isSpinning = false;
        }, 1000);
    }

    // РУЛЕТКА
    function initRoulette() {
        let grid = document.getElementById('rouletteNumbers');
        grid.innerHTML = '';
        for(let i = 0; i <= 36; i++) {
            let btn = document.createElement('button');
            btn.className = 'num-btn';
            btn.innerText = i;
            btn.onclick = (function(num) {
                return function() {
                    document.querySelectorAll('.num-btn').forEach(b => b.classList.remove('selected'));
                    document.querySelectorAll('.bet-option').forEach(b => b.classList.remove('selected'));
                    btn.classList.add('selected');
                    selectedRouletteBet = 'number';
                    window.selectedNumber = num;
                };
            })(i);
            grid.appendChild(btn);
        }
        document.querySelectorAll('.bet-option').forEach(btn => {
            btn.onclick = function() {
                document.querySelectorAll('.bet-option').forEach(b => b.classList.remove('selected'));
                document.querySelectorAll('.num-btn').forEach(b => b.classList.remove('selected'));
                this.classList.add('selected');
                selectedRouletteBet = this.dataset.bet;
                window.selectedNumber = null;
            };
        });
    }

    async function spinRoulette() {
        if(!selectedRouletteBet && window.selectedNumber === null) { alert('Выберите ставку!'); return; }
        let bet = parseInt(document.getElementById('rouletteBet').value);
        if(bet < 10 || bet > currentBalance) { alert('Ошибка ставки!'); return; }
        await updateBalance(-bet);
        let result = Math.floor(Math.random() * 37);
        let win = 0;
        let winText = '';
        if(selectedRouletteBet == 'red' && redNumbers.includes(result)) { win = bet * 2; winText = 'Красное'; }
        else if(selectedRouletteBet == 'black' && blackNumbers.includes(result)) { win = bet * 2; winText = 'Чёрное'; }
        else if(selectedRouletteBet == 'green' && result === 0) { win = bet * 36; winText = 'Зелёное'; }
        else if(selectedRouletteBet == 'number' && window.selectedNumber === result) { win = bet * 36; winText = `Число ${result}`; }
        if(win > 0) {
            await updateBalance(win);
            addHistory('РУЛЕТКА', bet, win - bet, winText);
            alert('🎉 ПОБЕДА! +' + win.toLocaleString() + ' тяжек');
        } else {
            addHistory('РУЛЕТКА', bet, -bet, `Выпало ${result}`);
            alert('❌ ПРОИГРЫШ! -' + bet.toLocaleString() + ' тяжек');
        }
        drawWheel();
    }

    // МИНЫ
    function initMines() {
        let grid = document.getElementById('minesGrid');
        grid.innerHTML = '';
        for(let i = 0; i < 25; i++) {
            let cell = document.createElement('div');
            cell.className = 'mine-cell';
            cell.dataset.index = i;
            cell.innerHTML = '?';
            cell.onclick = () => revealMine(i);
            grid.appendChild(cell);
        }
        minesGame.active = false;
        document.getElementById('minesStatus').innerHTML = 'Нажмите "НОВАЯ ИГРА" чтобы начать';
    }

    async function startMines() {
        let bet = parseInt(document.getElementById('minesBet').value);
        if(bet < 10 || bet > currentBalance) { alert('Ошибка ставки!'); return; }
        minesGame = {
            active: true,
            bet: bet,
            totalCells: 25,
            mineCount: 5,
            revealed: new Array(25).fill(false),
            isMine: new Array(25).fill(false),
            multiplier: 1.0
        };
        let minesPlaced = 0;
        while(minesPlaced < 5) {
            let pos = Math.floor(Math.random() * 25);
            if(!minesGame.isMine[pos]) {
                minesGame.isMine[pos] = true;
                minesPlaced++;
            }
        }
        await updateBalance(-bet);
        let grid = document.getElementById('minesGrid');
        grid.innerHTML = '';
        for(let i = 0; i < 25; i++) {
            let cell = document.createElement('div');
            cell.className = 'mine-cell';
            cell.dataset.index = i;
            cell.innerHTML = '?';
            cell.onclick = () => revealMine(i);
            grid.appendChild(cell);
        }
        document.getElementById('minesStatus').innerHTML = `💰 Ставка: ${bet.toLocaleString()} тяжек | Множитель: 1.00x | Найдено мин: 0/${minesGame.mineCount}`;
    }

    async function revealMine(index) {
        if(!minesGame.active) { alert('Начните новую игру!'); return; }
        if(minesGame.revealed[index]) { alert('Эта клетка уже открыта!'); return; }
        if(minesGame.isMine[index]) {
            let cell = document.querySelector(`.mine-cell[data-index='${index}']`);
            cell.innerHTML = '💣';
            cell.classList.add('mine');
            addHistory('МИНЫ', minesGame.bet, -minesGame.bet, `Попалась мина!`);
            document.getElementById('minesStatus').innerHTML = `💣 МИНА! Вы проиграли ${minesGame.bet.toLocaleString()} тяжек`;
            minesGame.active = false;
            return;
        }
        minesGame.revealed[index] = true;
        let revealedCount = minesGame.revealed.filter(r => r === true).length;
        let safeCells = 25 - minesGame.mineCount;
        let multiplier = 1 + (revealedCount / safeCells) * 3;
        minesGame.multiplier = multiplier;
        let winAmount = Math.floor(minesGame.bet * multiplier);
        let cell = document.querySelector(`.mine-cell[data-index='${index}']`);
        cell.innerHTML = '💎';
        cell.classList.add('revealed');
        document.getElementById('minesStatus').innerHTML = `💰 Ставка: ${minesGame.bet.toLocaleString()} | Множитель: ${multiplier.toFixed(2)}x | Потенциальный выигрыш: ${winAmount.toLocaleString()} тяжек | Найдено мин: ${minesGame.revealed.filter(i => minesGame.isMine[i]).length}/${minesGame.mineCount}`;
        if(revealedCount === safeCells) {
            await updateBalance(winAmount);
            addHistory('МИНЫ', minesGame.bet, winAmount - minesGame.bet, `Победа! Множитель ${multiplier.toFixed(2)}x`);
            alert('🏆 ПОБЕДА! Вы открыли все безопасные клетки!');
            minesGame.active = false;
        }
    }

    function addHistory(game, bet, win, result) {
        let historyDiv = document.getElementById('historyList');
        let item = document.createElement('div');
        item.className = 'history-item';
        let winClass = win > 0 ? 'win-text' : 'lose-text';
        item.innerHTML = `<span>${game}</span><span>${bet.toLocaleString()}</span><span class="${winClass}">${win > 0 ? '+' + win.toLocaleString() : win.toLocaleString()}</span><span>${result}</span>`;
        historyDiv.insertBefore(item, historyDiv.firstChild);
        if(historyDiv.children.length > 15) historyDiv.removeChild(historyDiv.lastChild);
    }

    function setMaxBet() {
        if(currentBalance > 0) {
            if(document.getElementById('betAmount').offsetParent) document.getElementById('betAmount').value = currentBalance;
            if(document.getElementById('slotsBet').offsetParent) document.getElementById('slotsBet').value = currentBalance;
            if(document.getElementById('rouletteBet').offsetParent) document.getElementById('rouletteBet').value = currentBalance;
            if(document.getElementById('minesBet').offsetParent) document.getElementById('minesBet').value = currentBalance;
        }
    }

    function switchGame(game) {
        document.getElementById('crashGame').style.display = game == 'crash' ? 'block' : 'none';
        document.getElementById('slotsGame').style.display = game == 'slots' ? 'block' : 'none';
        document.getElementById('rouletteGame').style.display = game == 'roulette' ? 'block' : 'none';
        document.getElementById('minesGame').style.display = game == 'mines' ? 'block' : 'none';
        document.getElementById('promoGame').style.display = game == 'promo' ? 'block' : 'none';
        if(game == 'roulette') drawWheel();
        if(game == 'mines') initMines();
    }

    async function getBonus() {
        if(!tgId) { alert('Привяжите Telegram!'); return; }
        let res = await fetch('/api/get_bonus', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({telegram_id:tgId})});
        let data = await res.json();
        if(data.success) {
            await updateBalance(data.amount);
            alert(`🎉 +${data.amount.toLocaleString()} тяжек`);
        } else {
            alert(`⏰ ${data.message}`);
        }
    }

    document.querySelectorAll('.game-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.game-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            switchGame(btn.dataset.game);
        });
    });

    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            let bet = btn.dataset.bet;
            if(bet === 'max') {
                setMaxBet();
            } else {
                if(document.getElementById('betAmount').offsetParent) document.getElementById('betAmount').value = bet;
                if(document.getElementById('slotsBet').offsetParent) document.getElementById('slotsBet').value = bet;
                if(document.getElementById('rouletteBet').offsetParent) document.getElementById('rouletteBet').value = bet;
                if(document.getElementById('minesBet').offsetParent) document.getElementById('minesBet').value = bet;
            }
        });
    });

    document.getElementById('placeBetBtn').onclick = placeBet;
    document.getElementById('cashoutBtn').onclick = cashout;
    document.getElementById('slotsSpinBtn').onclick = spinSlots;
    document.getElementById('rouletteSpinBtn').onclick = spinRoulette;
    document.getElementById('minesNewGameBtn').onclick = startMines;
    document.getElementById('promoBonusBtn').onclick = getBonus;

    setInterval(fetchState, 300);
    setInterval(checkCrash, 500);
    if(tgId) loadBalance();
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

@app.route('/api/balance', methods=['POST'])
def api_balance():
    data = request.json
    tg_id = data.get('telegram_id')
    if not tg_id:
        return jsonify({'balance': 5000})
    return jsonify({'balance': get_balance(tg_id)})

@app.route('/api/update_balance', methods=['POST'])
def api_update_balance():
    data = request.json
    tg_id = data.get('telegram_id')
    amount = data.get('amount', 0)
    new_bal = update_balance(tg_id, amount)
    return jsonify({'balance': new_bal})

@app.route('/api/crash_state', methods=['GET'])
def crash_state():
    timer = 0
    if game_state == 'betting':
        timer = betting_timer
    return jsonify({
        'multiplier': current_multiplier,
        'state': game_state,
        'timer': timer,
        'history': crash_history[:10]
    })

@app.route('/api/place_crash_bet', methods=['POST'])
def place_crash_bet():
    global user_bets, game_state
    data = request.json
    tg_id = data.get('telegram_id')
    bet = data.get('bet', 0)
    auto_cash = data.get('auto_cash', 0)
    
    if game_state != 'betting':
        return jsonify({'success': False, 'message': 'Ставки только между раундами!'})
    if tg_id in user_bets:
        return jsonify({'success': False, 'message': 'У вас уже есть ставка!'})
    if get_balance(tg_id) < bet:
        return jsonify({'success': False, 'message': 'Недостаточно тяжек!'})
    
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

@app.route('/api/get_bonus', methods=['POST'])
def api_get_bonus():
    data = request.json
    tg_id = data.get('telegram_id')
    bonus = random.randint(100, 100000)
    update_balance(tg_id, bonus)
    return jsonify({'success': True, 'amount': bonus})
'''

@app.route('/')
def index():
    return WEB_HTML
