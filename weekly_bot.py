import os
import time
import threading
from flask import Flask
from telegram import Bot

# ===== DEBUG TOKEN =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("BOT_TOKEN:", BOT_TOKEN)
print("CHAT_ID:", CHAT_ID)

# ===== SAFE BOT INIT =====
bot = None
if BOT_TOKEN:
    try:
        bot = Bot(token=BOT_TOKEN)
    except Exception as e:
        print("Bot init error:", e)
else:
    print("❌ BOT_TOKEN missing")

# ===== SEND TEST =====
def send_test():
    if bot and CHAT_ID:
        try:
            bot.send_message(chat_id=CHAT_ID, text="🔥 DEBUG SUCCESS")
            print("✅ Message sent")
        except Exception as e:
            print("Send error:", e)
    else:
        print("❌ Missing bot or chat id")

# ===== LOOP =====
def run_bot():
    send_test()
    while True:
        print("Bot running...")
        time.sleep(60)

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ===== START =====
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
