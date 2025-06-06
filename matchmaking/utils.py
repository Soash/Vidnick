import requests, json, random, string
from environ import Env

env = Env()
Env.read_env()
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')

def send_telegram_notification(chat_id, message, button_text, button_url):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",  # Optional: Use Markdown or HTML for text formatting
        "disable_web_page_preview": True,  # This hides the link preview
        "reply_markup": json.dumps({
            "inline_keyboard": [
                [{"text": button_text, "url": button_url}]
            ]
        })
    }
    response = requests.post(url, data=data)
    return response.json()


def generate_jitsi_meeting_url():
    base_url = "https://meet.jit.si"
    room_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    join_url = f"{base_url}/{room_name}"
    start_url = join_url
    return {
        "id": room_name,
        "join_url": join_url,
        "start_url": start_url
    }
    
    