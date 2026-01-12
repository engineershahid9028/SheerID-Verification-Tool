import threading
import time
import requests
import os
from fastapi import FastAPI

BOT_TOKEN = os.getenv("BOT_TOKEN")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

offset = 0
app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "bot": "running"}

def send_message(chat_id, text):
    requests.post(f"{API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text[:4000]
    })

def polling_loop():
    global offset
    print("🤖 Telegram polling started...")

    while True:
        try:
            res = requests.get(f"{API}/getUpdates", params={
                "timeout": 30,
                "offset": offset
            }).json()

            if "result" in res:
                for update in res["result"]:
                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text", "")

                    if text == "/start":
                        send_message(chat_id,
                            "Welcome!\n\nAvailable tools:\n"
                            "/k12\n"
                            "/spotify\n"
                            "/youtube\n"
                            "/canva\n"
                            "/veterans"
                        )
                    else:
                        send_message(chat_id, f"Received: {text}")

        except Exception as e:
            print("Polling error:", e)

        time.sleep(2)

# Start polling in background thread
threading.Thread(target=polling_loop, daemon=True).start()
