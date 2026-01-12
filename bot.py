import os
import requests
from fastapi import FastAPI, Request
from launcher import run_tool

BOT_TOKEN = os.getenv("BOT_TOKEN")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()

def send_message(chat_id, text):
    requests.post(f"{TG_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text[:4000]
    })

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").replace("/", "").lower()

    if text == "start":
        send_message(chat_id,
            "Choose a tool:\n"
            "/boltnew\n"
            "/canva\n"
            "/k12\n"
            "/one\n"
            "/perplexity\n"
            "/spotify\n"
            "/veterans\n"
            "/youtube"
        )
        return {"ok": True}

    output = run_tool(text)
    send_message(chat_id, output)

    return {"ok": True}
