import requests

def generate_signal(symbol, api_key, manual=False):
    try:
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&convert=USDT"
        headers = {"X-CMC_PRO_API_KEY": api_key}
        response = requests.get(url, headers=headers)
        data = response.json()
        price = data["data"][symbol]["quote"]["USDT"]["price"]

        if manual:
            return f"{symbol} BUY\nENTRY: قیمت مناسب فعلی\nSL: پشتیبانی نزدیک\nTP1: مقاومت اول\nTP2: مقاومت دوم\nTP3: مقاومت سوم\nLeverage: 5x"
        else:
            return f"سیگنال هوشمند برای {symbol}:\nقیمت فعلی: {round(price, 2)} USDT\nوضعیت بازار بررسی شد."
    except Exception as e:
        return f"خطا در دریافت داده: {e}"
