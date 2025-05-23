import telebot
from telebot import types
from datetime import datetime, timedelta
import requests
from config import TELEGRAM_TOKEN, ADMIN_ID, PRICING, WELCOME_MESSAGE, COINMARKETCAP_API_KEY

bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_subscriptions = {}

def is_subscribed(user_id):
    if user_id == ADMIN_ID:
        return True
    expiry = user_subscriptions.get(user_id)
    return expiry and datetime.now() < expiry

def get_signal(symbol):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY}
    params = {'symbol': symbol.upper(), 'convert': 'USDT'}

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        price = data["data"][symbol.upper()]["quote"]["USDT"]["price"]
        return {
            "entry": round(price, 2),
            "sl": round(price * 0.985, 2),
            "tp1": round(price * 1.01, 2),
            "tp2": round(price * 1.015, 2),
            "tp3": round(price * 1.02, 2),
            "leverage": "5x"
        }
    except Exception as e:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, WELCOME_MESSAGE, parse_mode='Markdown')

@bot.message_handler(commands=['menu'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("دریافت سیگنال", "خرید اشتراک", "ارتباط با ادمین")
    bot.send_message(message.chat.id, "یکی از گزینه‌ها را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "خرید اشتراک")
def show_subscriptions(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("ماهانه", "شش ماهه", "سالانه")
    bot.send_message(message.chat.id, "نوع اشتراک را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in ['ماهانه', 'شش ماهه', 'سالانه'])
def buy_subscription(message):
    duration_map = {
        'ماهانه': ('monthly', 30),
        'شش ماهه': ('6months', 180),
        'سالانه': ('yearly', 365)
    }
    key, days = duration_map[message.text]
    amount = PRICING[key]['amount']
    expiry = datetime.now() + timedelta(days=days)
    user_subscriptions[message.from_user.id] = expiry
    bot.send_message(message.chat.id, f"✅ اشتراک شما برای {days} روز فعال شد.")

@bot.message_handler(func=lambda msg: msg.text == "دریافت سیگنال")
def signal_menu(message):
    if not is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, "اشتراک ندارید. لطفاً از منو، اشتراک تهیه کنید.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("هوشمند", "دستی")
    bot.send_message(message.chat.id, "نوع سیگنال را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "هوشمند")
def smart_signal(message):
    signal = get_signal("BTC")
    if signal:
        msg = f"BTC BUY\nENTRY: {signal['entry']}\nSL: {signal['sl']}\nTP1: {signal['tp1']}\nTP2: {signal['tp2']}\nTP3: {signal['tp3']}\nLeverage: {signal['leverage']}"
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, "دریافت سیگنال ممکن نیست.")

@bot.message_handler(func=lambda msg: msg.text == "دستی")
def ask_symbol(message):
    msg = bot.send_message(message.chat.id, "نماد ارز را وارد کنید (مثلاً ETH):")
    bot.register_next_step_handler(msg, send_custom_signal)

def send_custom_signal(message):
    symbol = message.text.upper()
    signal = get_signal(symbol)
    if signal:
        msg = f"{symbol} BUY\nENTRY: {signal['entry']}\nSL: {signal['sl']}\nTP1: {signal['tp1']}\nTP2: {signal['tp2']}\nTP3: {signal['tp3']}\nLeverage: {signal['leverage']}"
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, "نماد نامعتبر یا خطا در دریافت سیگنال.")

bot.infinity_polling()
