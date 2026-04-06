import os
import time
import requests
import json
from datetime import datetime
import pytz
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

# ===== TELEGRAM =====
def send(msg):
    try:
        print("Sending:", msg)
        bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print("Telegram Error:", e)

# ===== KEYS =====
def day_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.month}-{now.day}"

def week_key():
    now = datetime.now(tz)
    return f"{now.year}-{now.isocalendar()[1]}"

# ===== LEVELS =====
def get_levels(symbol, interval):
    url = "https://fapi.binance.com/fapi/v1/klines"
    data = requests.get(url, params={"symbol": symbol, "interval": interval, "limit": 2}).json()
    prev = data[0]
    return float(prev[1]), float(prev[2]), float(prev[3]), float(prev[4])

# ===== TODAY TOUCH CHECK (🔥 FINAL FIX) =====
def touched_today(symbol, level):
    url = "https://fapi.binance.com/fapi/v1/klines"

    data = requests.get(url, params={
        "symbol": symbol,
        "interval": "1d",
        "limit": 1
    }).json()

    today = data[0]
    high = float(today[2])
    low = float(today[3])

    return low <= level <= high

# ===== CHECK =====
def check_coin(symbol):
    try:
        print(f"Checking {symbol}")

        dk = day_key()
        wk = week_key()

        # ===== DAILY =====
        d_open, d_high, d_low, d_close = get_levels(symbol, "1d")

        levels_d = {
            "HIGH": d_high,
            "LOW": d_low,
            "OPEN": d_open,
            "CLOSE": d_close
        }

        for name, lvl in levels_d.items():
            key = f"{symbol}-{dk}-D-{name}"

            if touched_today(symbol, lvl):
                print(f"🔥 DAILY TOUCH {symbol} {name} {lvl}")

                if not state.get(key):
                    send(f"🚨 {symbol} DAILY {name} TOUCH ({lvl})")
                    state[key] = True

        # ===== WEEKLY =====
        w_open, w_high, w_low, w_close = get_levels(symbol, "1w")

        levels_w = {
            "HIGH": w_high,
            "LOW": w_low,
            "OPEN": w_open,
            "CLOSE": w_close
        }

        for name, lvl in levels_w.items():
            key = f"{symbol}-{wk}-W-{name}"

            if touched_today(symbol, lvl):
                print(f"📊 WEEKLY TOUCH {symbol} {name} {lvl}")

                if not state.get(key):
                    send(f"📊 {symbol} WEEKLY {name} TOUCH ({lvl})")
                    state[key] = True

    except Exception as e:
        print("Error:", symbol, e)

# ===== MAIN LOOP =====
def run_bot():
    send("🚀 BOT STARTED")
    send("🔥 TEST MESSAGE")
    send("🟢 BOT LIVE (6H) ✅")

    while True:
        print("🔄 Checking all coins...")

        for coin in COINS:
            check_coin(coin)

        save_state(state)

        time.sleep(60)  # 1 min loop

# ===== START =====
if __name__ == "__main__":
    run_bot()
