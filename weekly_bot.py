import os
import threading
import asyncio
import requests
import json
from datetime import datetime
import pytz
from flask import Flask
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

COINS = [
"BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT",
"ADAUSDT","DOGEUSDT","TRXUSDT","LINKUSDT","MATICUSDT",
"DOTUSDT","LTCUSDT","BCHUSDT","AVAXUSDT","UNIUSDT",
"ATOMUSDT","XLMUSDT","ETCUSDT","FILUSDT","APTUSDT",
"NEARUSDT","ICPUSDT","HBARUSDT","ARBUSDT","OPUSDT",
"SANDUSDT","MANAUSDT","AXSUSDT","EGLDUSDT","THETAUSDT",
"FLOWUSDT","XTZUSDT","GRTUSDT","CHZUSDT","CRVUSDT",
"DYDXUSDT","1INCHUSDT","ZILUSDT","ENJUSDT","FTMUSDT",
"LDOUSDT","STXUSDT","GMXUSDT","IMXUSDT","RNDRUSDT",
"BLURUSDT","PEPEUSDT","ALGOUSDT"
]

tz = pytz.timezone("Asia/Kolkata")
STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

state = load_state()

async def send(msg):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        await asyncio.sleep(1)
    except Exception as e:
        print("Telegram Error:", e)

async def heartbeat():
    while True:
        await send("🟢 BOT LIVE ✅")
        await asyncio.sleep(21600)

def day_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.month}-{now.day}"

def week_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.isocalendar()[1]}"

# 🔥 GET PREVIOUS LEVELS
def get_levels(symbol, interval):
    url = "https://fapi.binance.com/fapi/v1/klines"
    data = requests.get(url, params={"symbol": symbol, "interval": interval, "limit": 2}).json()
    prev = data[0]
    return float(prev[1]), float(prev[2]), float(prev[3]), float(prev[4])

# 🔥 LIVE PRICE
def get_price(symbol):
    url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    return float(requests.get(url).json()["price"])

# 🔥 TOUCH LOGIC (0.2% tolerance)
def touched(price, level):
    return abs(price - level) / level < 0.002

async def check_coin(coin):
    try:
        dk = day_key()
        wk = week_key()

        price = get_price(coin)

        # ===== DAILY =====
        d_open, d_high, d_low, d_close = get_levels(coin, "1d")

        levels_d = {
            "HIGH": d_high,
            "LOW": d_low,
            "OPEN": d_open,
            "CLOSE": d_close
        }

        for name, lvl in levels_d.items():
            key = f"{coin}-{dk}-D-{name}"
            if touched(price, lvl) and not state.get(key):
                await send(f"🚨 {coin} DAILY {name} TOUCHED\nPrice: {price}")
                state[key] = True

        # ===== WEEKLY =====
        w_open, w_high, w_low, w_close = get_levels(coin, "1w")

        levels_w = {
            "HIGH": w_high,
            "LOW": w_low,
            "OPEN": w_open,
            "CLOSE": w_close
        }

        for name, lvl in levels_w.items():
            key = f"{coin}-{wk}-W-{name}"
            if touched(price, lvl) and not state.get(key):
                await send(f"📊 {coin} WEEKLY {name} TOUCHED\nPrice: {price}")
                state[key] = True

    except Exception as e:
        print("Error:", coin, e)

async def run_bot():
    await send("🚀 BOT STARTED")

    asyncio.create_task(heartbeat())

    while True:
        tasks = [check_coin(c) for c in COINS]
        await asyncio.gather(*tasks)
        save_state(state)
        await asyncio.sleep(30)   # 🔥 fast checking

# Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running 🚀"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    asyncio.run(run_bot())
