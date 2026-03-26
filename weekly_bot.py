import os
import time
import threading
from flask import Flask
from telegram import Bot

# ===== ENV VARIABLES =====
BOT_TOKEN = os.getenv("8690174599:AAEMuipJVajwkZaBBsoPxsor-c1H3NxdP3M")
CHAT_ID = os.getenv("5270697473")

# ===== TELEGRAM BOT =====
bot = Bot(token=BOT_TOKEN)

# ===== SEND START MESSAGE =====
def send_start_message():
    try:
        bot.send_message(chat_id=CHAT_ID, text="🚀 BOT 2 LIVE & WORKING!")
        print("Message sent successfully")
    except Exception as e:
        print("Error sending message:", e)

# ===== BACKGROUND LOOP =====
def run_bot():
    send_start_message()  # run once on start
    while True:
        print("Bot running...")
        time.sleep(60)

# ===== FLASK SERVER (RENDER FREE FIX) =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ===== START THREADS =====
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
