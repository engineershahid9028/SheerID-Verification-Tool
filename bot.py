import os
import time
import threading
import subprocess
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

offset = 0

# ================= TELEGRAM =================

def send_message(chat_id, text):
    requests.post(
        f"{API}/sendMessage",
        json={"chat_id": chat_id, "text": text[:4000]},
        timeout=20
    )

# ================= WORKER =================

def run_job(chat_id, command):
    """
    Runs long job in background and sends result
    """
    try:
        send_message(chat_id, "⏳ Job started. I’ll notify you when finished.")

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=600   # 10 minutes max
        )

        output = result.stdout or result.stderr or "Job finished."

        send_message(chat_id, f"✅ Job finished:\n\n{output[:3500]}")

    except subprocess.TimeoutExpired:
        send_message(chat_id, "❌ Job timed out.")

    except Exception as e:
        send_message(chat_id, f"❌ Job failed:\n{str(e)}")


def start_job_async(chat_id, command):
    thread = threading.Thread(target=run_job, args=(chat_id, command))
    thread.start()


# ================= POLLING =================

def polling_loop():
    global offset
    print("🤖 Bot running...")

    while True:
        try:
            res = requests.get(
                f"{API}/getUpdates",
                params={"timeout": 30, "offset": offset},
                timeout=40
            ).json()

            if "result" in res:
                for update in res["result"]:
                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text", "").strip()

                    if text == "/start":
                        send_message(chat_id, "Send /run to start a job")

                    elif text == "/run":
                        # Example job
                        command = ["python", "job.py"]
                        start_job_async(chat_id, command)

                    else:
                        send_message(chat_id, "Unknown command. Use /run")

        except Exception as e:
            print("Polling error:", e)

        time.sleep(2)


# ================= START =================

if __name__ == "__main__":
    polling_loop()
