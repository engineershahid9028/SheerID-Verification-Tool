import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = "https://sheerid-verification-tool-production.up.railway.app"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
res = requests.post(url, data={"url": f"{APP_URL}/webhook"})

print(res.text)
