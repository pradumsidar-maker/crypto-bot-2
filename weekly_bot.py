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

# 🔥 TOP 50 COINS
COINS = [
"BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT",
"ADAUSDT","DOGEUSDT","TRXUSDT","LINKUSDT","MATICUSDT",
"DOTUSDT","LTCUSDT","BCHUSDT","AVAXUSDT","UNIUSDT",
"ATOMUSDT","XLMUSDT","ETCUSDT","FILUSDT","APTUSDT",

# +30 more
"NEARUSDT","ICPUSDT","HBARUSDT","ARBUSDT","OPUSDT",
"SANDUSDT","MANAUSDT","AXSUSDT","EGLDUSDT","THETAUSDT",
"FLOWUSDT","XTZUSDT","KLAYUSDT","GRTUSDT","CHZUSDT",
"CRVUSDT","DYDXUSDT","1INCHUSDT","ZILUSDT","ENJUSDT",
"BATUSDT","HOTUSDT","FTMUSDT","RNDRUSDT","LDOUSDT",
"STXUSDT","GMXUSDT","IMXUSDT","BLURUSDT","PEPEUSDT"
]

tz = pytz.timezone("Asia/Kolkata")

STATE_FILE = "state.json"
LAST_FILE = "last_run.txt"

# 🔄 LOAD STATE
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"hl": {}, "oc": {}}

# 💾 SAVE STATE
def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

state = load_state()

# 📩 SEND
async def send(msg):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        await asyncio.sleep(1)
    except Exception as e:
        print("Telegram Error:", e)

# 🧠 SLEEP CHECK
def check_sleep():
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r") as f:
            last_time = float(f.read())
        now = datetime.now(tz).timestamp()
        return now - last_time > 1800   # 30 min gap = sleep
    return False

# 💾 SAVE TIME
def save_time():
    with open(LAST_FILE, "w") as f:
        f.write(str(datetime.now(tz).timestamp()))

# 🔄 HEARTBEAT SAVE
async def heartbeat_save():
    while True:
        save_time()
        await asyncio.sleep(300)

# 🟢 HEARTBEAT ALERT (6 HOURS)
async def heartbeat_alert():
    while True:
        await send("🟢 BOT LIVE (6h check) ✅")
        await asyncio.sleep(21600)  # 6 hours

# 🔄 PRICE (FUTURES)
def get_price(symbol):
    url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    return float(requests.get(url).json()["price"])

# 🔄 WEEKLY LEVELS
def get_weekly_levels(symbol):
    url = f"https://fapi.binance.com/fapi/v1/klines"
    params = {"symbol": symbol, "interval": "1w", "limit": 2}
    data = requests.get(url, params=params).json()
    prev = data[0]
    return float(prev[1]), float(prev[2]), float(prev[3]), float(prev[4])

# 🗓️ WEEK KEY
def week_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.isocalendar()[1]}"

# 🚀 MAIN BOT
async def run_bot():

    if check_sleep():
        await send("😴 Bot woke up from SLEEP mode")

    await send("✅ Futures Bot STARTED 🚀")

    asyncio.create_task(heartbeat_save())
    asyncio.create_task(heartbeat_alert())

    while True:
        try:
            wk = week_key()

            for coin in COINS:
                try:
                    price = get_price(coin)
                    open_p, high, low, close = get_weekly_levels(coin)

                    key1 = f"{coin}-{wk}-hl"
                    key2 = f"{coin}-{wk}-oc"

                    # 🔔 HIGH / LOW
                    if price >= high and not state["hl"].get(key1):
                        await send(f"🚀 {coin} HIGH BREAKOUT\nPrice: {price} USDT")
                        state["hl"][key1] = True

                    elif price <= low and not state["hl"].get(key1):
                        await send(f"🔻 {coin} LOW BREAKDOWN\nPrice: {price} USDT")
                        state["hl"][key1] = True

                    # 🔔 OPEN / CLOSE
                    if state["hl"].get(key1) and not state["oc"].get(key2):

                        if abs(price - open_p) / open_p < 0.01:
                            await send(f"📊 {coin} OPEN TOUCH\nPrice: {price} USDT")
                            state["oc"][key2] = True

                        elif abs(price - close) / close < 0.01:
                            await send(f"📊 {coin} CLOSE TOUCH\nPrice: {price} USDT")
                            state["oc"][key2] = True

                except Exception as e:
                    print("Coin Error:", coin, e)

            save_state(state)

            await asyncio.sleep(120)

        except Exception as e:
            print("Main Error:", e)
            await asyncio.sleep(10)

# 🌐 Flask (KEEP ALIVE)
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
