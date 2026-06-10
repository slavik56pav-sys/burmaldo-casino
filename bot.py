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

# ========== ПОДЫ VOOPOO ==========
XSLIM_PODS = ["XSLIM Pro", "XSLIM Nano", "XSLIM Air", "XSLIM Ultra", "XSLIM Max", "XSLIM Mini", "XSLIM Edge", "XSLIM Plus", "XSLIM Lite", "XSLIM Flex", "XSLIM Twist", "XSLIM Curve", "XSLIM Flat", "XSLIM Round", "XSLIM Square", "XSLIM 2.0", "XSLIM 3.0", "XSLIM X", "XSLIM S", "XSLIM R", "XSLIM Pro Max", "XSLIM Ultra Lite", "XSLIM Air Plus", "XSLIM Nano Pro", "XSLIM Flex Edge", "XSLIM Twist Pro", "XSLIM Curve Max", "XSLIM Flat Ultra", "XSLIM Round Plus", "XSLIM Square Pro", "XSLIM 2 Pro", "XSLIM 3 Ultra", "XSLIM X Pro", "XSLIM S Max", "XSLIM R Plus"]

VINCI_PODS = ["VINCI", "VINCI X", "VINCI Royal", "VINCI Spark", "VINCI Q", "VINCI Pod", "VINCI 2", "VINCI 3", "VINCI Pro", "VINCI Max", "VINCI Air", "VINCI Nano", "VINCI Ultra", "VINCI Flex", "VINCI Twist", "VINCI Edge", "VINCI Plus", "VINCI Lite", "VINCI X Pro", "VINCI X Max", "VINCI Royal Pro", "VINCI Spark Pro", "VINCI Q Max", "VINCI Pod 2", "VINCI 2 Pro", "VINCI 3 Max", "VINCI Pro Max", "VINCI Air Plus", "VINCI Nano Pro", "VINCI Ultra Max", "VINCI Flex Pro", "VINCI Twist Max", "VINCI Edge Pro", "VINCI Plus Max", "VINCI Lite Pro"]

ARGUS_PODS = ["ARGUS GT", "ARGUS XT", "ARGUS Air", "ARGUS Pod", "ARGUS Pro", "ARGUS 2", "ARGUS 3", "ARGUS Max", "ARGUS Ultra", "ARGUS Flex", "ARGUS G", "ARGUS P", "ARGUS M", "ARGUS Z", "ARGUS MT", "ARGUS GT 2", "ARGUS XT Pro", "ARGUS Air Max", "ARGUS Pod Pro", "ARGUS Pro Max", "ARGUS 2 Pro", "ARGUS 3 Max", "ARGUS Ultra Plus", "ARGUS Flex Edge", "ARGUS G Pro", "ARGUS P Max", "ARGUS M Plus", "ARGUS Z Pro", "ARGUS MT Max", "ARGUS GT Max", "ARGUS XT Ultra", "ARGUS Air Pro", "ARGUS Pod Max", "ARGUS Pro Ultra", "ARGUS 2 Max"]

DRAGX_PODS = ["DRAG X", "DRAG X Plus", "DRAG X Pro", "DRAG X Max", "DRAG X Ultra", "DRAG X 2", "DRAG X 3", "DRAG X Nano", "DRAG X Air", "DRAG X Flex", "DRAG X Pro Max", "DRAG X Ultra Plus", "DRAG X 2 Pro", "DRAG X 3 Max", "DRAG X Nano Pro", "DRAG X Air Plus", "DRAG X Flex Edge", "DRAG X Pro Ultra", "DRAG X Max Plus", "DRAG X 2 Ultra", "DRAG X 3 Pro", "DRAG X Nano Max", "DRAG X Air Pro", "DRAG X Flex Pro", "DRAG X Ultra Pro", "DRAG X Pro 2", "DRAG X Max 2", "DRAG X Plus 2", "DRAG X Air 2", "DRAG X Flex 2", "DRAG X Nano 2", "DRAG X Ultra 2", "DRAG X Pro 3", "DRAG X Max 3", "DRAG X Plus 3"]

# ========== РЕДКОСТИ ==========
POD_RARITIES = {
    'Шерпотреб': {'pods': XSLIM_PODS, 'chance': 35, 'price': 100, 'mining_rate': 1, 'emoji': '⬜', 'color': '#808080'},
    'Комонка': {'pods': VINCI_PODS, 'chance': 25, 'price': 250, 'mining_rate': 2, 'emoji': '🟢', 'color': '#00ff00'},
    'Редкий': {'pods': ARGUS_PODS, 'chance': 15, 'price': 500, 'mining_rate': 3, 'emoji': '🔵', 'color': '#0088ff'},
    'Епический': {'pods': DRAGX_PODS, 'chance': 10, 'price': 1000, 'mining_rate': 5, 'emoji': '🟣', 'color': '#aa00ff'}
}

def get_random_pod():
    rand = random.random() * 100
    cumulative = 0
    for rarity, data in POD_RARITIES.items():
        cumulative += data['chance']
        if rand <= cumulative:
            pod_name = random.choice(data['pods'])
            return {'name': pod_name, 'rarity': rarity, 'price': data['price'], 'mining_rate': data['mining_rate'], 'emoji': data['emoji']}
    return {'name': XSLIM_PODS[0], 'rarity': 'Шерпотреб', 'price': 100, 'mining_rate': 1, 'emoji': '⬜'}# ========== ПОДЫ (5-8 редкости) ==========
DRAGS_PODS = ["DRAG S", "DRAG S Plus", "DRAG S Pro", "DRAG S Max", "DRAG S Ultra", "DRAG S 2", "DRAG S 3", "DRAG S Nano", "DRAG S Air", "DRAG S Flex", "DRAG S Pro Max", "DRAG S Ultra Plus", "DRAG S 2 Pro", "DRAG S 3 Max", "DRAG S Nano Pro", "DRAG S Air Plus", "DRAG S Flex Edge", "DRAG S Pro Ultra", "DRAG S Max Plus", "DRAG S 2 Ultra", "DRAG S 3 Pro", "DRAG S Nano Max", "DRAG S Air Pro", "DRAG S Flex Pro", "DRAG S Ultra Pro", "DRAG S Pro 2", "DRAG S Max 2", "DRAG S Plus 2", "DRAG S Air 2", "DRAG S Flex 2", "DRAG S Nano 2", "DRAG S Ultra 2", "DRAG S Pro 3", "DRAG S Max 3", "DRAG S Plus 3"]

LEGENDARY_PODS = ["DRAG 4", "DRAG 5", "DRAG 4 Pro", "DRAG 5 Pro", "DRAG 4 Max", "DRAG 5 Ultra", "DRAG 4 Plus", "DRAG 5 Plus", "DRAG 4 Titan", "DRAG 5 Titan", "DRAG 4 X", "DRAG 5 X", "DRAG 4 S", "DRAG 5 S", "DRAG 4 R", "DRAG 5 R", "DRAG 4 GT", "DRAG 5 GT", "DRAG 4 Ultimate", "DRAG 5 Ultimate", "DRAG 4 Legend", "DRAG 5 Legend", "DRAG 4 Mythic", "DRAG 5 Mythic", "DRAG 4 Godly", "DRAG 5 Godly", "DRAG 4 Eternal", "DRAG 5 Eternal", "DRAG 4 Infinity", "DRAG 5 Infinity", "DRAG 4 Zero", "DRAG 5 Zero", "DRAG 4 Prime", "DRAG 5 Prime", "DRAG 4 Omega"]

CHROMATIC_PODS = ["DRAG 3", "DRAG 3 Pro", "DRAG 3 Max", "DRAG 3 Ultra", "DRAG 3 Plus", "DRAG 3 X", "DRAG 3 S", "DRAG 3 R", "DRAG 3 GT", "DRAG 3 Titan", "DRAG 3 Legend", "DRAG 3 Mythic", "DRAG 3 Godly", "DRAG 3 Eternal", "DRAG 3 Infinity", "DRAG 3 Chroma", "DRAG 3 Prism", "DRAG 3 Spectrum", "DRAG 3 Rainbow", "DRAG 3 Aurora", "DRAG 3 Galaxy", "DRAG 3 Nebula", "DRAG 3 Star", "DRAG 3 Comet", "DRAG 3 Meteor", "DRAG 3 Eclipse", "DRAG 3 Solar", "DRAG 3 Lunar", "DRAG 3 Stellar", "DRAG 3 Cosmic", "DRAG 3 Void", "DRAG 3 Quantum", "DRAG 3 Atomic", "DRAG 3 Plasma", "DRAG 3 Photon"]

ARCANA_PODS = ["XROS", "XROS 2", "XROS 3", "XROS 4", "XROS Pro", "XROS Nano", "XROS Mini", "XROS Air", "XROS Ultra", "XROS Max", "XROS X", "XROS S", "XROS R", "XROS GT", "XROS Titan", "XROS Legend", "XROS Mythic", "XROS Godly", "XROS Eternal", "XROS Infinity", "XROS Arcana", "XROS Mystic", "XROS Oracle", "XROS Prophet", "XROS Seer", "XROS Diviner", "XROS Sage", "XROS Wizard", "XROS Sorcerer", "XROS Enchanter", "XROS Magus", "XROS Archmage", "XROS Hierophant", "XROS Ascendant", "XROS Transcendent"]

POD_RARITIES.update({
    'Мифический': {'pods': DRAGS_PODS, 'chance': 7, 'price': 2500, 'mining_rate': 8, 'emoji': '🟠', 'color': '#ff8800'},
    'Легендарный': {'pods': LEGENDARY_PODS, 'chance': 4, 'price': 5000, 'mining_rate': 12, 'emoji': '🔴', 'color': '#ff4400'},
    'Хроматический': {'pods': CHROMATIC_PODS, 'chance': 2, 'price': 10000, 'mining_rate': 20, 'emoji': '💜', 'color': '#ff00ff'},
    'Аркана': {'pods': ARCANA_PODS, 'chance': 2, 'price': 25000, 'mining_rate': 35, 'emoji': '👑', 'color': '#ffd700'}
})

# ========== БАЗА ДАННЫХ ==========
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
        balance INTEGER DEFAULT 5000,
        last_daily_time TIMESTAMP,
        games_played INTEGER DEFAULT 0,
        total_won INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0
    )''')
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
        drop_chance_level INTEGER DEFAULT 0,
        cooldown_level INTEGER DEFAULT 0,
        rarity_luck_level INTEGER DEFAULT 0
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

def upgrade_pod_chance(current_level, rarity):
    base = {'Шерпотреб':80, 'Комонка':70, 'Редкий':60, 'Епический':50, 'Мифический':40, 'Легендарный':30, 'Хроматический':20, 'Аркана':10}
    chance = base.get(rarity, 50) / current_level
    return max(5, min(95, chance))

UPGRADE_COSTS = {'drop_chance':[0,10000,20000,35000,55000,80000,110000,150000,200000,260000,330000],
                 'cooldown':[0,5000,12000,22000,35000,52000,73000,98000,128000,163000,205000],
                 'rarity_luck':[0,8000,18000,32000,50000,72000,98000,128000,162000,200000,242000]}

def get_user_upgrades(user_id):
    conn = get_db()
    upgrades = conn.execute("SELECT * FROM user_upgrades WHERE user_id = ?", (str(user_id),)).fetchone()
    conn.close()
    if not upgrades:
        return {'drop_chance_level':0, 'cooldown_level':0, 'rarity_luck_level':0}
    return upgrades

def get_drop_chance_bonus(level): return min(level * 4, 40)
def get_cooldown_reduction(level): return min(level * 2, 20)
def get_rarity_luck_bonus(level): return min(level * 3, 30)# ========== CRASH GAME ==========
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
    commands = [BotCommand("start","Главное меню"), BotCommand("casino","Открыть казино"),
                BotCommand("daily","Ежедневный под"), BotCommand("mypods","Мои поды"),
                BotCommand("balance","Баланс"), BotCommand("mine","Майнинг"),
                BotCommand("shop","Магазин"), BotCommand("market","Рынок"), BotCommand("help","Помощь")]
    bot.set_my_commands(commands)
    bot.set_chat_menu_button(menu_button=MenuButtonCommands())

setup_menu()

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    if not get_user(user_id): create_user(user_id, username)
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("🎰 КАЗИНО"), KeyboardButton("🎁 DAILY"))
    keyboard.add(KeyboardButton("📦 МОИ ПОДЫ"), KeyboardButton("⛏️ МАЙНИНГ"))
    keyboard.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("🏪 МАГАЗИН"))
    keyboard.add(KeyboardButton("🏪 РЫНОК"), KeyboardButton("❓ ПОМОЩЬ"))
    bot.send_message(message.chat.id, f"🐐 БУРМАЛДАТОЕ CASINO\n\n💰 Тяжки: {get_balance(user_id):,}\n\nВыберите действие:", reply_markup=keyboard)

@bot.message_handler(commands=['daily'])
def daily_pod(message):
    user_id = message.from_user.id
    last_daily = get_user(user_id)['last_daily_time'] if get_user(user_id) else datetime.now() - timedelta(hours=24)
    last_daily = datetime.fromisoformat(last_daily) if isinstance(last_daily, str) else last_daily
    now = datetime.now()
    upgrades = get_user_upgrades(user_id)
    cooldown_hours = 24 - get_cooldown_reduction(upgrades['cooldown_level'])
    if (now - last_daily).total_seconds() < cooldown_hours * 3600:
        remaining = int((cooldown_hours * 3600 - (now - last_daily).total_seconds()) / 3600)
        bot.reply_to(message, f"⏰ Следующий под через {remaining} часов!"); return
    drop_bonus = get_drop_chance_bonus(upgrades['drop_chance_level'])
    rand = random.random() * 100
    cum = 0
    selected = None
    for rarity, data in POD_RARITIES.items():
        cum += data['chance'] + (drop_bonus if rarity != 'Аркана' else 0)
        if rand <= cum: selected = rarity; break
    if not selected: selected = 'Шерпотреб'
    pod_data = POD_RARITIES[selected]
    pod_name = random.choice(pod_data['pods'])
    add_pod_to_user(user_id, pod_name, selected, pod_data['mining_rate'])
    conn = get_db()
    conn.execute("UPDATE users SET last_daily_time = ? WHERE telegram_id = ?", (now.isoformat(), str(user_id)))
    conn.commit(); conn.close()
    bot.reply_to(message, f"🎁 ВЫ ПОЛУЧИЛИ ПОД!\n\n{pod_data['emoji']} {pod_name}\n⭐ {selected}\n💰 {pod_data['price']} тяжек\n⛏️ {pod_data['mining_rate']} тяжек/час")

@bot.message_handler(commands=['mypods'])
def my_pods(message):
    user_id = message.from_user.id
    pods = get_user_pods(user_id)
    if not pods: bot.reply_to(message, "📦 У вас нет подов! Используйте /daily"); return
    text = "📦 ВАША КОЛЛЕКЦИЯ ПОДОВ\n\n"
    for pod in pods:
        rdata = POD_RARITIES.get(pod['rarity'], {})
        text += f"🆔 {pod['id']} | {rdata.get('emoji','📟')} {pod['pod_name']}\n   ⭐ {pod['rarity']} | Ур.{pod['level']} | ⛏️ {pod['mining_rate']} тяжек/ч\n\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['balance'])
def balance_cmd(message):
    bot.reply_to(message, f"💰 ТЯЖКИ: {get_balance(message.from_user.id):,}")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, "❓ ПОМОЩЬ\n\n/start - Главное меню\n/casino - Открыть казино\n/daily - Ежедневный под\n/mypods - Мои поды\n/balance - Баланс\n/mine - Майнинг\n/shop - Магазин\n/market - Рынок")# ========== КНОПКИ ==========
@bot.message_handler(func=lambda m: m.text == "🎰 КАЗИНО")
def casino_button(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎰 ВОЙТИ В КАЗИНО", url=f"{WEB_URL}?tg_id={user_id}&tg_name={username}"))
    bot.send_message(message.chat.id, "Нажмите на кнопку:", reply_markup=kb)

@bot.message_handler(commands=['casino'])
def casino_cmd(message): casino_button(message)

@bot.message_handler(func=lambda m: m.text == "🎁 DAILY")
def daily_button(message): daily_pod(message)

@bot.message_handler(func=lambda m: m.text == "📦 МОИ ПОДЫ")
def mypods_button(message): my_pods(message)

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def balance_button(message): balance_cmd(message)

@bot.message_handler(func=lambda m: m.text == "❓ ПОМОЩЬ")
def help_button(message): help_cmd(message)

# ========== CRASH API ==========
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

@app.route('/api/balance', methods=['POST'])
def api_balance():
    data = request.json
    tg_id = data.get('telegram_id')
    return jsonify({'balance': get_balance(tg_id) if tg_id else 5000})

@app.route('/api/update_balance', methods=['POST'])
def api_update_balance():
    data = request.json
    tg_id = data.get('telegram_id')
    amount = data.get('amount', 0)
    return jsonify({'balance': update_balance(tg_id, amount) if tg_id else 5000})

@app.route('/api/get_bonus', methods=['POST'])
def api_get_bonus():
    data = request.json
    tg_id = data.get('telegram_id')
    bonus = random.randint(100, 100000)
    update_balance(tg_id, bonus)
    return jsonify({'success': True, 'amount': bonus})# ========== МАЙНИНГ ==========
@bot.message_handler(commands=['mine'])
def mine_command(message):
    args = message.text.split()
    user_id = message.from_user.id
    if len(args) < 2:
        bot.reply_to(message, "⛏️ /mine start ID - начать\n/mine claim - забрать\n/mine stop - остановить")
        return
    action = args[1]
    if action == 'start':
        if len(args) < 3: bot.reply_to(message, "❌ Укажите ID: /mine start 1"); return
        pod_id = int(args[2])
        pod = get_pod_by_id(pod_id)
        if not pod or pod['user_id'] != str(user_id): bot.reply_to(message, "❌ Под не найден!"); return
        conn = get_db()
        existing = conn.execute("SELECT * FROM active_mining WHERE user_id = ?", (str(user_id),)).fetchone()
        if existing: bot.reply_to(message, "❌ У вас уже активен майнинг!"); conn.close(); return
        conn.execute("INSERT INTO active_mining (user_id, pod_id, start_time, last_claim) VALUES (?, ?, ?, ?)",
                     (str(user_id), pod_id, datetime.now().isoformat(), datetime.now().isoformat()))
        conn.commit(); conn.close()
        bot.reply_to(message, f"✅ МАЙНИНГ ЗАПУЩЕН!\n{pod['pod_name']}\n⛏️ {pod['mining_rate']} тяжек/час")
    elif action == 'claim':
        conn = get_db()
        mining = conn.execute("SELECT * FROM active_mining WHERE user_id = ?", (str(user_id),)).fetchone()
        if not mining: bot.reply_to(message, "❌ Нет активного майнинга!"); conn.close(); return
        pod = get_pod_by_id(mining['pod_id'])
        last_claim = datetime.fromisoformat(mining['last_claim'])
        now = datetime.now()
        hours = (now - last_claim).total_seconds() / 3600
        earned = int(hours * pod['mining_rate'])
        if earned > 0:
            update_balance(user_id, earned)
            conn.execute("UPDATE active_mining SET last_claim = ? WHERE user_id = ?", (now.isoformat(), str(user_id)))
            conn.commit()
            bot.reply_to(message, f"⛏️ ВЫ ПОЛУЧИЛИ {earned} ТЯЖЕК!")
        else: bot.reply_to(message, "⏳ Майнинг ещё не принёс тяжки!")
        conn.close()
    elif action == 'stop':
        conn = get_db()
        conn.execute("DELETE FROM active_mining WHERE user_id = ?", (str(user_id),))
        conn.commit(); conn.close()
        bot.reply_to(message, "✅ МАЙНИНГ ОСТАНОВЛЕН")

# ========== ПРОДАЖА ПОДА ==========
@bot.message_handler(commands=['sell'])
def sell_pod(message):
    args = message.text.split()
    user_id = message.from_user.id
    if len(args) < 2: bot.reply_to(message, "❌ /sell pod_id"); return
    pod_id = int(args[1])
    pod = get_pod_by_id(pod_id)
    if not pod or pod['user_id'] != str(user_id): bot.reply_to(message, "❌ Под не найден!"); return
    price = POD_RARITIES.get(pod['rarity'], {}).get('price', 100)
    delete_pod(pod_id)
    update_balance(user_id, price)
    bot.reply_to(message, f"✅ ПРОДАНО!\n{pod['pod_name']}\n💰 +{price} ТЯЖЕК")# ========== АПГРЕЙД ПОДА ==========
@bot.message_handler(commands=['upgrade'])
def upgrade_pod(message):
    args = message.text.split()
    user_id = message.from_user.id
    if len(args) < 2: bot.reply_to(message, "❌ /upgrade pod_id"); return
    pod_id = int(args[1])
    pod = get_pod_by_id(pod_id)
    if not pod or pod['user_id'] != str(user_id): bot.reply_to(message, "❌ Под не найден!"); return
    cost = pod['level'] * 100
    balance = get_balance(user_id)
    if balance < cost: bot.reply_to(message, f"❌ Нужно {cost} тяжек!"); return
    chance = upgrade_pod_chance(pod['level'], pod['rarity'])
    if random.random() * 100 < chance:
        new_rate = int(pod['mining_rate'] * 1.5)
        conn = get_db()
        conn.execute("UPDATE user_pods SET level = level + 1, mining_rate = ? WHERE id = ?", (new_rate, pod_id))
        conn.commit(); conn.close()
        update_balance(user_id, -cost)
        bot.reply_to(message, f"✅ АПГРЕЙД УСПЕШЕН!\n{pod['pod_name']}\n📈 Уровень {pod['level']+1}\n⛏️ {new_rate} тяжек/час")
    else:
        update_balance(user_id, -cost)
        bot.reply_to(message, f"❌ АПГРЕЙД НЕ УДАЛСЯ!\nШанс {chance:.1f}%")

# ========== РЫНОК ==========
@bot.message_handler(commands=['list'])
def list_pod(message):
    args = message.text.split()
    user_id = message.from_user.id
    if len(args) < 3: bot.reply_to(message, "❌ /list pod_id цена"); return
    pod_id = int(args[1])
    price = int(args[2])
    pod = get_pod_by_id(pod_id)
    if not pod or pod['user_id'] != str(user_id): bot.reply_to(message, "❌ Под не найден!"); return
    conn = get_db()
    conn.execute("UPDATE user_pods SET is_listed = 1, list_price = ? WHERE id = ?", (price, pod_id))
    conn.execute("INSERT INTO market_listings (seller_id, pod_id, price, listed_at) VALUES (?, ?, ?, ?)",
                 (str(user_id), pod_id, price, datetime.now().isoformat()))
    conn.commit(); conn.close()
    bot.reply_to(message, f"✅ ПОД ВЫСТАВЛЕН НА РЫНОК!\n{pod['pod_name']}\n💰 Цена: {price} тяжек")

@bot.message_handler(commands=['market'])
def market_cmd(message):
    conn = get_db()
    listings = conn.execute('''SELECT m.id, m.price, m.seller_id, u.username, p.pod_name, p.rarity 
        FROM market_listings m JOIN user_pods p ON m.pod_id = p.id 
        LEFT JOIN users u ON m.seller_id = u.telegram_id 
        WHERE m.seller_id != ? AND p.is_listed = 1 ORDER BY m.listed_at DESC''', (str(message.from_user.id),)).fetchall()
    conn.close()
    if not listings: bot.reply_to(message, "🏪 РЫНОК ПУСТ"); return
    text = "🏪 ВТОРИЧНЫЙ РЫНОК\n\n"
    for l in listings[:20]:
        emoji = POD_RARITIES.get(l['rarity'], {}).get('emoji', '📟')
        text += f"🆔 {l['id']} | {emoji} {l['pod_name']}\n   ⭐ {l['rarity']} | 💰 {l['price']} тяжек\n\n"
    text += "💡 Купить: /buy listing_id"
    bot.reply_to(message, text)

@bot.message_handler(commands=['buy'])
def buy_pod(message):
    args = message.text.split()
    user_id = message.from_user.id
    if len(args) < 2: bot.reply_to(message, "❌ /buy listing_id"); return
    listing_id = int(args[1])
    conn = get_db()
    listing = conn.execute('''SELECT m.*, p.pod_name, p.rarity FROM market_listings m JOIN user_pods p ON m.pod_id = p.id WHERE m.id = ?''', (listing_id,)).fetchone()
    if not listing: bot.reply_to(message, "❌ Объявление не найдено!"); conn.close(); return
    if listing['seller_id'] == str(user_id): bot.reply_to(message, "❌ Нельзя купить свой под!"); conn.close(); return
    balance = get_balance(user_id)
    if balance < listing['price']: bot.reply_to(message, f"❌ Нужно {listing['price']} тяжек!"); conn.close(); return
    conn.execute("UPDATE user_pods SET user_id = ?, is_listed = 0, list_price = 0 WHERE id = ?", (str(user_id), listing['pod_id']))
    conn.execute("DELETE FROM market_listings WHERE id = ?", (listing_id,))
    update_balance(listing['seller_id'], listing['price'])
    update_balance(user_id, -listing['price'])
    conn.commit(); conn.close()
    bot.reply_to(message, f"✅ ПОД КУПЛЕН!\n{listing['pod_name']}\n💰 -{listing['price']} тяжек")# ========== МАГАЗИН УЛУЧШЕНИЙ ==========
@bot.message_handler(commands=['shop'])
def shop_cmd(message):
    user_id = message.from_user.id
    upgrades = get_user_upgrades(user_id)
    balance = get_balance(user_id)
    text = f"🏪 МАГАЗИН УЛУЧШЕНИЙ\n\n💰 Тяжек: {balance:,}\n\n"
    text += f"🎲 Шанс выпадения: ур.{upgrades['drop_chance_level']}/10\n"
    text += f"⏱️ Перезарядка: ур.{upgrades['cooldown_level']}/10\n"
    text += f"🍀 Удача: ур.{upgrades['rarity_luck_level']}/10\n\n"
    text += f"/drop_chance - {UPGRADE_COSTS['drop_chance'][upgrades['drop_chance_level']+1] if upgrades['drop_chance_level']<10 else 'MAX'} тяжек\n"
    text += f"/cooldown - {UPGRADE_COSTS['cooldown'][upgrades['cooldown_level']+1] if upgrades['cooldown_level']<10 else 'MAX'} тяжек\n"
    text += f"/luck - {UPGRADE_COSTS['rarity_luck'][upgrades['rarity_luck_level']+1] if upgrades['rarity_luck_level']<10 else 'MAX'} тяжек"
    bot.reply_to(message, text)

@bot.message_handler(commands=['drop_chance'])
def buy_drop(message):
    user_id = message.from_user.id
    upgrades = get_user_upgrades(user_id)
    level = upgrades['drop_chance_level']
    if level >= 10: bot.reply_to(message, "❌ Максимальный уровень!"); return
    cost = UPGRADE_COSTS['drop_chance'][level + 1]
    if get_balance(user_id) < cost: bot.reply_to(message, f"❌ Нужно {cost} тяжек!"); return
    update_balance(user_id, -cost)
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO user_upgrades (user_id, drop_chance_level) VALUES (?, ?)", (str(user_id), level + 1))
    conn.commit(); conn.close()
    bot.reply_to(message, f"✅ Шанс выпадения улучшен до {level + 1}/10!")

@bot.message_handler(commands=['cooldown'])
def buy_cooldown(message):
    user_id = message.from_user.id
    upgrades = get_user_upgrades(user_id)
    level = upgrades['cooldown_level']
    if level >= 10: bot.reply_to(message, "❌ Максимальный уровень!"); return
    cost = UPGRADE_COSTS['cooldown'][level + 1]
    if get_balance(user_id) < cost: bot.reply_to(message, f"❌ Нужно {cost} тяжек!"); return
    update_balance(user_id, -cost)
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO user_upgrades (user_id, cooldown_level) VALUES (?, ?)", (str(user_id), level + 1))
    conn.commit(); conn.close()
    bot.reply_to(message, f"✅ Перезарядка улучшена до {level + 1}/10!")

@bot.message_handler(commands=['luck'])
def buy_luck(message):
    user_id = message.from_user.id
    upgrades = get_user_upgrades(user_id)
    level = upgrades['rarity_luck_level']
    if level >= 10: bot.reply_to(message, "❌ Максимальный уровень!"); return
    cost = UPGRADE_COSTS['rarity_luck'][level + 1]
    if get_balance(user_id) < cost: bot.reply_to(message, f"❌ Нужно {cost} тяжек!"); return
    update_balance(user_id, -cost)
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO user_upgrades (user_id, rarity_luck_level) VALUES (?, ?)", (str(user_id), level + 1))
    conn.commit(); conn.close()
    bot.reply_to(message, f"✅ Удача улучшена до {level + 1}/10!")# ========== АДМИН-КОМАНДЫ ==========
@bot.message_handler(commands=['addmoney'])
def add_money(message):
    if not is_admin(message.from_user.id): return
    try:
        parts = message.text.split()
        if len(parts) != 3: bot.reply_to(message, "❌ /addmoney @user 1000"); return
        user_input = parts[1]; amount = int(parts[2]); tg_id = None
        if user_input.startswith('@'):
            conn = get_db()
            user = conn.execute("SELECT telegram_id FROM users WHERE username LIKE ?", (f'%{user_input[1:]}%',)).fetchone()
            conn.close()
            if user: tg_id = user['telegram_id']
        else: tg_id = user_input
        if not tg_id: bot.reply_to(message, "❌ Пользователь не найден!"); return
        new_balance = update_balance(tg_id, amount)
        bot.reply_to(message, f"✅ Выдано {amount:,} тяжек\n💰 Новый баланс: {new_balance:,}")
        try: bot.send_message(int(tg_id), f"🎉 АДМИН ВЫДАЛ ВАМ {amount:,} тяжек!\n💰 Новый баланс: {new_balance:,}")
        except: pass
    except: bot.reply_to(message, "❌ Ошибка!")

@bot.message_handler(commands=['givepod'])
def give_pod(message):
    if not is_admin(message.from_user.id): return
    try:
        parts = message.text.split()
        if len(parts) < 2: bot.reply_to(message, "❌ /givepod @user"); return
        user_input = parts[1]; tg_id = None
        if user_input.startswith('@'):
            conn = get_db()
            user = conn.execute("SELECT telegram_id FROM users WHERE username LIKE ?", (f'%{user_input[1:]}%',)).fetchone()
            conn.close()
            if user: tg_id = user['telegram_id']
        else: tg_id = user_input
        if not tg_id: bot.reply_to(message, "❌ Пользователь не найден!"); return
        pod = get_random_pod()
        add_pod_to_user(tg_id, pod['name'], pod['rarity'], pod['mining_rate'])
        bot.reply_to(message, f"✅ Выдан под {pod['name']} ({pod['rarity']})")
    except: bot.reply_to(message, "❌ Ошибка!")

@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if not is_admin(message.from_user.id): return
    try:
        parts = message.text.split()
        if len(parts) < 2: bot.reply_to(message, "❌ /addadmin @user"); return
        user_input = parts[1]; tg_id = None
        if user_input.startswith('@'):
            conn = get_db()
            user = conn.execute("SELECT telegram_id FROM users WHERE username LIKE ?", (f'%{user_input[1:]}%',)).fetchone()
            conn.close()
            if user: tg_id = user['telegram_id']
        else: tg_id = user_input
        if not tg_id: bot.reply_to(message, "❌ Пользователь не найден!"); return
        make_admin(tg_id)
        bot.reply_to(message, f"✅ Админ добавлен!")
        try: bot.send_message(int(tg_id), f"👑 ВАМ ВЫДАНЫ ПРАВА АДМИНИСТРАТОРА!")
        except: pass
    except: bot.reply_to(message, "❌ Ошибка!")# ========== ВЕБ-СЕРВЕР ==========
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Бурмалдатое Casino</title>
    <style>*{margin:0;padding:0;box-sizing:border-box;}body{background:radial-gradient(ellipse at 20%30%,#0a0f1e,#05080f);font-family:Segoe UI,sans-serif;padding:16px;color:#fff;}.container{max-width:480px;margin:0 auto;background:rgba(8,12,25,0.85);backdrop-filter:blur(15px);border:1px solid rgba(255,215,0,0.3);border-radius:28px;overflow:hidden;}.header{background:linear-gradient(135deg,#1a1f2e,#0d1225);padding:20px;text-align:center;border-bottom:2px solid #ffd700;}.title{font-size:22px;font-weight:bold;background:linear-gradient(45deg,#ffd700,#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}.balance-box{background:rgba(0,0,0,0.5);border-radius:20px;padding:12px;margin-top:12px;}.balance-amount{font-size:36px;font-weight:bold;color:#ffd700;}.game-nav{display:grid;grid-template-columns:repeat(5,1fr);gap:5px;padding:15px;background:rgba(0,0,0,0.3);}.game-btn{background:rgba(255,255,255,0.08);border:none;padding:12px 5px;border-radius:16px;color:#aaa;font-size:12px;cursor:pointer;text-align:center;}.game-btn.active{background:linear-gradient(135deg,#ffd700,#ff8c00);color:#000;}.game-area{padding:20px;}.crash-multiplier{font-size:64px;text-align:center;color:#ffd700;margin:20px 0;}.bet-input{width:100%;background:rgba(0,0,0,0.5);border:1px solid #ffd700;padding:14px;border-radius:16px;color:#fff;font-size:18px;text-align:center;margin-bottom:12px;}.bet-presets{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px;}.preset-btn{background:rgba(255,255,255,0.08);border:none;padding:10px;border-radius:12px;color:#ffd700;cursor:pointer;}.action-btn{width:100%;background:linear-gradient(135deg,#ffd700,#ff8c00);border:none;padding:16px;border-radius:20px;font-size:18px;font-weight:bold;color:#000;cursor:pointer;}.auto-cash-row{display:flex;align-items:center;justify-content:space-between;background:rgba(0,0,0,0.3);padding:12px;border-radius:16px;margin-bottom:16px;}.auto-cash-input{background:rgba(0,0,0,0.5);border:1px solid #ffd700;padding:8px;color:#ffd700;width:80px;text-align:center;}.slots-reels{display:flex;justify-content:center;gap:15px;margin:30px 0;}.slot-reel{width:85px;height:85px;background:rgba(0,0,0,0.6);border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:52px;border:2px solid #ffd700;}.history-section{padding:15px;border-top:1px solid rgba(255,215,0,0.2);max-height:160px;overflow-y:auto;}.history-item{background:rgba(255,255,255,0.04);padding:8px;margin:4px 0;font-size:11px;display:flex;justify-content:space-between;}.win-text{color:#4caf50;}.lose-text{color:#ff4757;}.bet-status{text-align:center;margin-top:12px;font-size:12px;color:#aaa;}@media(max-width:480px){.slot-reel{width:65px;height:65px;font-size:40px;}.crash-multiplier{font-size:48px;}}</style></head>
    <body>
    <div class="container">
        <div class="header"><div class="title">🐐 БУРМАЛДАТОЕ CASINO 🐐</div><div class="balance-box"><div>ТЯЖКИ:</div><div class="balance-amount" id="balance">0</div></div></div>
        <div class="game-nav"><button class="game-btn active" data-game="crash">💥 КРАШ</button><button class="game-btn" data-game="slots">🎰 СЛОТЫ</button><button class="game-btn" data-game="promo">🎁 ПРОМО</button></div>
        <div class="game-area" id="gameArea">
            <div id="crashGame"><div class="crash-multiplier" id="currentMult">1.00x</div><div class="bet-section"><input type="number" id="betAmount" class="bet-input" placeholder="СТАВКА" value="100"><div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div><div class="auto-cash-row"><span>🤖 АВТО-ВЫВОД (x):</span><input type="number" id="autoCash" class="auto-cash-input" value="2.00" step="0.5"></div><button class="action-btn" id="placeBetBtn">💰 СДЕЛАТЬ СТАВКУ</button><button class="action-btn" id="cashoutBtn" style="display:none">✅ ЗАБРАТЬ</button><div class="bet-status" id="betStatus"></div></div></div>
            <div id="slotsGame" style="display:none"><div class="slots-reels"><div class="slot-reel" id="slot1">🍒</div><div class="slot-reel" id="slot2">🍋</div><div class="slot-reel" id="slot3">🍊</div></div><div class="bet-section"><input type="number" id="slotsBet" class="bet-input" placeholder="СТАВКА" value="100"><div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div><button class="action-btn" id="slotsSpinBtn">🎰 КРУТИТЬ</button></div></div>
            <div id="promoGame" style="display:none"><div style="text-align:center;padding:40px;"><div style="font-size:64px;">🎁</div><button class="action-btn" id="promoBonusBtn">🎁 ПОЛУЧИТЬ БОНУС</button></div></div>
        </div>
        <div class="history-section"><div class="history-title">📜 ИСТОРИЯ ИГР</div><div id="historyList"></div></div>
    </div>
    <script>    const urlParams=new URLSearchParams(window.location.search);let tgId=urlParams.get("tg_id");let balance=0,myBet=0,myAutoCash=2.00,hasBet=false,hasCashedOut=false;let currentMult=1.00,gameState="betting",timerSec=10,crashHistory=[];let isSpinning=false;const symbols=["🍒","🍋","🍊","🔔","💎","7️⃣"];const symbolMultipliers={"🍒":2,"🍋":3,"🍊":5,"🔔":7,"💎":10,"7️⃣":20};setInterval(()=>{document.querySelectorAll(".multiplier-item").forEach(el=>{el.innerText=(Math.random()*3+0.5).toFixed(2)+"x";});},4000);async function loadBalance(){if(!tgId)return;let res=await fetch("/api/balance",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({telegram_id:tgId})});let data=await res.json();balance=data.balance;document.getElementById("balance").innerText=balance.toLocaleString();}async function updateBalance(amount){if(!tgId)return;let res=await fetch("/api/update_balance",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({telegram_id:tgId,amount:amount})});let data=await res.json();balance=data.balance;document.getElementById("balance").innerText=balance.toLocaleString();return balance;}async function fetchState(){let res=await fetch("/api/crash_state");let data=await res.json();currentMult=data.multiplier;gameState=data.state;timerSec=data.timer;crashHistory=data.history;document.getElementById("currentMult").innerHTML=currentMult.toFixed(2)+"x";let placeBtn=document.getElementById("placeBetBtn"),cashBtn=document.getElementById("cashoutBtn");if(gameState=="betting"){if(!hasBet){placeBtn.style.display="block";cashBtn.style.display="none";}}else if(gameState=="flying"){if(hasBet&&!hasCashedOut&&myAutoCash>0&&currentMult>=myAutoCash)await cashout();if(hasBet&&!hasCashedOut){placeBtn.style.display="none";cashBtn.style.display="block";}else{placeBtn.style.display="block";cashBtn.style.display="none";}}else{placeBtn.style.display="block";cashBtn.style.display="none";}}async function placeBet(){if(!tgId){alert("Привяжите Telegram!");return;}if(hasBet){alert("У вас уже есть ставка!");return;}if(gameState!="betting"){alert("Ставки только между раундами!");return;}let bet=parseInt(document.getElementById("betAmount").value);if(bet<10||bet>balance){alert("Ошибка ставки!");return;}let autoVal=parseFloat(document.getElementById("autoCash").value);if(autoVal<1.01)autoVal=0;let res=await fetch("/api/place_crash_bet",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({telegram_id:tgId,bet:bet,auto_cash:autoVal})});let data=await res.json();if(data.success){await updateBalance(-bet);myBet=bet;myAutoCash=autoVal;hasBet=true;hasCashedOut=false;document.getElementById("placeBetBtn").style.display="none";}else alert(data.message);}async function cashout(){if(!hasBet||hasCashedOut){alert("Нет ставки!");return;}if(gameState!="flying"){alert("Вывод только во время полёта!");return;}let res=await fetch("/api/crash_cashout",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({telegram_id:tgId})});let data=await res.json();if(data.success){await updateBalance(data.win_amount);hasCashedOut=true;document.getElementById("placeBetBtn").style.display="block";document.getElementById("cashoutBtn").style.display="none";addHistory("КРАШ",myBet,data.win_amount-myBet,`${data.multiplier.toFixed(2)}x`);myBet=0;hasBet=false;}else alert(data.message);}async function checkCrash(){if(!hasBet||hasCashedOut)return;let res=await fetch("/api/check_crash_result",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({telegram_id:tgId})});let data=await res.json();if(data.crashed){document.getElementById("betStatus").innerHTML=`💀 КРАШ! -${myBet} тяжек`;document.getElementById("placeBetBtn").style.display="block";document.getElementById("cashoutBtn").style.display="none";addHistory("КРАШ",myBet,-myBet,`Краш ${data.crash_point.toFixed(2)}x`);myBet=0;hasBet=false;hasCashedOut=false;}}async function spinSlots(){if(isSpinning)return;let bet=parseInt(document.getElementById("slotsBet").value);if(bet<10||bet>balance){alert("Ошибка ставки!");return;}isSpinning=true;await updateBalance(-bet);for(let i=0;i<12;i++){setTimeout(()=>{if(i<10){document.getElementById("slot1").innerText=symbols[Math.floor(Math.random()*symbols.length)];document.getElementById("slot2").innerText=symbols[Math.floor(Math.random()*symbols.length)];document.getElementById("slot3").innerText=symbols[Math.floor(Math.random()*symbols.length)];}},i*80);}setTimeout(async()=>{let r1=symbols[Math.floor(Math.random()*symbols.length)];let r2=symbols[Math.floor(Math.random()*symbols.length)];let r3=symbols[Math.floor(Math.random()*symbols.length)];document.getElementById("slot1").innerText=r1;document.getElementById("slot2").innerText=r2;document.getElementById("slot3").innerText=r3;let win=0;if(r1==r2&&r2==r3){win=bet*symbolMultipliers[r1];}else if(r1==r2||r2==r3||r1==r3){win=bet*2;}if(win>0){await updateBalance(win);addHistory("СЛОТЫ",bet,win-bet,`${r1}${r2}${r3}`);alert("🏆 ПОБЕДА! +"+win.toLocaleString()+" тяжек");}else{addHistory("СЛОТЫ",bet,-bet,`${r1}${r2}${r3}`);alert("❌ ПРОИГРЫШ! -"+bet.toLocaleString()+" тяжек");}isSpinning=false;},1000);}async function getBonus(){if(!tgId){alert("Привяжите Telegram!");return;}let res=await fetch("/api/get_bonus",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({telegram_id:tgId})});let data=await res.json();if(data.success){await updateBalance(data.amount);alert("🎉 +"+data.amount.toLocaleString()+" тяжек");}else alert(`⏰ ${data.message}`);}function addHistory(game,bet,win,result){let hist=document.getElementById("historyList");let item=document.createElement("div");item.className="history-item";item.innerHTML=`<span>${game}</span><span>${bet.toLocaleString()}</span><span class="${win>0?"win-text":"lose-text"}">${win>0?"+"+win.toLocaleString():win}</span><span>${result}</span>`;hist.insertBefore(item,hist.firstChild);if(hist.children.length>15)hist.removeChild(hist.lastChild);}function setMaxBet(){if(balance>0){if(document.getElementById("betAmount").offsetParent)document.getElementById("betAmount").value=balance;if(document.getElementById("slotsBet").offsetParent)document.getElementById("slotsBet").value=balance;}}function switchGame(game){document.getElementById("crashGame").style.display=game=="crash"?"block":"none";document.getElementById("slotsGame").style.display=game=="slots"?"block":"none";document.getElementById("promoGame").style.display=game=="promo"?"block":"none";}document.querySelectorAll(".game-btn").forEach(btn=>{btn.addEventListener("click",()=>{document.querySelectorAll(".game-btn").forEach(b=>b.classList.remove("active"));btn.classList.add("active");switchGame(btn.dataset.game);});});document.querySelectorAll(".preset-btn").forEach(btn=>{btn.addEventListener("click",()=>{let bet=btn.dataset.bet;if(bet==="max"){setMaxBet();}else{if(document.getElementById("betAmount").offsetParent)document.getElementById("betAmount").value=bet;if(document.getElementById("slotsBet").offsetParent)document.getElementById("slotsBet").value=bet;}});});document.getElementById("placeBetBtn").onclick=placeBet;document.getElementById("cashoutBtn").onclick=cashout;document.getElementById("slotsSpinBtn").onclick=spinSlots;document.getElementById("promoBonusBtn").onclick=getBonus;setInterval(fetchState,300);setInterval(checkCrash,500);if(tgId)loadBalance();
    </script>
    </body>
    </html>
    '''

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("="*40)
    print("🐐 БУРМАЛДАТОЕ CASINO")
    print("="*40)
    print(f"🤖 Бот запущен")
    print(f"🌐 Веб-казино: {WEB_URL}")
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=WEB_PORT)
