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

# 🔥 COINS
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
LAST_FILE = "last_run.txt"

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

def week_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.isocalendar()[1]}"

def day_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.month}-{now.day}"

# 📊 API
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

# 🚀 MAIN BOT
async def run_bot():
    await send("✅ Bot STARTED 🚀")

    while True:
        try:
            wk = week_key()
            dk = day_key()

            for coin in COINS:
                try:
                    price = get_price(coin)

                    # 🔹 WEEKLY
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

                    # 🔹 DAILY
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

# 🌐 Flask (keep alive)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running 🚀"

@app.route("/ping")
def ping():
    return "pong"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# ▶️ START
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    asyncio.run(run_bot())
