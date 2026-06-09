#!/usr/bin/env python3
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
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
WEB_URL = "https://burmaldo-casino.onrender.com"  # ИСПРАВЛЕНО!

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
        total_won INTEGER DEFAULT 0
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
    conn.execute("INSERT INTO users (telegram_id, username, balance, last_bonus_time) VALUES (?, ?, 5000, ?)", 
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
    return user_id in ADMIN_IDS

# ========== TELEGRAM БОТ ==========
bot = telebot.TeleBot(BOT_TOKEN)

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
    
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎰 ВОЙТИ В КАЗИНО", url=f"{WEB_URL}?tg_id={user_id}&tg_name={username}"))
    bot.send_message(message.chat.id, "Нажмите на кнопку чтобы войти в казино:", reply_markup=kb)

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
        f"🎰 **ИГРАТЬ:** Нажмите КАЗИНО на клавиатуре",
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
    
    bot.send_message(message.chat.id, 
        "👑 **АДМИН-ПАНЕЛЬ**\n\n"
        "📌 **КОМАНДЫ:**\n"
        "`/addmoney @username 1000` - выдать монеты\n"
        "`/take @username 500` - забрать монеты\n"
        "`/setbalance @username 10000` - установить баланс\n"
        "`/userinfo @username` - инфо об игроке\n"
        "`/allusers` - список всех игроков", 
        parse_mode='Markdown')

@bot.message_handler(commands=['addmoney'])
def add_money_command(message):
    if not is_admin(message.from_user.id):
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
                    f"🏆 Выиграно: {user['total_won']:,} ₽",
                    parse_mode='Markdown')
            else:
                bot.reply_to(message, f"❌ Пользователь {user_input} не найден!")
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

# ========== FLASK ВЕБ-СЕРВЕР ==========
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Бурмалдатое Casino</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { background: linear-gradient(135deg, #0a0f1e, #0f1629); font-family: Arial, sans-serif; padding: 16px; color: white; }
            .container { max-width: 480px; margin: 0 auto; background: rgba(10,15,30,0.85); border-radius: 28px; border: 1px solid #ffd700; overflow: hidden; }
            .header { background: linear-gradient(135deg, #1a1f2e, #0d1225); padding: 20px; text-align: center; border-bottom: 2px solid #ffd700; }
            .title { font-size: 22px; font-weight: bold; background: linear-gradient(45deg, #ffd700, #ff6b6b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .balance-box { background: rgba(0,0,0,0.5); border-radius: 20px; padding: 12px; margin-top: 12px; }
            .balance-amount { font-size: 38px; font-weight: bold; color: #ffd700; }
            .game-nav { display: grid; grid-template-columns: repeat(5,1fr); gap:5px; padding:15px; background:rgba(0,0,0,0.3); }
            .game-btn { background:rgba(255,255,255,0.08); border:none; padding:10px; border-radius:16px; color:#aaa; cursor:pointer; text-align:center; }
            .game-btn.active { background:linear-gradient(135deg,#ffd700,#ff8c00); color:#000; }
            .game-area { padding:20px; }
            .crash-multiplier { font-size:64px; text-align:center; color:#ffd700; margin:20px 0; }
            .bet-input { width:100%; background:rgba(0,0,0,0.5); border:1px solid #ffd700; padding:14px; border-radius:16px; color:white; font-size:18px; text-align:center; margin-bottom:12px; }
            .bet-presets { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:16px; }
            .preset-btn { background:rgba(255,255,255,0.08); border:none; padding:10px; border-radius:12px; color:#ffd700; cursor:pointer; }
            .action-btn { width:100%; background:linear-gradient(135deg,#ffd700,#ff8c00); border:none; padding:16px; border-radius:20px; font-size:18px; font-weight:bold; color:#000; cursor:pointer; }
            .slots-reels { display:flex; justify-content:center; gap:15px; margin:30px 0; }
            .slot-reel { width:80px; height:80px; background:rgba(0,0,0,0.6); border-radius:18px; display:flex; align-items:center; justify-content:center; font-size:48px; border:2px solid #ffd700; }
            .roulette-number { width:90px; height:90px; background:radial-gradient(circle,#ffd700,#ff8c00); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:38px; margin:20px auto; }
            .numbers-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:8px; margin:20px 0; }
            .num-btn { background:rgba(255,255,255,0.08); border:none; padding:12px; border-radius:12px; color:white; cursor:pointer; text-align:center; }
            .num-btn.selected { background:#ffd700; color:#000; }
            .wheel-container { text-align:center; margin:20px 0; }
            canvas { box-shadow:0 0 20px rgba(255,215,0,0.3); border-radius:50%; }
            .history-section { padding:15px; border-top:1px solid rgba(255,215,0,0.2); max-height:160px; overflow-y:auto; }
            .history-item { background:rgba(255,255,255,0.04); padding:8px; margin:4px 0; border-radius:10px; font-size:11px; display:flex; justify-content:space-between; }
            .win-text { color:#4caf50; }
            .lose-text { color:#ff4757; }
            @media (max-width:480px){ .slot-reel{ width:65px; height:65px; font-size:40px; } }
        </style>
    </head>
    <body>
    <div class="container">
        <div class="header"><div class="title">🐐 БУРМАЛДАТОЕ CASINO 🐐</div><div class="balance-box"><div>БАЛАНС:</div><div class="balance-amount" id="balance">0</div></div></div>
        <div class="game-nav">
            <button class="game-btn active" data-game="crash">💥 CRASH</button>
            <button class="game-btn" data-game="slots">🎰 Слоты</button>
            <button class="game-btn" data-game="roulette">🎡 Рулетка</button>
            <button class="game-btn" data-game="wheel">🎲 Колесо</button>
            <button class="game-btn" data-game="promo">🎁 Промо</button>
        </div>
        <div class="game-area" id="gameArea">
            <div id="crashGame">
                <div class="crash-multiplier" id="currentMult">1.00x</div>
                <input type="number" id="betAmount" class="bet-input" placeholder="СТАВКА" value="100">
                <div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div>
                <button class="action-btn" id="placeBetBtn">💰 СДЕЛАТЬ СТАВКУ</button>
                <div class="bet-status" id="betStatus"></div>
            </div>
            <div id="slotsGame" style="display:none"><div class="slots-reels"><div class="slot-reel" id="slot1">🍒</div><div class="slot-reel" id="slot2">🍋</div><div class="slot-reel" id="slot3">🍊</div></div><input type="number" id="slotsBet" class="bet-input" placeholder="СТАВКА" value="100"><div class="bet-presets"><button class="preset-btn" data-bet="100">Min</button><button class="preset-btn" data-bet="1000">1K</button><button class="preset-btn" data-bet="5000">5K</button><button class="preset-btn" data-bet="max">Max</button></div><button class="action-btn" id="slotsSpinBtn">🎰 КРУТИТЬ</button></div>
            <div id="rouletteGame" style="display:none"><div class="roulette-number" id="rouletteResult">?</div><div class="numbers-grid" id="rouletteNumbers"></div><input type="number" id="rouletteBet" class="bet-input" placeholder="СТАВКА" value="100"><button class="action-btn" id="rouletteSpinBtn">🎡 КРУТИТЬ</button></div>
            <div id="wheelGame" style="display:none"><div class="wheel-container"><canvas id="wheelCanvas" width="240" height="240"></canvas></div><input type="number" id="wheelBet" class="bet-input" placeholder="СТАВКА" value="100"><button class="action-btn" id="wheelSpinBtn">🎲 КРУТИТЬ</button></div>
            <div id="promoGame" style="display:none"><div style="text-align:center; padding:40px;"><div style="font-size:64px;">🎁</div><div>ЕЖЕДНЕВНЫЙ БОНУС</div><div style="font-size:12px; color:#aaa;">от 100 до 100 000 ₽ каждые 10 мин</div><button class="action-btn" id="promoBonusBtn">🎁 ПОЛУЧИТЬ БОНУС</button></div></div>
        </div>
        <div class="history-section"><div class="history-title">📜 ИСТОРИЯ ИГР</div><div id="historyList"></div></div>
    </div>
    <script>
        const urlParams = new URLSearchParams(window.location.search);
        let tgId = urlParams.get('tg_id');
        let currentBalance = 0;
        let isSpinning = false, selectedNum = null;
        const symbols = ['🍒','🍋','🍊','🔔','💎','7️⃣'];
        const wheelSegments = [{mult:0,color:'#f44336'},{mult:1.5,color:'#ff9800'},{mult:0,color:'#f44336'},{mult:2,color:'#4caf50'},{mult:0,color:'#f44336'},{mult:3,color:'#2196f3'},{mult:0,color:'#f44336'},{mult:5,color:'#9c27b0'}];
        let wheelCanvas=null, wheelCtx=null, currentAngle=0;
        
        async function loadBalance(){
            if(!tgId) return;
            let res=await fetch('/api/balance',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId})});
            let data=await res.json();
            currentBalance=data.balance;
            document.getElementById('balance').innerText=currentBalance.toLocaleString();
        }
        async function updateBalance(amount){
            if(!tgId) return;
            let res=await fetch('/api/update_balance',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:tgId,amount:amount})});
            let data=await res.json();
            currentBalance=data.balance;
            document.getElementById('balance').innerText=currentBalance.toLocaleString();
            return currentBalance;
        }
        async function placeBet(){
            if(!tgId){alert('Привяжите Telegram!');return;}
            let bet=parseInt(document.getElementById('betAmount').value);
            if(bet<10||bet>currentBalance){alert('Ошибка ставки!');return;}
            await updateBalance(-bet);
            let result = Math.random();
            let win = 0;
            if(result < 0.05){
                win = bet * 10;
                alert('🏆 ДЖЕКПОТ! +'+win+' ₽');
            }else if(result < 0.15){
                win = bet * 3;
                alert('🎉 ВЫИГРЫШ! +'+win+' ₽');
            }else if(result < 0.3){
                win = bet * 2;
                alert('👍 ВЫИГРЫШ! +'+win+' ₽');
            }else{
                alert('❌ ПРОИГРЫШ! -'+bet+' ₽');
            }
            if(win>0) await updateBalance(win);
            addHistory('CRASH',bet,win-bet,win>0?'Выигрыш':'Проигрыш');
        }
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
        function setMaxBet(){if(currentBalance>0)document.getElementById('betAmount').value=currentBalance;}
        function setSlotsMaxBet(){if(currentBalance>0)document.getElementById('slotsBet').value=currentBalance;}
        function setRouletteMaxBet(){if(currentBalance>0)document.getElementById('rouletteBet').value=currentBalance;}
        function setWheelMaxBet(){if(currentBalance>0)document.getElementById('wheelBet').value=currentBalance;}
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
        document.getElementById('slotsSpinBtn').onclick=spinSlots;
        document.getElementById('rouletteSpinBtn').onclick=spinRoulette;
        document.getElementById('wheelSpinBtn').onclick=spinWheel;
        document.getElementById('promoBonusBtn').onclick=getBonus;
        if(tgId)loadBalance();
        initRoulette();
        drawWheel();
    </script>
    </body>
    </html>
    '''

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

# ========== ЗАПУСК ==========
def run_bot():
    print("🤖 БОТ ЗАПУЩЕН")
    bot.infinity_polling()

if __name__ == '__main__':
    print("="*40)
    print("🐐 БУРМАЛДАТОЕ CASINO")
    print("="*40)
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    app.run(host='0.0.0.0', port=WEB_PORT)

