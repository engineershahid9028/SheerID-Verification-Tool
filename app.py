import threading
import time
import requests
import os
import subprocess
from fastapi import FastAPI

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

API = f"https://api.telegram.org/bot{BOT_TOKEN}"
POLL_TIMEOUT = 30
POLL_SLEEP = 2

# Command → Script mapping
TOOLS = {
    "/boltnew": "boltnew-verify-tool/main.py",
    "/k12": "k12-verify-tool/main.py",
    "/one": "one-verify-tool/main.py",
    "/perplexity": "perplexity-verify-tool/main.py",
    "/spotify": "spotify-verify-tool/main.py",
    "/veterans": "veterans-verify-tool/main.py",
    "/youtube": "youtube-verify-tool/main.py",
}

# Store pending user input
user_state = {}

# ================= FASTAPI =================
app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "bot": "running"}

# ================= TELEGRAM =================
def send_message(chat_id, text):
    try:
        requests.post(
            f"{API}/sendMessage",
            json={"chat_id": chat_id, "text": text[:4000]},
            timeout=20
        )
    except Exception as e:
        print("Send error:", e)

# ================= TOOL RUNNER =================
def run_tool(command, argument):
    script = TOOLS[command]

    try:
        result = subprocess.run(
            ["python", script, argument],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.stdout or result.stderr or "✅ Tool finished."
    except subprocess.TimeoutExpired:
        return "⏱ Tool timed out. Try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ================= POLLING LOOP =================
offset = 0

def polling_loop():
    global offset
    print("🤖 Telegram polling started...")

    while True:
        try:
            response = requests.get(
                f"{API}/getUpdates",
                params={"timeout": POLL_TIMEOUT, "offset": offset},
                timeout=POLL_TIMEOUT + 10
            ).json()

            if "result" in response:
                for update in response["result"]:
                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    chat_id = update["message"]["chat"]["id"]
                    text = (update["message"].get("text") or "").strip()

                    # Start menu
                    if text.lower() == "/start":
                        send_message(
                            chat_id,
                            "Welcome!\n\nAvailable tools:\n"
                            "/boltnew\n"
                            "/k12\n"
                            "/one\n"
                            "/perplexity\n"
                            "/spotify\n"
                            "/veterans\n"
                            "/youtube\n\n"
                            "Send a command to run a tool."
                        )

                    # Tool selected → ask for URL
                    elif text.lower() in TOOLS:
                        send_message(chat_id, "🔗 Please send verification URL:")
                        user_state[chat_id] = text.lower()

                    # URL received → run tool
                    elif chat_id in user_state:
                        tool = user_state.pop(chat_id)
                        send_message(chat_id, "⏳ Running tool, please wait...")
                        result = run_tool(tool, text.strip())
                        send_message(chat_id, result)

                    else:
                        send_message(chat_id, "❓ Unknown command. Type /start")

        except Exception as e:
            print("Polling error:", e)

        time.sleep(POLL_SLEEP)

# ================= START BOT =================
threading.Thread(target=polling_loop, daemon=True).start()
