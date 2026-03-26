import os
import time
import threading
import asyncio
from flask import Flask
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# ✅ ASYNC FUNCTION
async def send_telegram():
    try:
        await bot.send_message(chat_id=CHAT_ID, text="🚀 BOT 2 WORKING!")
        print("✅ Message sent")
    except Exception as e:
        print("❌ Error:", e)

# 🔥 RUN ASYNC
def run_bot():
    asyncio.run(send_telegram())
    while True:
        print("Bot running...")
        time.sleep(60)

# 🌐 Flask server
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# 🚀 START
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
