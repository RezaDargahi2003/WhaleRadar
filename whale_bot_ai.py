from config import CMC_API_KEY, TELEGRAM_TOKEN, ADMIN_ID, ADMIN_USERNAME, USDT_WALLET, WEBHOOK_URL, PORT
import telebot
from telebot import types
import requests
from signal_generator import generate_signal
import flask
from flask import request

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = flask.Flask(__name__)
subscriptions = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("دریافت سیگنال", "خرید اشتراک")
    markup.row("تماس با ادمین")
    bot.send_message(message.chat.id, "به ربات رادار نهنگ‌ها خوش آمدید!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "تماس با ادمین")
def contact_admin(message):
    bot.send_message(message.chat.id, f"آیدی ادمین: @{ADMIN_USERNAME}")

@bot.message_handler(func=lambda m: m.text == "خرید اشتراک")
def subscription_options(message):
    bot.send_message(message.chat.id,
    "پلن اشتراک را انتخاب کنید:\n1. ماهانه: ۵۰ تتر\n2. شش ماهه: ۲۰۰ تتر\n3. سالانه: ۳۰۰ تتر\n\nآدرس تتر (TRC20):\n" + USDT_WALLET)

@bot.message_handler(func=lambda m: m.text == "دریافت سیگنال")
def get_signal(message):
    user_id = message.chat.id
    if user_id == ADMIN_ID or subscriptions.get(user_id, False):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("ارسال سیگنال دستی", "سیگنال هوشمند")
        bot.send_message(user_id, "نوع سیگنال را انتخاب کنید:", reply_markup=markup)
    else:
        bot.send_message(user_id, "شما اشتراک فعال ندارید. ابتدا اشتراک تهیه کنید.")

@bot.message_handler(func=lambda m: m.text == "سیگنال هوشمند")
def send_smart_signal(message):
    symbol = "BTC"
    signal = generate_signal(symbol, CMC_API_KEY)
    bot.send_message(message.chat.id, signal)

@bot.message_handler(func=lambda m: m.text == "ارسال سیگنال دستی")
def manual_signal(message):
    bot.send_message(message.chat.id, "نماد را وارد کنید (مثال: ETH):")
    bot.register_next_step_handler(message, handle_manual_symbol)

def handle_manual_symbol(message):
    symbol = message.text.upper()
    signal = generate_signal(symbol, CMC_API_KEY, manual=True)
    bot.send_message(message.chat.id, signal)

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    return 'Bot is running.'

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    app.run(host="0.0.0.0", port=PORT)
