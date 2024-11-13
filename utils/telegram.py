import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7352736287:AAEbcAIG7Re5C93yoGRzXK66opRw7EZ0zgo")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1002326002578")

def send_error_to_telegram(error_message: str, topic: int):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": error_message,
        "parse_mode": "HTML",
        "message_thread_id": topic
    }
    response = requests.post(url, data=payload)
    return response.status_code, response.json()


# Новые события 8
# фронт 2
# бек 6