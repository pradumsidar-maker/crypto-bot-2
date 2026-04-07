import requests
import time
import json
import os
from flask import Flask
from threading import Thread

# ================= CONFIG =================
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

COINS = [
"BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT",
"ADAUSDT","DOGEUSDT","MATICUSDT","DOTUSDT","TRXUSDT",
"LTCUSDT","BCHUSDT","LINKUSDT","ATOMUSDT","ETCUSDT",
"FILUSDT","APTUSDT","ARBUSDT","OPUSDT","AVAXUSDT",
"NEARUSDT","ALGOUSDT","FTMUSDT","EGLDUSDT","SANDUSDT"
]

# ================= FLASK =================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Running 🚀"

# ================= TELEGRAM DEBUG =================
def send(msg):
    try:
        print("📤 Sending:", msg)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.get(url, params={"chat_id": CHAT_ID, "text": msg})
        print("📡 Response:", r.text)
    except Exception as e:
        print("❌ Telegram Error:", e)

# ================= STATE =================
STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return {}

def save_state(state):
    json.dump(state, open(STATE_FILE, "w"))

# ================= DATA =================
def get_price(symbol):
    url = "https://fapi.binance.com/fapi/v1/ticker/price"
    return float(requests.get(url, params={"symbol": symbol}).json()["price"])

def get_prev_day_levels(symbol):
    url = "https://fapi.binance.com/fapi/v1/klines"
    data = requests.get(url, params={"symbol": symbol, "interval": "1d", "limit": 2}).json()
    prev = data[0]

    return {
        "HIGH": float(prev[2]),
        "LOW": float(prev[3]),
        "OPEN": float(prev[1]),
        "CLOSE": float(prev[4])
    }

# ================= BOT =================
def run_bot():
    print("🔥 BOT FUNCTION STARTED")

    # 👉 DEBUG START MESSAGE
    send("🔥 BOT STARTED TEST")

    time.sleep(5)

    send("🚀 BOT STARTED")
    send("🟢 BOT LIVE")

    # 👉 RESET STATE (हर deploy पर fresh alert)
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

    state = load_state()

    while True:
        print("🔄 Checking coins...")

        for symbol in COINS:
            try:
                price = get_price(symbol)
                levels = get_prev_day_levels(symbol)

                print(f"Checking {symbol} | Price: {price}")

                for name, lvl in levels.items():
                    key = f"{symbol}-{name}"

                    # 🔥 TOUCH LOGIC (0.2%)
                    if abs(price - lvl) / lvl < 0.002:
                        if not state.get(key):
                            msg = f"🚨 {symbol} {name} TOUCH\nLevel: {lvl}\nPrice: {price}"
                            print(msg)
                            send(msg)
                            state[key] = True

                save_state(state)

            except Exception as e:
                print(symbol, "Error:", e)

        time.sleep(10)

# ================= RUN =================
if __name__ == "__main__":
    # 👉 BOT THREAD (IMPORTANT)
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # 👉 FLASK MAIN (Render needs port)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
