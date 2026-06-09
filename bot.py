#!/usr/bin/env python3
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, BotCommand, MenuButtonCommands
from flask import Flask, request, jsonify
import sqlite3
import random
import threading
import time
from datetime import datetime, timedelta
import secrets
import socket
import json

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8684953028:AAEeLaicBO61TCHx3U-Emrupf-XSVjRy5fQ"
ADMIN_IDS = [8609901924]  # Главный админ
WEB_PORT = 5000
MAX_BALANCE = 9999999999

# ========== ДЛЯ ФОРСИРОВАНИЯ РЕЗУЛЬТАТОВ ==========
forced_crash_point = None  # Принудительная точка краша
forced_slots_result = None  # Принудительный результат слотов
forced_roulette_result = None  # Принудительный результат рулетки
forced_wheel_result = None  # Принудительный результат колеса

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
        last_bonus_time TIMESTAMP,
        games_played INTEGER DEFAULT 0,
        total_won INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

init_db()

def get_user(telegram_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (str(telegram_id),)).fetchone()
    conn.close()
    return user

def create_user(telegram_id, username):
    conn = get_db()
    conn.execute("INSERT INTO users (telegram_id, username, balance, last_bonus_time, is_admin) VALUES (?, ?, 5000, ?, 0)", 
                 (str(telegram_id), username, datetime.now() - timedelta(hours=1)))
    conn.commit()
    conn.close()

def get_balance(telegram_id):
    user = get_user(telegram_id)
    if user:
        return min(user['balance'], MAX_BALANCE)
    return 5000

def update_balance(telegram_id, amount):
    conn = get_db()
    current = get_balance(telegram_id)
    new_balance = current + amount
    if new_balance > MAX_BALANCE:
        new_balance = MAX_BALANCE
    if new_balance < 0:
        new_balance = 0
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

def get_last_bonus(telegram_id):
    user = get_user(telegram_id)
    if user and user['last_bonus_time']:
        return datetime.fromisoformat(user['last_bonus_time'])
    return datetime.now() - timedelta(hours=1)

def update_bonus_time(telegram_id):
    conn = get_db()
    conn.execute("UPDATE users SET last_bonus_time = ? WHERE telegram_id = ?", 
                 (datetime.now().isoformat(), str(telegram_id)))
    conn.commit()
    conn.close()

def is_admin(user_id):
    user = get_user(user_id)
    if user and user['is_admin'] == 1:
        return True
    return user_id in ADMIN_IDS

def make_admin(telegram_id):
    conn = get_db()
    conn.execute("UPDATE users SET is_admin = 1 WHERE telegram_id = ?", (str(telegram_id),))
    conn.commit()
    conn.close()

def remove_admin(telegram_id):
    conn = get_db()
    conn.execute("UPDATE users SET is_admin = 0 WHERE telegram_id = ?", (str(telegram_id),))
    conn.commit()
    conn.close()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return 'localhost'

# ========== ГЕНЕРАЦИЯ КРАША (редкие высокие иксы) ==========
high_x_counter = 0  # Счётчик для редких высоких иксов

def generate_crash_point():
    global high_x_counter
    high_x_counter += 1
    
    # Если есть принудительная точка - используем её
    global forced_crash_point
    if forced_crash_point is not None:
        point = forced_crash_point
        forced_crash_point = None
        print(f"🎯 ПРИНУДИТЕЛЬНЫЙ КРАШ: {point}x")
        high_x_counter = 0
        return point
    
    # Обычная генерация: 1 из 20 раундов может быть выше 5x
    if high_x_counter >= 20:
        # Высокий икс (5x - 75x)
        point = round(random.uniform(5.0, 75.0), 2)
        high_x_counter = 0
        print(f"💥 ВЫСОКИЙ ИКС! {point}x (1 раз на 20 раундов)")
    else:
        # Низкий икс (1.1x - 5x)
        point = round(random.uniform(1.1, 5.0), 2)
        print(f"📊 Обычный икс: {point}x")
    
    return point

# ========== CRASH GAME ==========
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
            
            for uid, bet_info in list(user_bets.items()):
                if not bet_info.get('cashed_out', False):
                    auto_cash = bet_info.get('auto_cash', 0)
                    if auto_cash > 0 and current_multiplier >= auto_cash:
                        win_amount = int(bet_info['bet'] * current_multiplier)
                        update_balance(uid, win_amount)
                        update_stats(uid, bet_info['bet'], win_amount)
                        bet_info['cashed_out'] = True
                        bet_info['win_amount'] = win_amount
                        print(f"🤖 Авто-вывод {uid}: {win_amount} на {current_multiplier}x")
            
            if current_multiplier >= crash_point:
                game_state = 'crashed'
                print(f"💥 РАУНД {current_round_id} КРАШ на {crash_point}x!")
                
                for uid, bet_info in list(user_bets.items()):
                    if not bet_info.get('cashed_out', False):
                        update_stats(uid, bet_info['bet'], -bet_info['bet'])
                        print(f"💀 Проигрыш {uid}: {bet_info['bet']}")
                
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
    
threading.Thread(target=game_loop, daemon=True).start()

# ========== TELEGRAM БОТ ==========
bot = telebot.TeleBot(BOT_TOKEN)

# Установка кнопки Menu
def setup_menu():
    commands = [
        BotCommand("start", "🏠 Главное меню"),
        BotCommand("casino", "🎰 Открыть казино"),
        BotCommand("bonus", "🎁 Получить бонус"),
        BotCommand("balance", "💰 Баланс"),
        BotCommand("stats", "📊 Статистика"),
        BotCommand("top", "🏆 Топ игроков"),
        BotCommand("admin", "👑 Админ панель"),
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
    
    balance = get_balance(user_id)
    
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("🎰 КАЗИНО"), KeyboardButton("🎁 БОНУС"))
    keyboard.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("📊 СТАТИСТИКА"))
    keyboard.add(KeyboardButton("🏆 ТОП"), KeyboardButton("❓ ПОМОЩЬ"))
    
    bot.send_message(message.chat.id,
        f"🐐 БУРМАЛДАТОЕ CASINO 🐐\n\nБаланс: {balance:,} ₽\n\nВыберите действие:",
        reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == "🎰 КАЗИНО")
def casino_button(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    ip = get_local_ip()
    
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎰 ВОЙТИ В КАЗИНО", url=f"http://{ip}:{WEB_PORT}?tg_id={user_id}&tg_name={username}"))
    bot.send_message(message.chat.id, "Нажмите на кнопку чтобы войти в казино:", reply_markup=kb)

@bot.message_handler(commands=['casino'])
def casino_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    ip = get_local_ip()
    
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎰 ВОЙТИ В КАЗИНО", url=f"http://{ip}:{WEB_PORT}?tg_id={user_id}&tg_name={username}"))
    bot.send_message(message.chat.id, "Нажмите на кнопку:", reply_markup=kb)

@bot.message_handler(commands=['bonus'])
def bonus_cmd(message):
    user_id = message.from_user.id
    
    if not get_user(user_id):
        create_user(user_id, message.from_user.username or "player")
    
    last_bonus = get_last_bonus(user_id)
    now = datetime.now()
    time_diff = (now - last_bonus).total_seconds()
    
    if time_diff < 600:
        remaining = int((600 - time_diff) / 60)
        bot.send_message(message.chat.id, f"⏰ БОНУС ЧЕРЕЗ {remaining} МИН")
        return
    
    bonus_amount = random.randint(100, 100000)
    update_bonus_time(user_id)
    new_balance = update_balance(user_id, bonus_amount)
    bot.send_message(message.chat.id, f"🎉 +{bonus_amount:,} ₽! Баланс: {new_balance:,} ₽")

@bot.message_handler(commands=['balance'])
def balance_cmd(message):
    balance = get_balance(message.from_user.id)
    bot.send_message(message.chat.id, f"💰 БАЛАНС: {balance:,} ₽")

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    user = get_user(message.from_user.id)
    if user:
        bot.send_message(message.chat.id,
            f"📊 **СТАТИСТИКА**\n\n"
            f"🎮 Игр: {user['games_played']}\n"
            f"🏆 Выиграно: {user['total_won']:,} ₽\n"
            f"💰 Баланс: {user['balance']:,} ₽",
            parse_mode='Markdown')

@bot.message_handler(commands=['top'])
def top_cmd(message):
    conn = get_db()
    top = conn.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10").fetchall()
    conn.close()
    text = "🏆 **ТОП-10** 🏆\n\n"
    for i, p in enumerate(top, 1):
        text += f"{i}. @{p['username'] or 'Игрок'} — {p['balance']:,} ₽\n"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id,
        f"❓ **ПОМОЩЬ**\n\n"
        f"🎮 **ИГРЫ:** Crash, Слоты, Рулетка, Колесо\n"
        f"🎁 **БОНУС:** /bonus каждые 10 мин\n"
        f"🎰 **ИГРАТЬ:** Нажмите КАЗИНО на клавиатуре\n\n"
        f"🔥 **ОСОБЕННОСТИ:**\n"
        f"• Высокие иксы (>5x) выпадают раз в 20 раундов\n"
        f"• Авто-вывод в Crash игре\n"
        f"• Привязка Telegram аккаунта", 
        parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text in ["🎁 БОНУС", "💰 БАЛАНС", "📊 СТАТИСТИКА", "🏆 ТОП", "❓ ПОМОЩЬ"])
def handle_buttons(message):
    if message.text == "🎁 БОНУС":
        bonus_cmd(message)
    elif message.text == "💰 БАЛАНС":
        balance_cmd(message)
    elif message.text == "📊 СТАТИСТИКА":
        stats_cmd(message)
    elif message.text == "🏆 ТОП":
        top_cmd(message)
    elif message.text == "❓ ПОМОЩЬ":
        help_cmd(message)

# ========== АДМИН-КОМАНДЫ ==========
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Нет доступа!")
        return
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="admin_stats"),
        InlineKeyboardButton("👥 ПОЛЬЗОВАТЕЛИ", callback_data="admin_users"),
        InlineKeyboardButton("📢 РАССЫЛКА", callback_data="admin_broadcast"),
        InlineKeyboardButton("💰 БАЛАНСЫ", callback_data="admin_balances"),
        InlineKeyboardButton("👑 ДОБАВИТЬ АДМИНА", callback_data="admin_add"),
        InlineKeyboardButton("🎯 ФОРС КРАША", callback_data="admin_force")
    )
    bot.send_message(message.chat.id, 
        "👑 **АДМИН-ПАНЕЛЬ**\n\n"
        "📌 **КОМАНДЫ:**\n"
        "`/addadmin @username` - добавить админа\n"
        "`/removeadmin @username` - удалить админа\n"
        "`/forcecrash @username 2.5` - принудительный краш\n"
        "`/addmoney @username 1000` - выдать монеты\n"
        "`/take @username 500` - забрать монеты\n"
        "`/setbalance @username 10000` - установить баланс", 
        reply_markup=kb, parse_mode='Markdown')

@bot.message_handler(commands=['addadmin'])
def add_admin_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Нет доступа!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ ФОРМАТ: `/addadmin @username`", parse_mode='Markdown')
            return
        
        user_input = parts[1]
        telegram_id = None
        username = None
        
        if user_input.startswith('@'):
            username_search = user_input[1:]
            conn = get_db()
            user = conn.execute("SELECT telegram_id, username FROM users WHERE username LIKE ?", (f'%{username_search}%',)).fetchone()
            conn.close()
            if user:
                telegram_id = user['telegram_id']
                username = user['username']
        else:
            telegram_id = user_input
            user = get_user(telegram_id)
            if user:
                username = user['username']
        
        if not telegram_id:
            bot.reply_to(message, f"❌ Пользователь {user_input} не найден!")
            return
        
        make_admin(telegram_id)
        bot.reply_to(message, f"✅ АДМИН ДОБАВЛЕН\n👤 @{username or telegram_id}")
        
        try:
            bot.send_message(int(telegram_id), f"👑 ВАМ ВЫДАНЫ ПРАВА АДМИНИСТРАТОРА!")
        except:
            pass
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(commands=['removeadmin'])
def remove_admin_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Нет доступа!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ ФОРМАТ: `/removeadmin @username`", parse_mode='Markdown')
            return
        
        user_input = parts[1]
        telegram_id = None
        username = None
        
        if user_input.startswith('@'):
            username_search = user_input[1:]
            conn = get_db()
            user = conn.execute("SELECT telegram_id, username FROM users WHERE username LIKE ?", (f'%{username_search}%',)).fetchone()
            conn.close()
            if user:
                telegram_id = user['telegram_id']
                username = user['username']
        else:
            telegram_id = user_input
            user = get_user(telegram_id)
            if user:
                username = user['username']
        
        if not telegram_id:
            bot.reply_to(message, f"❌ Пользователь {user_input} не найден!")
            return
        
        remove_admin(telegram_id)
        bot.reply_to(message, f"✅ АДМИН УДАЛЁН\n👤 @{username or telegram_id}")
        
        try:
            bot.send_message(int(telegram_id), f"⚠️ ВАС ЛИШИЛИ ПРАВ АДМИНИСТРАТОРА!")
        except:
            pass
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(commands=['forcecrash'])
def force_crash_command(message):
    global forced_crash_point
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Нет доступа!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ ФОРМАТ: `/forcecrash 2.5`\n\nУкажите множитель (от 1.1 до 75)", parse_mode='Markdown')
            return
        
        point = float(parts[1])
        if point < 1.1 or point > 75:
            bot.reply_to(message, "❌ Множитель должен быть от 1.1 до 75")
            return
        
        forced_crash_point = round(point, 2)
        bot.reply_to(message, f"🎯 **СЛЕДУЮЩИЙ КРАШ БУДЕТ НА {forced_crash_point}x!**\n\n⏰ Ожидайте начала следующего раунда.", parse_mode='Markdown')
        
        # Уведомление всех админов
        conn = get_db()
        admins = conn.execute("SELECT telegram_id FROM users WHERE is_admin = 1").fetchall()
        conn.close()
        for admin in admins:
            try:
                bot.send_message(admin['telegram_id'], f"🎯 АДМИН УСТАНОВИЛ ПРИНУДИТЕЛЬНЫЙ КРАШ: {forced_crash_point}x")
            except:
                pass
    except ValueError:
        bot.reply_to(message, "❌ Введите число!")

@bot.message_handler(commands=['addmoney'])
def add_money_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Нет доступа!")
        return
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ ФОРМАТ: `/addmoney @username 1000`", parse_mode='Markdown')
            return
        user_input = parts[1]
        amount = int(parts[2])
        if amount <= 0 or amount > MAX_BALANCE:
            bot.reply_to(message, f"❌ Сумма от 1 до {MAX_BALANCE:,} ₽")
            return
        telegram_id = None
        username = None
        if user_input.startswith('@'):
            username_search = user_input[1:]
            conn = get_db()
            user = conn.execute("SELECT telegram_id, username FROM users WHERE username LIKE ?", (f'%{username_search}%',)).fetchone()
            conn.close()
            if user:
                telegram_id = user['telegram_id']
                username = user['username']
        else:
            telegram_id = user_input
            user = get_user(telegram_id)
            if user:
                username = user['username']
        if not telegram_id:
            bot.reply_to(message, f"❌ Пользователь {user_input} не найден!")
            return
        new_balance = update_balance(telegram_id, amount)
        bot.reply_to(message, f"✅ ВЫДАНО {amount:,} ₽\n👤 @{username or telegram_id}\n💰 Баланс: {new_balance:,} ₽")
        try:
            bot.send_message(int(telegram_id), f"🎉 АДМИН ВЫДАЛ ВАМ {amount:,} ₽!\n💰 Новый баланс: {new_balance:,} ₽")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Ошибка!")

@bot.message_handler(commands=['take'])
def take_money_command(message):
    if not is_admin(message.from_user.id):
        return
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ ФОРМАТ: `/take @username 500`", parse_mode='Markdown')
            return
        user_input = parts[1]
        amount = int(parts[2])
        if amount <= 0:
            bot.reply_to(message, "❌ Сумма должна быть больше 0!")
            return
        telegram_id = None
        username = None
        if user_input.startswith('@'):
            username_search = user_input[1:]
            conn = get_db()
            user = conn.execute("SELECT telegram_id, username FROM users WHERE username LIKE ?", (f'%{username_search}%',)).fetchone()
            conn.close()
            if user:
                telegram_id = user['telegram_id']
                username = user['username']
        else:
            telegram_id = user_input
            user = get_user(telegram_id)
            if user:
                username = user['username']
        if not telegram_id:
            bot.reply_to(message, f"❌ Пользователь {user_input} не найден!")
            return
        current_balance = get_balance(telegram_id)
        if current_balance < amount:
            bot.reply_to(message, f"❌ У игрока недостаточно средств! Баланс: {current_balance:,} ₽")
            return
        new_balance = update_balance(telegram_id, -amount)
        bot.reply_to(message, f"✅ СНЯТО {amount:,} ₽\n👤 @{username or telegram_id}\n💰 Баланс: {new_balance:,} ₽")
        try:
            bot.send_message(int(telegram_id), f"⚠️ АДМИН СНЯЛ {amount:,} ₽!\n💰 Новый баланс: {new_balance:,} ₽")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Ошибка!")

@bot.message_handler(commands=['setbalance'])
def set_balance_command(message):
    if not is_admin(message.from_user.id):
        return
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ ФОРМАТ: `/setbalance @username 10000`", parse_mode='Markdown')
            return
        user_input = parts[1]
        new_amount = int(parts[2])
        if new_amount < 0 or new_amount > MAX_BALANCE:
            bot.reply_to(message, f"❌ Сумма от 0 до {MAX_BALANCE:,} ₽")
            return
        telegram_id = None
        username = None
        old_balance = 0
        if user_input.startswith('@'):
            username_search = user_input[1:]
            conn = get_db()
            user = conn.execute("SELECT telegram_id, username, balance FROM users WHERE username LIKE ?", (f'%{username_search}%',)).fetchone()
            conn.close()
            if user:
                telegram_id = user['telegram_id']
                username = user['username']
                old_balance = user['balance']
        else:
            telegram_id = user_input
            user = get_user(telegram_id)
            if user:
                username = user['username']
                old_balance = user['balance']
        if not telegram_id:
            bot.reply_to(message, f"❌ Пользователь {user_input} не найден!")
            return
        diff = new_amount - old_balance
        new_balance = update_balance(telegram_id, diff)
        bot.reply_to(message, f"✅ БАЛАНС ИЗМЕНЁН\n👤 @{username or telegram_id}\n📉 Было: {old_balance:,} ₽\n📈 Стало: {new_balance:,} ₽")
        try:
            bot.send_message(int(telegram_id), f"📊 АДМИН ИЗМЕНИЛ БАЛАНС!\n📉 Было: {old_balance:,} ₽\n📈 Стало: {new_balance:,} ₽")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Ошибка!")

@bot.message_handler(commands=['userinfo'])
def userinfo_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Нет доступа!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ ФОРМАТ: `/userinfo @username`", parse_mode='Markdown')
            return
        
        user_input = parts[1]
        if user_input.startswith('@'):
            username_search = user_input[1:]
            conn = get_db()
            user = conn.execute("SELECT * FROM users WHERE username LIKE ?", (f'%{username_search}%',)).fetchone()
            conn.close()
            if user:
                bot.reply_to(message, 
                    f"👤 **ИНФОРМАЦИЯ**\n\n"
                    f"📱 ID: `{user['telegram_id']}`\n"
                    f"👥 Username: @{user['username'] or 'Нет'}\n"
                    f"💰 Баланс: {user['balance']:,} ₽\n"
                    f"🎮 Игр: {user['games_played']}\n"
                    f"🏆 Выиграно: {user['total_won']:,} ₽\n"
                    f"👑 Админ: {'✅' if user['is_admin'] else '❌'}",
                    parse_mode='Markdown')
            else:
                bot.reply_to(message, f"❌ Пользователь {user_input} не найден!")
        else:
            user = get_user(user_input)
            if user:
                bot.reply_to(message, 
                    f"👤 **ИНФОРМАЦИЯ**\n\n"
                    f"📱 ID: `{user['telegram_id']}`\n"
                    f"👥 Username: @{user['username'] or 'Нет'}\n"
                    f"💰 Баланс: {user['balance']:,} ₽\n"
                    f"🎮 Игр: {user['games_played']}\n"
                    f"🏆 Выиграно: {user['total_won']:,} ₽\n"
                    f"👑 Админ: {'✅' if user['is_admin'] else '❌'}",
                    parse_mode='Markdown')
            else:
                bot.reply_to(message, f"❌ Пользователь не найден!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(commands=['allusers'])
def allusers_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Нет доступа!")
        return
    
    conn = get_db()
    users = conn.execute("SELECT telegram_id, username, balance FROM users ORDER BY balance DESC").fetchall()
    conn.close()
    
    if not users:
        bot.reply_to(message, "Нет пользователей")
        return
    
    text = "👥 **СПИСОК ВСЕХ ИГРОКОВ**\n\n"
    for i, user in enumerate(users, 1):
        text += f"{i}. @{user['username'] or user['telegram_id']} — {user['balance']:,} ₽\n"
        if len(text) > 3800:
            text += "..."
            break
    
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Доступ запрещён", show_alert=True)
        return
    
    if call.data == "admin_stats":
        conn = get_db()
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_balance = conn.execute("SELECT SUM(balance) FROM users").fetchone()[0] or 0
        total_games = conn.execute("SELECT SUM(games_played) FROM users").fetchone()[0] or 0
        total_won = conn.execute("SELECT SUM(total_won) FROM users").fetchone()[0] or 0
        conn.close()
        
        text = (f"📊 **СТАТИСТИКА**\n\n"
                f"👥 Игроков: {total_users}\n"
                f"💰 Общий баланс: {total_balance:,} ₽\n"
                f"🎮 Всего игр: {total_games}\n"
                f"🏆 Выиграно: {total_won:,} ₽")
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    
    elif call.data == "admin_users":
        conn = get_db()
        users = conn.execute("SELECT username, balance, is_admin FROM users ORDER BY balance DESC LIMIT 10").fetchall()
        conn.close()
        text = "👥 **ТОП-10 ИГРОКОВ**\n\n"
        for i, u in enumerate(users, 1):
            admin_star = " 👑" if u['is_admin'] else ""
            text += f"{i}. @{u['username'] or 'Игрок'}{admin_star} — {u['balance']:,} ₽\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    
    elif call.data == "admin_balances":
        conn = get_db()
        total = conn.execute("SELECT SUM(balance) FROM users").fetchone()[0] or 0
        avg = conn.execute("SELECT AVG(balance) FROM users").fetchone()[0] or 0
        mini = conn.execute("SELECT MIN(balance) FROM users").fetchone()[0] or 0
        maxi = conn.execute("SELECT MAX(balance) FROM users").fetchone()[0] or 0
        conn.close()
        text = (f"💰 **БАЛАНСЫ**\n\n"
                f"💵 Общий: {total:,} ₽\n"
                f"📊 Средний: {avg:,.0f} ₽\n"
                f"📉 Минимальный: {mini:,} ₽\n"
                f"📈 Максимальный: {maxi:,} ₽")
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    
    elif call.data == "admin_add":
        bot.edit_message_text(
            "👑 **ДОБАВИТЬ АДМИНА**\n\n"
            "Используйте команду:\n"
            "`/addadmin @username`\n\n"
            "Пример:\n"
            "`/addadmin @Piarkosiii`",
            call.message.chat.id, call.message.message_id,
            parse_mode='Markdown'
        )
    
    elif call.data == "admin_force":
        bot.edit_message_text(
            "🎯 **ФОРС КРАША**\n\n"
            "Используйте команду:\n"
            "`/forcecrash 2.5`\n\n"
            "Где 2.5 - множитель (от 1.1 до 75)\n\n"
            "Пример:\n"
            "`/forcecrash 10.0` - следующий краш на 10x",
            call.message.chat.id, call.message.message_id,
            parse_mode='Markdown'
        )
    
    elif call.data == "admin_broadcast":
        msg = bot.send_message(call.message.chat.id, "📢 Введите текст рассылки:")
        bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    if not is_admin(message.from_user.id):
        return
    
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
    
    bot.send_message(message.chat.id, f"✅ Рассылка завершена! Доставлено: {success}")

# ========== ВЕБ-СЕРВЕР ==========
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Сокращённый HTML для веб-казино (аналогичный предыдущим)
WEB_HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Бурмалдатое Casino</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: linear-gradient(135deg, #0a0f1e, #0f1629); font-family: 'Segoe UI', sans-serif; padding: 16px; color: white; }
        .container { max-width: 480px; margin: 0 auto; background: rgba(10,15,30,0.85); border-radius: 28px; border: 1px solid #ffd700; overflow: hidden; }
        .header { background: linear-gradient(135deg, #1a1f2e, #0d1225); padding: 20px; text-align: center; border-bottom: 2px solid #ffd700; }
        .title { font-size: 22px; font-weight: bold; background: linear-gradient(45deg, #ffd700, #ff6b6b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .balance-box { background: rgba(0,0,0,0.5); border-radius: 20px; padding: 12px; margin-top: 12px; }
        .balance-amount { font-size: 38px; font-weight: bold; color: #ffd700; }
        .multipliers-row { display: grid; grid-template-columns: repeat(5,1fr); gap:8px; padding:15px; background:rgba(0,0,0,0.3); text-align:center; }
        .multiplier-item { background:rgba(255,255,255,0.08); padding:8px; border-radius:12px; color:#ffd700; }
        .game-nav { display:grid; grid-template-columns:repeat(5,1fr); gap:5px; padding:15px; background:rgba(0,0,0,0.3); }
        .game-btn { background:rgba(255,255,255,0.08); border:none; padding:10px; border-radius:16px; color:#aaa; cursor:pointer; text-align:center; }
        .game-btn.active { background:linear-gradient(135deg,#ffd700,#ff8c00); color:#000; }
        .game-area { padding:20px; }
        .crash-container { background:linear-gradient(180deg,#1a1f2e,#0d1225); border-radius:24px; overflow:hidden; }
        .crash-header { background:#00000033; padding:25px; text-align:center; }
        .crash-multiplier { font-size:72px; font-weight:800; color:#ffd700; font-family:monospace; }
        .crash-status { text-align:center; font-size:14px; padding:8px; border-radius:20px; margin-top:10px; }
        .status-betting { background:#ff8c00; color:#000; }
        .status-flying { background:#2ed573; color:#000; animation: pulse 0.5s infinite; }
        .status-crashed { background:#ff4757; color:#fff; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
        .timer-section { background:#00000033; padding:15px; text-align:center; margin:15px; border-radius:20px; }
        .timer-value { font-size:28px; font-weight:bold; color:#ffd700; }
        .crash-history { display:flex; gap:10px; flex-wrap:wrap; justify-content:center; margin:15px; padding:10px; background:#00000033; border-radius:20px; }
        .history-crash-item { background:rgba(255,255,255,0.1); padding:6px 14px; border-radius:20px; font-size:14px; }
        .bet-section { padding:16px; }
        .bet-input { width:100%; background:rgba(0,0,0,0.5); border:1px solid #ffd700; padding:14px; border-radius:16px; color:white; font-size:18px; text-align:center; margin-bottom:12px; }
        .bet-presets { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:16px; }
        .preset-btn { background:rgba(255,255,255,0.08); border:none; padding:10px; border-radius:12px; color:#ffd700; cursor:pointer; }
        .auto-cash-row { display:flex; align-items:center; justify-content:space-between; background:#00000033; padding:12px; border-radius:16px; margin-bottom:16px; }
        .auto-cash-input { background:rgba(0,0,0,0.5); border:1px solid #ffd700; padding:8px; border-radius:12px; color:#ffd700; width:80px; text-align:center; }
        .action-btn { width:100%; background:linear-gradient(135deg,#ffd700,#ff8c00); border:none; padding:16px; border-radius:20px; font-size:18px; font-weight:bold; color:#000; cursor:pointer; }
        .action-btn:active { transform:scale(0.98); }
        .bet-status { text-align:center; margin-top:12px; font-size:12px; color:#aaa; }
        .slots-reels { display:flex; justify-content:center; gap:15px; margin:30px 0; }
        .slot-reel { width:80px; height:80px; background:rgba(0,0,0,0.6); border-radius:18px; display:flex; align-items:center; justify-content:center; font-size:48px; border:2px solid #ffd700; }
        .roulette-number { width:90px; height:90px; background:radial-gradient(circle,#ffd700,#ff8c00); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:38px; margin:20px auto; }
        .numbers-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:8px; margin:20px 0; }
        .num-btn { background:rgba(255,255,255,0.08); border:none; padding:12px; border-radius:12px; color:white; cursor:pointer; text-align:center; }
        .num-btn.selected { background:#ffd700; color:#000; }
        .wheel-container { text-align:center; margin:20px 0; }
        canvas { box-shadow:0 0 20px rgba(255,215,0,0.3); border-radius:50%; }
        .history-section { padding:15px; border-top:1px solid rgba(255,215,0,0.2); max-height:160px; overflow-y:auto; }
        .history-title { font-size:11px; color:#666; margin-bottom:8px; }
        .history-item { background:rgba(255,255,255,0.04); padding:8px; margin:4px 0; border-radius:10px; font-size:11px; display:flex; justify-content:space-between; }
        .win-text { color:#4caf50; }
        .lose-text { color:#ff4757; }
        @media (max-width:480px){ .slot-reel{ width:65px; height:65px; font-size:40px; } .crash-multiplier{ font-size:48px; } }
    </style>
</head>
<body>
<div class="container">
    <div class="header"><div class="title">🐐 БУРМАЛДАТОЕ CASINO 🐐</div><div class="balance-box"><div>БАЛАНС:</div><div class="balance-amount" id="balance">0</div></div></div>
    <div class="multipliers-row"><div class="multiplier-item">1.56x</div><div class="multiplier-item">1.45x</div><div class="multiplier-item">2.01x</div><div class="multiplier-item">1.00x</div><div class="multiplier-item">2.90x</div></div>
    <div class="game-nav"><button class="game-btn active" data-game="crash">💥 CRASH</button><button class="game-btn" data-game="slots">🎰 Слоты</button><button class="game-btn" data-game="roulette">🎡 Рулетка</button><button class="game-btn" data-game="wheel">🎲 Колесо</button><button class="game-btn" data-game="promo">🎁 Промо</button></div>
    <div class="game-area" id="gameArea">
        <div id="crashGame"><div class="crash-container"><div class="crash-header"><div class="crash-multiplier" id="currentMult">1.00x</div><div class="crash-status status-betting" id="crashStatus">🎲 ПРИЁМ СТАВОК</div></div><div class="timer-section"><div>⏱️ ДО ПОЛЁТА</div><div class="timer-value" id="timerValue">10</div></div><div class="crash-history" id="crashHistory"></div><div class="bet-section"><input type="number" id="betAmount" class="bet-input" placeholder="СТАВКА" value="100"><div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div><div class="auto-cash-row"><span>🤖 АВТО-ВЫВОД (x):</span><input type="number" id="autoCash" class="auto-cash-input" value="2.00" step="0.5"></div><button class="action-btn" id="placeBetBtn">💰 СДЕЛАТЬ СТАВКУ</button><button class="action-btn" id="cashoutBtn" style="display:none">✅ ЗАБРАТЬ</button><div class="bet-status" id="betStatus"></div></div></div></div>
        <div id="slotsGame" style="display:none"><div class="slots-reels"><div class="slot-reel" id="slot1">🍒</div><div class="slot-reel" id="slot2">🍋</div><div class="slot-reel" id="slot3">🍊</div></div><div class="bet-section"><input type="number" id="slotsBet" class="bet-input" placeholder="СТАВКА" value="100"><div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div><button class="action-btn" id="slotsSpinBtn">🎰 КРУТИТЬ</button></div></div>
        <div id="rouletteGame" style="display:none"><div class="roulette-number" id="rouletteResult">?</div><div class="numbers-grid" id="rouletteNumbers"></div><div class="bet-section"><input type="number" id="rouletteBet" class="bet-input" placeholder="СТАВКА" value="100"><div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div><button class="action-btn" id="rouletteSpinBtn">🎡 КРУТИТЬ</button></div></div>
        <div id="wheelGame" style="display:none"><div class="wheel-container"><canvas id="wheelCanvas" width="240" height="240"></canvas></div><div class="bet-section"><input type="number" id="wheelBet" class="bet-input" placeholder="СТАВКА" value="100"><div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div><button class="action-btn" id="wheelSpinBtn">🎲 КРУТИТЬ</button></div></div>
        <div id="promoGame" style="display:none"><div style="text-align:center; padding:40px;"><div style="font-size:64px;">🎁</div><div style="font-size:18px;">ЕЖЕДНЕВНЫЙ БОНУС</div><div style="font-size:12px; color:#aaa;">от 100 до 100 000 ₽ каждые 10 мин</div><button class="action-btn" id="promoBonusBtn">🎁 ПОЛУЧИТЬ БОНУС</button></div></div>
    </div>
    <div class="history-section"><div class="history-title">📜 ИСТОРИЯ ИГР</div><div id="historyList"></div></div>
</div>
<script>
    const urlParams = new URLSearchParams(window.location.search);
    let tgId = urlParams.get('tg_id');
    let currentBalance = 0;
    let myBet = 0, myAutoCash = 2.00, hasBet = false, hasCashedOut = false;
    let currentMult = 1.00, gameState = 'betting', timerSec = 10, crashHistory = [];
    let isSpinning = false, selectedNum = null;
    const symbols = ['🍒','🍋','🍊','🔔','💎','7️⃣'];
    const wheelSegments = [{mult:0,color:'#f44336'},{mult:1.5,color:'#ff9800'},{mult:0,color:'#f44336'},{mult:2,color:'#4caf50'},{mult:0,color:'#f44336'},{mult:3,color:'#2196f3'},{mult:0,color:'#f44336'},{mult:5,color:'#9c27b0'}];
    let wheelCanvas=null, wheelCtx=null, currentAngle=0;
    
    setInterval(()=>{document.querySelectorAll('.multiplier-item').forEach(el=>{el.innerText=(Math.random()*3+0.5).toFixed(2)+'x';});},4000);
    
    async function loadBalance(){
        if(!tgId) return;
        try{
            let res=await fetch('/api/balance',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId})});
            let data=await res.json();
            currentBalance=data.balance;
            document.getElementById('balance').innerText=currentBalance.toLocaleString();
        }catch(e){}
    }
    async function updateBalance(amount){
        if(!tgId) return;
        let res=await fetch('/api/update_balance',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId,amount:amount})});
        let data=await res.json();
        currentBalance=data.balance;
        document.getElementById('balance').innerText=currentBalance.toLocaleString();
        return currentBalance;
    }
    async function fetchState(){
        try{
            let res=await fetch('/api/crash_state');
            let data=await res.json();
            currentMult=data.multiplier;
            gameState=data.state;
            timerSec=data.timer;
            crashHistory=data.history;
            document.getElementById('currentMult').innerHTML=currentMult.toFixed(2)+'x';
            document.getElementById('timerValue').innerHTML=timerSec;
            let historyDiv=document.getElementById('crashHistory');
            historyDiv.innerHTML='';
            crashHistory.slice(0,8).forEach(p=>{let col=p<2?'#ff4755':p<5?'#ffaa00':'#4caf50';historyDiv.innerHTML+=`<div class="history-crash-item" style="background:${col}33;color:${col}">${p.toFixed(2)}x</div>`;});
            let statusDiv=document.getElementById('crashStatus');
            let placeBtn=document.getElementById('placeBetBtn');
            let cashBtn=document.getElementById('cashoutBtn');
            if(gameState=='betting'){
                statusDiv.innerHTML='🎲 ПРИЁМ СТАВОК';
                statusDiv.className='crash-status status-betting';
                placeBtn.style.display='block';
                cashBtn.style.display='none';
            }else if(gameState=='flying'){
                statusDiv.innerHTML='✈️ ПОЛЁТ... ЗАБЕРИТЕ ВЫИГРЫШ!';
                statusDiv.className='crash-status status-flying';
                if(hasBet && !hasCashedOut && myAutoCash>0 && currentMult>=myAutoCash){await cashout();}
                if(hasBet && !hasCashedOut){placeBtn.style.display='none';cashBtn.style.display='block';}
                else{placeBtn.style.display='block';cashBtn.style.display='none';}
            }else{
                statusDiv.innerHTML='💥 КРАШ!';
                statusDiv.className='crash-status status-crashed';
                placeBtn.style.display='block';
                cashBtn.style.display='none';
            }
        }catch(e){}
    }
    async function placeBet(){
        if(!tgId){alert('Привяжите Telegram!');return;}
        if(hasBet){alert('У вас уже есть ставка!');return;}
        if(gameState!='betting'){alert('❌ СТАВКИ ТОЛЬКО В РЕЖИМЕ ПРИЁМА СТАВОК! Ждите следующего раунда.');return;}
        let bet=parseInt(document.getElementById('betAmount').value);
        if(bet<10){alert('Минимальная ставка 10 ₽');return;}
        if(bet>currentBalance){alert('Не хватает денег! Баланс: '+currentBalance.toLocaleString()+' ₽');return;}
        let autoVal=parseFloat(document.getElementById('autoCash').value);
        if(autoVal<1.01)autoVal=0;
        let res=await fetch('/api/place_crash_bet',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId,bet:bet,auto_cash:autoVal})});
        let data=await res.json();
        if(data.success){
            await updateBalance(-bet);
            myBet=bet;myAutoCash=autoVal;hasBet=true;hasCashedOut=false;
            document.getElementById('betStatus').innerHTML=`✅ Ставка ${bet.toLocaleString()} ₽ принята!`;
            document.getElementById('placeBetBtn').style.display='none';
        }else{alert(data.message);}
    }
    async function cashout(){
        if(!hasBet || hasCashedOut){alert('Нет активной ставки!');return;}
        if(gameState!='flying'){alert('❌ ВЫВОД ТОЛЬКО ВО ВРЕМЯ ПОЛЁТА!');return;}
        let res=await fetch('/api/crash_cashout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId})});
        let data=await res.json();
        if(data.success){
            await updateBalance(data.win_amount);
            hasCashedOut=true;
            document.getElementById('betStatus').innerHTML=`🎉 ВЫИГРЫШ! ${data.multiplier.toFixed(2)}x = ${data.win_amount.toLocaleString()} ₽`;
            document.getElementById('placeBetBtn').style.display='block';
            document.getElementById('cashoutBtn').style.display='none';
            addHistory('CRASH',myBet,data.win_amount-myBet,`${data.multiplier.toFixed(2)}x`);
            myBet=0;hasBet=false;
        }else{alert(data.message);}
    }
    async function checkCrash(){
        if(!hasBet || hasCashedOut)return;
        let res=await fetch('/api/check_crash_result',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId})});
        let data=await res.json();
        if(data.crashed){
            document.getElementById('betStatus').innerHTML=`💀 КРАШ! -${myBet.toLocaleString()} ₽`;
            document.getElementById('placeBetBtn').style.display='block';
            document.getElementById('cashoutBtn').style.display='none';
            addHistory('CRASH',myBet,-myBet,`Краш ${data.crash_point.toFixed(2)}x`);
            myBet=0;hasBet=false;hasCashedOut=false;
        }
    }
    function setMaxBet(){if(currentBalance>0)document.getElementById('betAmount').value=currentBalance;}
    function setSlotsMaxBet(){if(currentBalance>0)document.getElementById('slotsBet').value=currentBalance;}
    function setRouletteMaxBet(){if(currentBalance>0)document.getElementById('rouletteBet').value=currentBalance;}
    function setWheelMaxBet(){if(currentBalance>0)document.getElementById('wheelBet').value=currentBalance;}
    async function spinSlots(){
        if(isSpinning)return;
        let bet=parseInt(document.getElementById('slotsBet').value);
        if(bet<10||bet>currentBalance){alert('Ошибка ставки!');return;}
        isSpinning=true;
        await updateBalance(-bet);
        for(let i=0;i<12;i++){setTimeout(()=>{if(i<10){document.getElementById('slot1').innerText=symbols[Math.floor(Math.random()*symbols.length)];document.getElementById('slot2').innerText=symbols[Math.floor(Math.random()*symbols.length)];document.getElementById('slot3').innerText=symbols[Math.floor(Math.random()*symbols.length)];}},i*80);}
        setTimeout(async()=>{let r1=symbols[Math.floor(Math.random()*symbols.length)];let r2=symbols[Math.floor(Math.random()*symbols.length)];let r3=symbols[Math.floor(Math.random()*symbols.length)];document.getElementById('slot1').innerText=r1;document.getElementById('slot2').innerText=r2;document.getElementById('slot3').innerText=r3;let win=0;if(r1==r2&&r2==r3){win=r1=='7️⃣'?bet*10:bet*5;}else if(r1==r2||r2==r3||r1==r3){win=bet*2;}if(win>0){await updateBalance(win);addHistory('Слоты',bet,win-bet,r1+r2+r3);alert('🏆 ПОБЕДА! +'+win.toLocaleString()+' ₽');}else{addHistory('Слоты',bet,-bet,r1+r2+r3);alert('❌ ПРОИГРЫШ! -'+bet.toLocaleString()+' ₽');}isSpinning=false;},1000);
    }
    function initRoulette(){
        let grid=document.getElementById('rouletteNumbers');
        grid.innerHTML='';
        for(let i=0;i<=36;i++){
            let btn=document.createElement('button');
            btn.className='num-btn';
            btn.innerText=i;
            btn.onclick=(function(num){return function(){document.querySelectorAll('.num-btn').forEach(b=>b.classList.remove('selected'));btn.classList.add('selected');selectedNum=num;};})(i);
            grid.appendChild(btn);
        }
    }
    async function spinRoulette(){
        if(selectedNum===null){alert('Выберите число!');return;}
        let bet=parseInt(document.getElementById('rouletteBet').value);
        if(bet<10||bet>currentBalance){alert('Ошибка ставки!');return;}
        await updateBalance(-bet);
        let result=Math.floor(Math.random()*37);
        document.getElementById('rouletteResult').innerHTML=result;
        if(result==selectedNum){let win=bet*35;await updateBalance(win);addHistory('Рулетка',bet,win-bet,'Угадал '+result);alert('🎉 ПОБЕДА! +'+win.toLocaleString()+' ₽');}
        else{addHistory('Рулетка',bet,-bet,'Выпало '+result);alert('❌ ПРОИГРЫШ! -'+bet.toLocaleString()+' ₽');}
    }
    function drawWheel(){
        if(!wheelCanvas){wheelCanvas=document.getElementById('wheelCanvas');wheelCtx=wheelCanvas.getContext('2d');}
        let anglePer=(Math.PI*2)/wheelSegments.length;
        wheelCtx.clearRect(0,0,240,240);
        for(let i=0;i<wheelSegments.length;i++){
            let start=currentAngle+i*anglePer;
            let end=start+anglePer;
            wheelCtx.beginPath();
            wheelCtx.arc(120,120,115,start,end);
            wheelCtx.lineTo(120,120);
            wheelCtx.fillStyle=wheelSegments[i].color;
            wheelCtx.fill();
            wheelCtx.save();
            wheelCtx.translate(120,120);
            wheelCtx.rotate(start+anglePer/2);
            wheelCtx.fillStyle='white';
            wheelCtx.font='bold 12px Arial';
            wheelCtx.fillText(wheelSegments[i].mult+'x',42,6);
            wheelCtx.restore();
        }
    }
    async function spinWheel(){
        let bet=parseInt(document.getElementById('wheelBet').value);
        if(bet<10||bet>currentBalance){alert('Ошибка ставки!');return;}
        await updateBalance(-bet);
        let idx=Math.floor(Math.random()*wheelSegments.length);
        let mult=wheelSegments[idx].mult;
        let win=Math.floor(bet*mult);
        if(win>0){await updateBalance(win);addHistory('Колесо',bet,win-bet,mult+'x');alert('🎉 ПОБЕДА! '+mult+'x +'+win.toLocaleString()+' ₽');}
        else{addHistory('Колесо',bet,-bet,'0x');alert('❌ ПРОИГРЫШ! -'+bet.toLocaleString()+' ₽');}
    }
    async function getBonus(){
        if(!tgId){alert('Привяжите Telegram!');return;}
        let res=await fetch('/api/get_bonus',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId})});
        let data=await res.json();
        if(data.success){await updateBalance(data.amount);alert(`🎉 +${data.amount.toLocaleString()} ₽`);}
        else{alert(`⏰ ${data.message}`);}
    }
    function addHistory(game,bet,win,res){
        let hist=document.getElementById('historyList');
        let item=document.createElement('div');
        item.className='history-item';
        item.innerHTML=`<span>${game}</span><span>${bet.toLocaleString()} ₽</span><span class="${win>0?'win-text':'lose-text'}">${win>0?'+'+win.toLocaleString():win}</span><span>${res}</span>`;
        hist.insertBefore(item,hist.firstChild);
        if(hist.children.length>15)hist.removeChild(hist.lastChild);
    }
    function switchGame(game){
        document.getElementById('crashGame').style.display=game=='crash'?'block':'none';
        document.getElementById('slotsGame').style.display=game=='slots'?'block':'none';
        document.getElementById('rouletteGame').style.display=game=='roulette'?'block':'none';
        document.getElementById('wheelGame').style.display=game=='wheel'?'block':'none';
        document.getElementById('promoGame').style.display=game=='promo'?'block':'none';
        if(game=='wheel')drawWheel();
    }
    document.querySelectorAll('.game-btn').forEach(btn=>{btn.addEventListener('click',()=>{document.querySelectorAll('.game-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');switchGame(btn.dataset.game);});});
    document.querySelectorAll('.preset-btn').forEach(btn=>{btn.addEventListener('click',()=>{let bet=btn.dataset.bet;
        if(bet==='max'){
            if(document.getElementById('betAmount').offsetParent)setMaxBet();
            if(document.getElementById('slotsBet').offsetParent)setSlotsMaxBet();
            if(document.getElementById('rouletteBet').offsetParent)setRouletteMaxBet();
            if(document.getElementById('wheelBet').offsetParent)setWheelMaxBet();
        }else{
            if(document.getElementById('betAmount').offsetParent)document.getElementById('betAmount').value=bet;
            if(document.getElementById('slotsBet').offsetParent)document.getElementById('slotsBet').value=bet;
            if(document.getElementById('rouletteBet').offsetParent)document.getElementById('rouletteBet').value=bet;
            if(document.getElementById('wheelBet').offsetParent)document.getElementById('wheelBet').value=bet;
        }});});
    document.getElementById('placeBetBtn').onclick=placeBet;
    document.getElementById('cashoutBtn').onclick=cashout;
    document.getElementById('slotsSpinBtn').onclick=spinSlots;
    document.getElementById('rouletteSpinBtn').onclick=spinRoulette;
    document.getElementById('wheelSpinBtn').onclick=spinWheel;
    document.getElementById('promoBonusBtn').onclick=getBonus;
    setInterval(fetchState,300);
    setInterval(checkCrash,500);
    if(tgId)loadBalance();
    initRoulette();
    drawWheel();
</script>
</body>
</html>'''

@app.route('/')
def index():
    return WEB_HTML

@app.route('/api/balance', methods=['POST'])
def api_balance():
    data = request.json
    tg_id = data.get('telegram_id')
    if not tg_id:
        return jsonify({'balance': 5000})
    user = get_user(tg_id)
    if not user:
        create_user(tg_id, "player")
        return jsonify({'balance': 5000})
    return jsonify({'balance': user['balance']})

@app.route('/api/update_balance', methods=['POST'])
def api_update_balance():
    data = request.json
    tg_id = data.get('telegram_id')
    amount = data.get('amount', 0)
    if not tg_id:
        return jsonify({'balance': 5000})
    user = get_user(tg_id)
    if not user:
        create_user(tg_id, "player")
    new_bal = update_balance(tg_id, amount)
    return jsonify({'balance': new_bal})

@app.route('/api/crash_state', methods=['GET'])
def crash_state():
    global game_state, current_multiplier, betting_timer, crash_history
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
        return jsonify({'success': False, 'message': '❌ СТАВКИ ТОЛЬКО В РЕЖИМЕ ПРИЁМА СТАВОК! Ждите следующего раунда.'})
    if tg_id in user_bets:
        return jsonify({'success': False, 'message': '❌ У вас уже есть ставка!'})
    
    user = get_user(tg_id)
    if not user or user['balance'] < bet:
        return jsonify({'success': False, 'message': '❌ Недостаточно средств!'})
    
    user_bets[tg_id] = {'bet': bet, 'cashed_out': False, 'auto_cash': auto_cash, 'win_amount': 0}
    print(f"✅ Ставка {bet} от {tg_id} принята")
    return jsonify({'success': True})

@app.route('/api/crash_cashout', methods=['POST'])
def crash_cashout():
    global user_bets, current_multiplier, game_state
    data = request.json
    tg_id = data.get('telegram_id')
    
    if tg_id not in user_bets:
        return jsonify({'success': False, 'message': 'Нет ставки'})
    if user_bets[tg_id]['cashed_out']:
        return jsonify({'success': False, 'message': 'Уже забрали'})
    if game_state != 'flying':
        return jsonify({'success': False, 'message': 'Вывод только во время полёта!'})
    
    bet_info = user_bets[tg_id]
    win_amount = int(bet_info['bet'] * current_multiplier)
    user_bets[tg_id]['cashed_out'] = True
    update_balance(tg_id, win_amount)
    update_stats(tg_id, bet_info['bet'], win_amount)
    print(f"💰 Вывод {tg_id}: {win_amount} на {current_multiplier}x")
    return jsonify({'success': True, 'win_amount': win_amount, 'multiplier': current_multiplier})

@app.route('/api/check_crash_result', methods=['POST'])
def check_crash_result():
    global user_bets, game_state, crash_point
    data = request.json
    tg_id = data.get('telegram_id')
    
    if game_state == 'crashed' and tg_id in user_bets and not user_bets[tg_id]['cashed_out']:
        bet_info = user_bets[tg_id]
        del user_bets[tg_id]
        update_stats(tg_id, bet_info['bet'], -bet_info['bet'])
        print(f"💀 Проигрыш {tg_id}: {bet_info['bet']} (краш {crash_point}x)")
        return jsonify({'crashed': True, 'crash_point': crash_point})
    return jsonify({'crashed': False})

@app.route('/api/get_bonus', methods=['POST'])
def api_get_bonus():
    data = request.json
    tg_id = data.get('telegram_id')
    user = get_user(tg_id)
    if not user:
        create_user(tg_id, "player")
        return jsonify({'success': True, 'amount': 1000})
    last_bonus = get_last_bonus(tg_id)
    now = datetime.now()
    if (now - last_bonus).total_seconds() < 600:
        remaining = 600 - (now - last_bonus).total_seconds()
        return jsonify({'success': False, 'message': f'Бонус через {int(remaining/60)} мин'})
    bonus = random.randint(100, 100000)
    update_bonus_time(tg_id)
    update_balance(tg_id, bonus)
    return jsonify({'success': True, 'amount': bonus})

def run_bot():
    print("🤖 БОТ ЗАПУЩЕН")
    bot.infinity_polling()

def run_web():
    ip = get_local_ip()
    print(f"🌐 ВЕБ-КАЗИНО: http://{ip}:{WEB_PORT}")
    print(f"🐐 БУРМАЛДАТОЕ CASINO")
    app.run(host='0.0.0.0', port=WEB_PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("="*40)
    print("🐐 БУРМАЛДАТОЕ CRASH CASINO")
    print("="*40)
    threading.Thread(target=run_bot, daemon=True).start()
    run_web()
