import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message_text):
    """
    Sends a message via the Telegram Bot API to a specific chat ID.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        print("Error: Missing Telegram credentials in .env file")
        print(f"Would have sent: {message_text}")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 400:
            # HTML parse error — retry without parse_mode
            print(f"Telegram HTML parse error: {response.text}")
            print("Retrying without HTML formatting...")
            import re
            plain_text = re.sub(r'<[^>]+>', '', message_text)
            payload_plain = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": plain_text,
                "disable_web_page_preview": False
            }
            response = requests.post(url, json=payload_plain, timeout=10)
        response.raise_for_status()
        print("Telegram notification sent successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response body: {e.response.text}")
        return False

if __name__ == "__main__":
    # Test block
    print("Testing Telegram Notifier (Requires proper .env vars)")
    success = send_telegram_message("🤖 <b>Test message</b> from your new Flight Tracker Bot!")
    if success:
        print("Message sent! Check your Telegram.")
    else:
         print("Did not send message. Please ensure .env is set up correctly.")
