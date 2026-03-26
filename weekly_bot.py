import os
import threading
import asyncio
import requests
from datetime import datetime
import pytz
from flask import Flask
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# 🔥 TOP 20 FUTURES COINS
COINS = [
"BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT",
"ADAUSDT","DOGEUSDT","TRXUSDT","LINKUSDT","MATICUSDT",
"DOTUSDT","LTCUSDT","BCHUSDT","AVAXUSDT","UNIUSDT",
"ATOMUSDT","XLMUSDT","ETCUSDT","FILUSDT","APTUSDT"
]

hl_triggered = {}
oc_triggered = {}

tz = pytz.timezone("Asia/Kolkata")

# 🔄 Futures Price
def get_price(symbol):
    url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    return float(requests.get(url).json()["price"])

# 🔄 Weekly Levels
def get_weekly_levels(symbol):
    url = f"https://fapi.binance.com/fapi/v1/klines"
    params = {"symbol": symbol, "interval": "1w", "limit": 2}
    data = requests.get(url, params=params).json()

    prev = data[0]

    return float(prev[1]), float(prev[2]), float(prev[3]), float(prev[4])

# 📩 Telegram Send
async def send(msg):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        print("Sent:", msg)
    except Exception as e:
        print("Telegram Error:", e)

# 🗓️ Week Key
def week_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.isocalendar()[1]}"

# 🚀 MAIN BOT
async def run_bot():
    await send("✅ Futures Bot Started 🚀")

    while True:
        wk = week_key()

        for coin in COINS:
            try:
                price = get_price(coin)
                open_p, high, low, close = get_weekly_levels(coin)

                key1 = f"{coin}-{wk}-hl"
                key2 = f"{coin}-{wk}-oc"

                print(f"{coin} Price: {price}")

                # 🔔 HIGH / LOW ALERT
                if price >= high and not hl_triggered.get(key1):
                    await send(f"🚀 {coin} HIGH BREAKOUT\nPrice: {price} USDT")
                    hl_triggered[key1] = True

                elif price <= low and not hl_triggered.get(key1):
                    await send(f"🔻 {coin} LOW BREAKDOWN\nPrice: {price} USDT")
                    hl_triggered[key1] = True

                # 🔔 OPEN / CLOSE ALERT (after HL)
                if hl_triggered.get(key1) and not oc_triggered.get(key2):

                    if abs(price - open_p) / open_p < 0.01:
                        await send(f"📊 {coin} OPEN TOUCH\nPrice: {price} USDT")
                        oc_triggered[key2] = True

                    elif abs(price - close) / close < 0.01:
                        await send(f"📊 {coin} CLOSE TOUCH\nPrice: {price} USDT")
                        oc_triggered[key2] = True

            except Exception as e:
                print("Error:", coin, e)

        await asyncio.sleep(120)  # 🔥 Free plan optimized

# 🌐 Flask (Render ke liye)
app = Flask(__name__)

@app.route("/")
def home():
    return "Futures Bot Running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ▶️ START
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    asyncio.run(run_bot())
