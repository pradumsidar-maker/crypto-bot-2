import os
import time
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

# 🔥 Futures Coins
COINS = [
    "BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT",
    "DOGEUSDT","ADAUSDT","TRXUSDT","LINKUSDT","MATICUSDT",
    "LTCUSDT","DOTUSDT","BCHUSDT","AVAXUSDT","UNIUSDT",
    "ATOMUSDT","XLMUSDT","ETCUSDT","FILUSDT","APTUSDT"
]

# 🧠 Tracking
hl_triggered = {}
oc_triggered = {}

tz = pytz.timezone("Asia/Kolkata")

# 🔄 Futures price
def get_price(symbol):
    url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    return float(requests.get(url).json()["price"])

# 🔄 Weekly data (Binance klines)
def get_weekly_levels(symbol):
    url = f"https://fapi.binance.com/fapi/v1/klines"
    params = {
        "symbol": symbol,
        "interval": "1w",
        "limit": 2
    }
    data = requests.get(url, params=params).json()

    prev = data[0]

    open_p = float(prev[1])
    high = float(prev[2])
    low = float(prev[3])
    close = float(prev[4])

    return open_p, high, low, close

# 📩 Send message
async def send(msg):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        print("Sent:", msg)
    except Exception as e:
        print("Error:", e)

# 🗓️ Week key
def week_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.isocalendar()[1]}"

# 🚀 MAIN LOGIC
async def run_bot():
    while True:
        wk = week_key()

        for coin in COINS:
            try:
                price = get_price(coin)
                open_p, high, low, close = get_weekly_levels(coin)

                key1 = f"{coin}-{wk}-hl"
                key2 = f"{coin}-{wk}-oc"

                # 🔔 1: HIGH / LOW
                if price >= high and not hl_triggered.get(key1):
                    await send(f"🚀 {coin} HIGH TOUCH\nPrice: {round(price,2)} USDT")
                    hl_triggered[key1] = True

                elif price <= low and not hl_triggered.get(key1):
                    await send(f"🔻 {coin} LOW TOUCH\nPrice: {round(price,2)} USDT")
                    hl_triggered[key1] = True

                # 🔔 2: OPEN / CLOSE (after HL)
                if hl_triggered.get(key1) and not oc_triggered.get(key2):

                    if abs(price - open_p) / open_p < 0.001:
                        await send(f"📊 {coin} OPEN TOUCH\nPrice: {round(price,2)} USDT")
                        oc_triggered[key2] = True

                    elif abs(price - close) / close < 0.001:
                        await send(f"📊 {coin} CLOSE TOUCH\nPrice: {round(price,2)} USDT")
                        oc_triggered[key2] = True

            except Exception as e:
                print("Error:", coin, e)

        await asyncio.sleep(60)

# 🌐 Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Futures bot running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ▶️ Start
def start():
    asyncio.run(run_bot())

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    start()
