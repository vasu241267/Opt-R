import logging
import requests
import threading
import time
import os
from flask import Flask, Response
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import html  
import time
last_change_time = {}

# ====== CONFIG ======
import os

BOT_TOKEN = "8270301262:AAEldMmzcGK9sRbYk9WrFz6MqYE42EDnwlc"
AUTH_TOKEN = "e225134d-ac59-42b0-ba3f-0c41f43ceb62"
GROUP_ID = "-4967707436"
API_URL = "https://raazit.acchub.io/api/"
BASE_URL = "https://raazit.acchub.io/api/sms"
FETCH_INTERVAL = 2  # seconds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====== Flask App for Render Health Checks ======
app = Flask(__name__)

@app.route("/health")
def health():
    logger.info("Health check requested")
    return Response("OK", status=200)

@app.route("/")
def root():
    logger.info("Root endpoint requested")
    return Response("OK", status=200)

# =========================================
# ====== acchubb.py ka OTP monitor ========
# =========================================
def mask_number(num):
    num = str(num)
    if len(num) > 5:
        return num[:2] + '*' * (len(num) - 5) + num[-3:]
    return num  # agar number bahut chhota ho toh mask na karo
def fetch_otp_acchubb():
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "auth-token": AUTH_TOKEN,
        "Cookie": f"authToken={AUTH_TOKEN}; authRole=Freelancer",
        "Origin": "https://raazit.acchub.io",
        "Referer": "https://raazit.acchub.io",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0"
    }
    data = {
        "action": "get_otp",
        "number": "1234567890"
    }
    try:
        response = requests.post(API_URL, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            return response.json().get("data", [])
    except Exception as e:
        logger.error(f"Error fetching OTP: {e}")
    return []

# Config me ye add karo
DEV_LINK = os.getenv("DEV_LINK", "https://t.me/Vxxwo")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/DDxOTP")

def send_telegram_message(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        # Inline buttons
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "👨‍💻 Developer", "url": DEV_LINK},
                    {"text": "📢 Channel", "url": CHANNEL_LINK}
                ]
            ]
        }

        payload = {
            "chat_id": GROUP_ID,
            "text": msg,
            "parse_mode": "HTML",
            "reply_markup": str(keyboard).replace("'", '"')
        }

        r = requests.post(url, data=payload)
        if r.status_code == 200:
            logger.info("✅ OTP sent to Telegram")
        else:
            logger.error(f"❌ Telegram send failed: {r.text}")
    except Exception as e:
        logger.error(f"⚠️ Telegram error: {e}")

def otp_monitor_acchubb():
    logger.info("Starting OTP monitor thread")
    sent_ids = set()

    # Send old OTPs
    for otp_entry in fetch_otp_acchubb():
        otp_id = otp_entry.get("id")
        otp_code = otp_entry.get("otp", "").strip()
        if otp_code:
            sent_ids.add(otp_id)
            msg = (
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "📩 <b>New OTP Notification</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"📞 <b>Number:</b> <code>{mask_number(otp_entry.get('did'))}</code>\n"
    f"🌍 <b>Country:</b> <b>{otp_entry.get('country_name')}</b>\n\n"
    f"🔑 <b>OTP:</b> <blockquote>{html.escape(otp_code)}</blockquote>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚡️ <i>Powered by @Vxxwo 🔱</i>\n"
    "━━━━━━━━━━━━━━━━━━━━━━"
)

            send_telegram_message(msg)

    # Continuous loop
    while True:
        for otp_entry in fetch_otp_acchubb():
            otp_id = otp_entry.get("id")
            otp_code = otp_entry.get("otp", "").strip()
            if otp_code and otp_id not in sent_ids:
                sent_ids.add(otp_id)
            

                msg = (
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "📩 <b>New OTP Notification</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"📞 <b>Number:</b> <code>{mask_number(otp_entry.get('did'))}</code>\n"
    f"🌍 <b>Country:</b> <b>{otp_entry.get('country_name')}</b>\n\n"
    f"🔑 <b>OTP:</b> <blockquote>{html.escape(otp_code)}</blockquote>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚡️ <i>Powered by @Vxxwo Bot 🔱 </i>\n"
    "━━━━━━━━━━━━━━━━━━━━━━"
)


                send_telegram_message(msg)
        time.sleep(FETCH_INTERVAL)
    # Continuous loop
    while True:
        for otp_entry in fetch_otp_acchubb():
            otp_id = otp_entry.get("id")
            otp_code = otp_entry.get("otp", "").strip()
            if otp_code and otp_id not in sent_ids:
                sent_ids.add(otp_id)
                msg = (
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "📩 <b>New OTP Notification</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"📞 <b>Number:</b> <code>{mask_number(otp_entry.get('did'))}</code>\n"
    f"🌍 <b>Country:</b> <b>{otp_entry.get('country_name')}</b>\n\n"
    f"🔑 <b>OTP:</b> <blockquote>{html.escape(otp_code)}</blockquote>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚡️ <i>Powered by @Vxxwo Bot ❤️</i>\n"
    "━━━━━━━━━━━━━━━━━━━━━━"
)
                send_telegram_message(msg)
        time.sleep(FETCH_INTERVAL)

# =========================================
# ====== acc.py ka number add bot =========
# =========================================
def get_countries():
    headers = {"Auth-Token": AUTH_TOKEN}
    resp = requests.get(f"{BASE_URL}/combo-list", headers=headers)
    data = resp.json()
    return data.get("data", []) if data.get("meta") == 200 else []

def get_carriers(country_id):
    headers = {"Auth-Token": AUTH_TOKEN}
    resp = requests.get(f"{BASE_URL}/carrier-list?app={country_id}", headers=headers)
    data = resp.json()
    return data.get("data", []) if data.get("meta") == 200 else []

def add_number(app_id, carrier_id):
    headers = {
        "Auth-Token": AUTH_TOKEN,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {
        "authToken": AUTH_TOKEN,
        "app": app_id,
        "carrier": carrier_id
    }
    return requests.post(f"{BASE_URL}/", headers=headers, files={}, data=data).json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    countries = get_countries()
    if not countries:
        await update.message.reply_text("❌ Countries fetch nahi ho paayi.")
        return
    keyboard = [[InlineKeyboardButton(c["text"], callback_data=f"country|{c['id']}")] for c in countries]
    await update.message.reply_text("🌍 Select a country:", reply_markup=InlineKeyboardMarkup(keyboard))

# Memory store for user preferences
user_last_selection = {}
COUNTRIES_PER_PAGE = 10

def paginate_countries(page=0):
    countries = get_countries()
    start = page * COUNTRIES_PER_PAGE
    end = start + COUNTRIES_PER_PAGE

    buttons = [
        [InlineKeyboardButton(c["text"], callback_data=f"country|{c['id']}")]
        for c in countries[start:end]
    ]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅ Back", callback_data=f"more_countries|{page-1}"))
    if end < len(countries):
        nav_buttons.append(InlineKeyboardButton("➡ More", callback_data=f"more_countries|{page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    return buttons


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = paginate_countries(0)
    await update.message.reply_text("🌍 Select a country:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, *values = query.data.split("|")

    if action == "more_countries":
        page = int(values[0])
        keyboard = paginate_countries(page)
        await query.edit_message_text("🌍 Select a country:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif action == "country":
        country_id = values[0]
        carriers = get_carriers(country_id)

        if not carriers:  # No carrier → try to directly allocate number
            res = add_number(country_id, "")
            if res.get("meta") == 200 and res.get("data"):
                data = res["data"]
                user_last_selection[query.from_user.id] = (country_id, "")
                await send_number_message(query, data, country_id, "")
            else:
                await query.edit_message_text("❌ Numbers currently not available.")
            return

        keyboard = [
            [InlineKeyboardButton(c["text"], callback_data=f"carrier|{country_id}|{c['id']}")]
            for c in carriers
        ]
        await query.edit_message_text("🚚 Select a carrier:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif action == "carrier":
        country_id, carrier_id = values
        res = add_number(country_id, carrier_id)
        if res.get("meta") == 200 and res.get("data"):
            data = res["data"]
            user_last_selection[query.from_user.id] = (country_id, carrier_id)
            await send_number_message(query, data, country_id, carrier_id)
        else:
            await query.edit_message_text("❌ Numbers currently not available.")

    elif action == "change_number":
        if query.from_user.id not in user_last_selection:
            await query.edit_message_text("❌ First get a number.")
            return

        country_id, carrier_id = user_last_selection[query.from_user.id]
        res = add_number(country_id, carrier_id)
        if res.get("meta") == 200 and res.get("data"):
            data = res["data"]
            await send_number_message(query, data, country_id, carrier_id, changed=True)
        else:
            await query.edit_message_text("❌ Numbers currently not available.")


    elif action == "more_countries":
      page = int(values[0])
      keyboard = paginate_countries(page)
      await query.edit_message_text("🌍 Select a country:", reply_markup=InlineKeyboardMarkup(keyboard))


async def send_number_message(query, data, country_id, carrier_id, changed=False):
    msg = (
        ("🔄 <b>Number Changed!</b>\n\n" if changed else "✅ <b>Number Added Successfully!</b>\n\n") +
        f"📞 <b>Number:</b> <code>{data.get('did')}</code>\n"
        f"<i>Devloped by @Vxxwo ❤️</i>"
    )
    keyboard = [
        [
            InlineKeyboardButton("📩 View OTP", url="https://t.me/+bzv2oFwslWI3Y2I1"),
            InlineKeyboardButton("📢 Main Channel", url="https://t.me/ddxotp")
        ],
        [
            InlineKeyboardButton("🔄 Change Number", callback_data="change_number")
        ]
    ]
    await query.edit_message_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
# =========================================
# ====== Main start functions ============
# =========================================

from telegram.ext import CommandHandler

async def search_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🔍 Usage: /search <country name>")
        return

    query = " ".join(context.args).lower()
    countries = get_countries()

    matched = [c for c in countries if query in c["text"].lower()]
    if not matched:
        await update.message.reply_text("❌ Country not found.")
        return

    # Agar multiple matches mile to list dikhao
    if len(matched) > 1:
        keyboard = [[InlineKeyboardButton(c["text"], callback_data=f"country|{c['id']}")] for c in matched]
        await update.message.reply_text("🌍 Select a country:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Single match → carrier selection
    country = matched[0]
    carriers = get_carriers(country["id"])
    if not carriers:
        res = add_number(country["id"], "")
        if res.get("meta") == 200 and res.get("data"):
            await send_number_message(update, res["data"], country["id"], "")
        else:
            await update.message.reply_text("❌ Numbers currently not available.")
        return

    keyboard = [
        [InlineKeyboardButton(c["text"], callback_data=f"carrier|{country['id']}|{c['id']}")]
        for c in carriers
    ]
    await update.message.reply_text("🚚 Select a carrier:", reply_markup=InlineKeyboardMarkup(keyboard))

# Start bot function me handler add karo



def start_otp_thread():
    threading.Thread(target=otp_monitor_acchubb, daemon=True).start()

def start_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("search", search_country))
    application.run_polling()

if __name__ == "__main__":
    logger.info("Starting application...")

    # Start OTP monitor in background
    start_otp_thread()

    # Start Flask server in background (for Render health checks)
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)), threaded=True),
        daemon=True
    ).start()

    # Start Telegram bot in main thread
    start_bot()