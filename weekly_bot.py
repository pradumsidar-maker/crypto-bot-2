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
    return {"hl": {}, "oc": {}}

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

async def heartbeat_alert():
    while True:
        await send("🟢 BOT LIVE (6h check) ✅")
        await asyncio.sleep(21600)

def week_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.isocalendar()[1]}"

def day_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.month}-{now.day}"

def get_weekly_levels(symbol):
    url = "https://fapi.binance.com/fapi/v1/klines"
    data = requests.get(url, params={"symbol": symbol, "interval": "1w", "limit": 2}).json()
    prev = data[0]
    return float(prev[1]), float(prev[2]), float(prev[3]), float(prev[4])

def get_daily_levels(symbol):
    url = "https://fapi.binance.com/fapi/v1/klines"
    data = requests.get(url, params={"symbol": symbol, "interval": "1d", "limit": 2}).json()
    prev = data[0]
    return float(prev[1]), float(prev[2]), float(prev[3]), float(prev[4])

async def run_bot():
    await send("✅ Bot STARTED 🚀")
    asyncio.create_task(heartbeat_alert())

    wk = week_key()
    dk = day_key()

    # 🔥 MISSED ALERT (TOUCH BASED)
    for coin in COINS:
        try:
            url = "https://fapi.binance.com/fapi/v1/klines"

            # ===== WEEKLY =====
            w_open, w_high, w_low, w_close = get_weekly_levels(coin)
            w_data = requests.get(url, params={"symbol": coin, "interval": "1w", "limit": 1}).json()[0]

            week_high_now = float(w_data[2])
            week_low_now = float(w_data[3])

            w_key = f"{coin}-{wk}-w"

            if not state["hl"].get(w_key):

                if week_low_now <= w_high <= week_high_now:
                    await send(f"🚨 {coin} PREV WEEK HIGH TOUCHED")

                if week_low_now <= w_low <= week_high_now:
                    await send(f"🚨 {coin} PREV WEEK LOW TOUCHED")

                if week_low_now <= w_open <= week_high_now:
                    await send(f"📊 {coin} PREV WEEK OPEN TOUCHED")

                if week_low_now <= w_close <= week_high_now:
                    await send(f"📊 {coin} PREV WEEK CLOSE TOUCHED")

                state["hl"][w_key] = True

            # ===== DAILY =====
            d_open, d_high, d_low, d_close = get_daily_levels(coin)
            d_data = requests.get(url, params={"symbol": coin, "interval": "1d", "limit": 1}).json()[0]

            today_high = float(d_data[2])
            today_low = float(d_data[3])

            d_key = f"{coin}-{dk}-d"

            if not state["hl"].get(d_key):

                if today_low <= d_high <= today_high:
                    await send(f"🚨 {coin} PREV DAY HIGH TOUCHED")

                if today_low <= d_low <= today_high:
                    await send(f"🚨 {coin} PREV DAY LOW TOUCHED")

                if today_low <= d_open <= today_high:
                    await send(f"📊 {coin} PREV DAY OPEN TOUCHED")

                if today_low <= d_close <= today_high:
                    await send(f"📊 {coin} PREV DAY CLOSE TOUCHED")

                state["hl"][d_key] = True

        except Exception as e:
            print("History Error:", coin, e)

    # 🔥 MAIN LOOP
    while True:
        try:
            wk = week_key()
            dk = day_key()

            for coin in COINS:
                try:
                    url = "https://fapi.binance.com/fapi/v1/klines"

                    # ===== WEEKLY =====
                    w_open, w_high, w_low, w_close = get_weekly_levels(coin)
                    w_data = requests.get(url, params={"symbol": coin, "interval": "1w", "limit": 1}).json()[0]

                    week_high_now = float(w_data[2])
                    week_low_now = float(w_data[3])

                    key_w = f"{coin}-{wk}-touch"

                    if not state["hl"].get(key_w):

                        if week_low_now <= w_high <= week_high_now:
                            await send(f"🚀 {coin} WEEKLY HIGH TOUCHED")

                        if week_low_now <= w_low <= week_high_now:
                            await send(f"🔻 {coin} WEEKLY LOW TOUCHED")

                        if week_low_now <= w_open <= week_high_now:
                            await send(f"📊 {coin} WEEKLY OPEN TOUCHED")

                        if week_low_now <= w_close <= week_high_now:
                            await send(f"📊 {coin} WEEKLY CLOSE TOUCHED")

                        state["hl"][key_w] = True

                    # ===== DAILY =====
                    d_open, d_high, d_low, d_close = get_daily_levels(coin)
                    d_data = requests.get(url, params={"symbol": coin, "interval": "1d", "limit": 1}).json()[0]

                    today_high = float(d_data[2])
                    today_low = float(d_data[3])

                    key_d = f"{coin}-{dk}-touch"

                    if not state["hl"].get(key_d):

                        if today_low <= d_high <= today_high:
                            await send(f"🚀 {coin} DAILY HIGH TOUCHED")

                        if today_low <= d_low <= today_high:
                            await send(f"🔻 {coin} DAILY LOW TOUCHED")

                        if today_low <= d_open <= today_high:
                            await send(f"📊 {coin} DAILY OPEN TOUCHED")

                        if today_low <= d_close <= today_high:
                            await send(f"📊 {coin} DAILY CLOSE TOUCHED")

                        state["hl"][key_d] = True

                except Exception as e:
                    print("Coin Error:", coin, e)

            save_state(state)
            await asyncio.sleep(120)

        except Exception as e:
            print("Main Error:", e)
            await asyncio.sleep(10)

# 🌐 Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running 🚀"

@app.route("/ping")
def ping():
    return "pong"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    asyncio.run(run_bot())
