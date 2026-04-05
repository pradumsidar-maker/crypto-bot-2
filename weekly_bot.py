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

# 🔥 RESET DAILY (NO REPEAT, NO MISS)
def reset_state_if_new_day():
    today = day_key()
    new_hl = {}
    new_oc = {}

    for key in state["hl"]:
        if today in key:
            new_hl[key] = True

    for key in state["oc"]:
        if today in key:
            new_oc[key] = True

    state["hl"] = new_hl
    state["oc"] = new_oc

    save_state(state)

async def send(msg):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        await asyncio.sleep(1)
    except Exception as e:
        print("Telegram Error:", e)

# 🔥 6H HEARTBEAT
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

def get_price(symbol):
    url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    return float(requests.get(url).json()["price"])

def get_weekly_levels(symbol):
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {"symbol": symbol, "interval": "1w", "limit": 2}
    data = requests.get(url, params=params).json()
    prev = data[0]
    return float(prev[1]), float(prev[2]), float(prev[3]), float(prev[4])

def get_daily_levels(symbol):
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {"symbol": symbol, "interval": "1d", "limit": 2}
    data = requests.get(url, params=params).json()
    prev = data[0]
    return float(prev[1]), float(prev[2]), float(prev[3]), float(prev[4])

async def run_bot():
    await send("✅ Bot STARTED 🚀")
    # ================= DAILY MISSED ALERT =================

d_open, d_high, d_low, d_close = get_daily_levels(coin)

d_data = requests.get(url, params={"symbol": coin, "interval": "1d", "limit": 1}).json()[0]

today_high = float(d_data[2])
today_low = float(d_data[3])

d_key = f"{coin}-{dk}-history-d"

if not state["hl"].get(d_key):

    if today_high >= d_high:
        await send(f"🚨 {coin} PREV DAY HIGH TOUCHED (missed)")

    if today_low <= d_low:
        await send(f"🚨 {coin} PREV DAY LOW TOUCHED (missed)")

    if today_low <= d_open <= today_high:
        await send(f"🚨 {coin} PREV DAY OPEN TOUCHED (missed)")

    if today_low <= d_close <= today_high:
        await send(f"🚨 {coin} PREV DAY CLOSE TOUCHED (missed)")

    state["hl"][d_key] = True
    
# ================= DAILY MISSED ALERT =================

d_open, d_high, d_low, d_close = get_daily_levels(coin)

d_data = requests.get(url, params={"symbol": coin, "interval": "1d", "limit": 1}).json()[0]

today_high = float(d_data[2])
today_low = float(d_data[3])

d_key = f"{coin}-{dk}-history-d"

if not state["hl"].get(d_key):

    if today_high >= d_high:
        await send(f"🚨 {coin} PREV DAY HIGH TOUCHED (missed)")

    if today_low <= d_low:
        await send(f"🚨 {coin} PREV DAY LOW TOUCHED (missed)")

    if today_low <= d_open <= today_high:
        await send(f"🚨 {coin} PREV DAY OPEN TOUCHED (missed)")

    if today_low <= d_close <= today_high:
        await send(f"🚨 {coin} PREV DAY CLOSE TOUCHED (missed)")

    state["hl"][d_key] = True
    asyncio.create_task(heartbeat_alert())

    # 🔥 RESET STATE
    reset_state_if_new_day()

    # 🔥 HISTORY CHECK (NO MISS)
    wk = week_key()
    dk = day_key()

    for coin in COINS:
        try:
            price = get_price(coin)
            url = "https://fapi.binance.com/fapi/v1/klines"

            # WEEKLY
            w_open, w_high, w_low, w_close = get_weekly_levels(coin)
            w_data = requests.get(url, params={"symbol": coin, "interval": "1w", "limit": 1}).json()[0]
            week_high_now = float(w_data[2])
            week_low_now = float(w_data[3])

            w_key = f"{coin}-{wk}-history-w"

            if not state["hl"].get(w_key):
                if price >= w_high * 0.998 or week_high_now >= w_high:
                    await send(f"🚨 {coin} TOUCHED PREV WEEK HIGH")
                if price <= w_low * 1.002 or week_low_now <= w_low:
                    await send(f"🚨 {coin} TOUCHED PREV WEEK LOW")
                if week_low_now <= w_open <= week_high_now:
                    await send(f"🚨 {coin} TOUCHED PREV WEEK OPEN")
                if week_low_now <= w_close <= week_high_now:
                    await send(f"🚨 {coin} TOUCHED PREV WEEK CLOSE")

                state["hl"][w_key] = True

            # DAILY
            d_open, d_high, d_low, d_close = get_daily_levels(coin)
            d_data = requests.get(url, params={"symbol": coin, "interval": "1d", "limit": 1}).json()[0]
            today_high = float(d_data[2])
            today_low = float(d_data[3])

            d_key = f"{coin}-{dk}-history-d"

            if not state["hl"].get(d_key):
                if price >= d_high * 0.998 or today_high >= d_high:
                    await send(f"🚨 {coin} TOUCHED PREV DAY HIGH")
                if price <= d_low * 1.002 or today_low <= d_low:
                    await send(f"🚨 {coin} TOUCHED PREV DAY LOW")
                if today_low <= d_open <= today_high:
                    await send(f"🚨 {coin} TOUCHED PREV DAY OPEN")
                if today_low <= d_close <= today_high:
                    await send(f"🚨 {coin} TOUCHED PREV DAY CLOSE")

                state["hl"][d_key] = True

        except Exception as e:
            print("History Error:", coin, e)

    # 🔥 ORIGINAL LOOP
    while True:
        try:
            wk = week_key()
            dk = day_key()

            for coin in COINS:
                try:
                    price = get_price(coin)

                    open_p, high, low, close = get_weekly_levels(coin)
                    key1 = f"{coin}-{wk}-hl"
                    key2 = f"{coin}-{wk}-oc"

                    if not state["hl"].get(key1):
                        if price >= high:
                            await send(f"🚀 {coin} WEEKLY BREAKOUT\nPrice: {price}")
                            state["hl"][key1] = True
                        elif price <= low:
                            await send(f"🔻 {coin} WEEKLY BREAKDOWN\nPrice: {price}")
                            state["hl"][key1] = True

                    if state["hl"].get(key1) and not state["oc"].get(key2):
                        if abs(price - open_p)/open_p < 0.01:
                            await send(f"📊 {coin} WEEKLY OPEN TOUCH")
                            state["oc"][key2] = True
                        elif abs(price - close)/close < 0.01:
                            await send(f"📊 {coin} WEEKLY CLOSE TOUCH")
                            state["oc"][key2] = True

                    d_open, d_high, d_low, d_close = get_daily_levels(coin)
                    d_key1 = f"{coin}-{dk}-hl"
                    d_key2 = f"{coin}-{dk}-oc"

                    if not state["hl"].get(d_key1):
                        if price >= d_high:
                            await send(f"🟡 {coin} DAILY BREAKOUT\nPrice: {price}")
                            state["hl"][d_key1] = True
                        elif price <= d_low:
                            await send(f"🟡 {coin} DAILY BREAKDOWN\nPrice: {price}")
                            state["hl"][d_key1] = True

                    if state["hl"].get(d_key1) and not state["oc"].get(d_key2):
                        if abs(price - d_open)/d_open < 0.01:
                            await send(f"📊 {coin} DAILY OPEN TOUCH")
                            state["oc"][d_key2] = True
                        elif abs(price - d_close)/d_close < 0.01:
                            await send(f"📊 {coin} DAILY CLOSE TOUCH")
                            state["oc"][d_key2] = True

                except Exception as e:
                    print("Coin Error:", coin, e)

            save_state(state)
            await asyncio.sleep(120)

        except Exception as e:
            print("Main Error:", e)
            await asyncio.sleep(10)

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
