import time
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

offset = 0

def get_updates():
    global offset
    url = f"{API}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    res = requests.get(url, params=params).json()
    return res

def send_message(chat_id, text):
    requests.post(f"{API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text[:4000]
    })

print("🤖 Telegram bot polling started...")

while True:
    try:
        data = get_updates()

        if "result" in data:
            for update in data["result"]:
                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                chat_id = update["message"]["chat"]["id"]
                text = update["message"].get("text", "")

                if text == "/start":
                    send_message(chat_id,
                        "Welcome!\n\n"
                        "Available tools:\n"
                        "/k12\n"
                        "/spotify\n"
                        "/youtube\n"
                        "/canva\n"
                        "/veterans"
                    )
                else:
                    send_message(chat_id, f"Received: {text}")

    except Exception as e:
        print("Error:", e)

    time.sleep(2)
