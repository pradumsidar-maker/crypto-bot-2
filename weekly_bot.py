import requests
import time
import json
import os
import asyncio
from datetime import datetime
from telegram import Bot

# ================= CONFIG =================
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

COINS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","XRPUSDT","SOLUSDT",
    "ADAUSDT","DOGEUSDT","MATICUSDT","DOTUSDT","TRXUSDT",
    "LTCUSDT","BCHUSDT","LINKUSDT","ATOMUSDT","ETCUSDT",
    "FILUSDT","APTUSDT","ARBUSDT","OPUSDT","AVAXUSDT",
    "NEARUSDT","ALGOUSDT","FTMUSDT","EGLDUSDT","SANDUSDT"
]

bot = Bot(token=BOT_TOKEN)

# ================= TELEGRAM =================
async def send(msg):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print("Telegram Error:", e)

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
    data = requests.get(url, params={"symbol": symbol}).json()
    return float(data["price"])

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

# ================= BOT LOGIC =================
async def run_bot():
    print("🚀 BOT STARTED")
    await send("🚀 BOT STARTED")
    await send("🟢 BOT LIVE")

    # 🔥 AUTO RESET STATE (FIRST TIME)
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

    state = load_state()

    while True:
        print("⚡ Checking coins...")
        for symbol in COINS:
            try:
                price = get_price(symbol)
                levels = get_prev_day_levels(symbol)

                for name, lvl in levels.items():
                    key = f"{symbol}-{name}"

                    # 🔥 TOUCH LOGIC (0.2% range)
                    if abs(price - lvl) / lvl < 0.002:
                        if not state.get(key):
                            msg = f"🚨 {symbol} {name} TOUCH\nLevel: {lvl}\nPrice: {price}"
                            print(msg)
                            await send(msg)
                            state[key] = True

                save_state(state)

            except Exception as e:
                print(symbol, "Error:", e)

        time.sleep(10)

# ================= RUN =================
if __name__ == "__main__":
    asyncio.run(run_bot())
