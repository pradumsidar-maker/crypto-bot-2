import os
import time
import requests
import json
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running 🚀"

# ===== TELEGRAM =====
def send(msg):
    try:
        print("Sending:", msg)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram Error:", e)

# ===== COINS =====
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

# ===== STATE =====
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

state = load_state()

def day_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.month}-{now.day}"

def week_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.isocalendar()[1]}"

# ===== LEVEL FETCH =====
def get_levels(symbol, interval):
    url = "https://fapi.binance.com/fapi/v1/klines"
    data = requests.get(url, params={"symbol": symbol, "interval": interval, "limit": 2}).json()
    prev = data[0]
    return {
        "OPEN": float(prev[1]),
        "HIGH": float(prev[2]),
        "LOW": float(prev[3]),
        "CLOSE": float(prev[4])
    }

# ===== TODAY RANGE =====
def today_range(symbol):
    url = "https://fapi.binance.com/fapi/v1/klines"
    data = requests.get(url, params={"symbol": symbol, "interval": "1d", "limit": 1}).json()
    today = data[0]
    return float(today[2]), float(today[3])  # high, low

# ===== CHECK TOUCH =====
def is_touched(level, high, low):
    return low <= level <= high

# ===== CHECK =====
def check_coin(symbol):
    try:
        print("Checking", symbol)

        d_key = day_key()
        w_key = week_key()

        today_high, today_low = today_range(symbol)

        # ===== DAILY =====
        d_levels = get_levels(symbol, "1d")

        for name, lvl in d_levels.items():
            key = f"{symbol}-D-{name}-{d_key}"

            if is_touched(lvl, today_high, today_low):
                if not state.get(key):
                    send(f"🚨 {symbol} DAILY {name} TOUCH ({lvl})")
                    state[key] = True

        # ===== WEEKLY =====
        w_levels = get_levels(symbol, "1w")

        for name, lvl in w_levels.items():
            key = f"{symbol}-W-{name}-{w_key}"

            if is_touched(lvl, today_high, today_low):
                if not state.get(key):
                    send(f"📊 {symbol} WEEKLY {name} TOUCH ({lvl})")
                    state[key] = True

    except Exception as e:
        print("Error:", symbol, e)

# ===== BOT LOOP =====
def run_bot():
    time.sleep(5)

    send("🚀 BOT STARTED")
    send("🟢 BOT LIVE")

    # 👉 PAST TOUCH CHECK (IMPORTANT)
    send("⚡ Checking past touches...")

    for coin in COINS:
        check_coin(coin)

    while True:
        print("🔄 Checking all coins...")

        for coin in COINS:
            check_coin(coin)

        save_state(state)
        time.sleep(60)

# ===== RUN =====
if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)
