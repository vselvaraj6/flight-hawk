import random
import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

OTP_EXPIRY_SECONDS = 300  # 5 minutes


def generate_otp():
    """Generates a random 6-digit OTP and returns it with an expiry timestamp."""
    code = str(random.randint(100000, 999999))
    expiry = time.time() + OTP_EXPIRY_SECONDS
    return code, expiry


def send_otp_via_telegram(otp_code):
    """Sends the OTP code to the configured Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    msg = (
        f"🔐 <b>Flight Tracker Login OTP</b>\n\n"
        f"Your one-time password is:\n\n"
        f"<code>{otp_code}</code>\n\n"
        f"This code expires in 5 minutes. Do not share it with anyone."
    )

    try:
        response = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        }, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def verify_otp(input_code, stored_code, expiry_time):
    """Verifies the OTP against stored code and expiry."""
    if time.time() > expiry_time:
        return False, "OTP has expired. Please request a new one."
    if input_code.strip() == stored_code:
        return True, "Login successful!"
    return False, "Invalid OTP. Please try again."
