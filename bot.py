import html
import json
import time
import requests

# ============================================================
# CONFIGURATION
# ============================================================

BOT_TOKEN = "8996541145:AAHAee6lM28XbeuASDRf1wTgdKehZT30-Yg"
ADMIN_ID = 8755636383

# RapidAPI Credentials (Routing Number Bank Lookup)
RAPIDAPI_HOST = "routing-number-bank-lookup.p.rapidapi.com"
RAPIDAPI_KEY = "cb62ff742emshbc0487ab2ad6aedp1dc6b4jsne6838bd9f298"

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


# ============================================================
# SEND MESSAGE
# ============================================================


def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = f"{TELEGRAM_API}/sendMessage"

    data = {"chat_id": chat_id, "text": str(text)}

    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup)

    if parse_mode is not None:
        data["parse_mode"] = parse_mode

    try:
        response = requests.post(url, data=data, timeout=30)
        return response.json()
    except requests.exceptions.RequestException as error:
        print("sendMessage request error:", error)
        return None
    except Exception as error:
        print("sendMessage unexpected error:", error)
        return None


# ============================================================
# GET UPDATES
# ============================================================


def get_updates(offset):
    url = f"{TELEGRAM_API}/getUpdates"
    params = {"offset": offset, "timeout": 30}

    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except requests.exceptions.RequestException as error:
        print("getUpdates request error:", error)
        return None
    except Exception as error:
        print("getUpdates unexpected error:", error)
        return None


# ============================================================
# KEYBOARDS
# ============================================================


def main_keyboard():
    return {
        "keyboard": [[{"text": "🏦 Bank Lookup"}]],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


def admin_keyboard():
    return {
        "keyboard": [[{"text": "🏦 Bank Lookup"}], [{"text": "👑 Admin"}]],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }


# ============================================================
# WELCOME MESSAGE
# ============================================================


def send_welcome(chat_id, user_id):
    if user_id == ADMIN_ID:
        message = (
            "👋 Welcome, Admin!\n\n"
            "🤖 Bot is online.\n"
            "👇 Choose an option from the menu below:"
        )
        send_message(chat_id, message, reply_markup=admin_keyboard())
    else:
        message = (
            "👋 Welcome!\n\n👇 Please choose an option from the menu below:"
        )
        send_message(chat_id, message, reply_markup=main_keyboard())


# ============================================================
# EXTERNAL API REQUEST (BANK ROUTING LOOKUP)
# ============================================================


def call_external_api(routing_number):
    if not RAPIDAPI_KEY:
        return {
            "success": False,
            "error": "RAPIDAPI_KEY is missing.",
        }

    # API Endpoint URL
    url = f"https://{RAPIDAPI_HOST}/api/v1/{routing_number}"

    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY,
        "Content-Type": "application/json",
    }

    params = {"format": "json", "paymentType": "ach"}

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=30
        )

        try:
            return response.json()
        except ValueError:
            return {
                "success": False,
                "error": "API did not return valid JSON.",
                "response": response.text[:1000],
            }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "External API request timed out."}
    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "error": "API request failed.",
            "details": str(error),
        }
    except Exception as error:
        return {
            "success": False,
            "error": "Unexpected API error.",
            "details": str(error),
        }


# ============================================================
# FORMAT JSON FOR TELEGRAM
# ============================================================


def format_json(data):
    try:
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        formatted = str(data)

    return html.escape(formatted)


# ============================================================
# HANDLE MESSAGE
# ============================================================


def handle_message(message):
    if "chat" not in message:
        return

    chat_id = message["chat"]["id"]
    user_id = message.get("from", {}).get("id", 0)
    text = message.get("text", "").strip()

    if not text:
        return

    print(f"Message: {text} | User ID: {user_id}")

    # Start Command
    if text == "/start":
        send_welcome(chat_id, user_id)
        return

    # Admin Panel
    if text in ["/admin", "👑 Admin"]:
        if user_id != ADMIN_ID:
            send_message(
                chat_id, "❌ You are not authorized to use admin commands."
            )
            return

        admin_msg = (
            "👑 <b>Admin Panel</b>\n\n"
            "✅ Bot Status: Online\n"
            "📡 Polling: Active\n"
            "🔐 Admin Verification: Active"
        )
        send_message(
            chat_id, admin_msg, parse_mode="HTML", reply_markup=admin_keyboard()
        )
        return

    # Bank Lookup Menu Button
    if text in ["📱 Phone Lookup", "🏦 Bank Lookup"]:
        send_message(
            chat_id,
            "🏦 Send Routing Number (e.g., 121000248):",
            reply_markup=main_keyboard(),
        )
        return

    # Process Routing Number / Input
    if text.isdigit():
        result = call_external_api(text)

        # Handle Errors gracefully
        if isinstance(result, dict) and "message" in result:
            if result["message"] == "You are not subscribed to this API.":
                telegram_message = "❌ <b>Error:</b> RapidAPI par is Routing Number API ko Subscribe karein."
            elif result["message"] == "Too many requests":
                telegram_message = "⚠️ <b>Error:</b> Rate limit exceed ho gayi hai. Thodi der baad try karein."
            else:
                formatted_result = format_json(result)
                telegram_message = (
                    f"📋 <b>Result:</b>\n<pre>{formatted_result}</pre>"
                )
        else:
            formatted_result = format_json(result)
            telegram_message = f"📋 <b>Result:</b>\n<pre>{formatted_result}</pre>"

        if len(telegram_message) > 3900:
            telegram_message = (
                telegram_message[:3800] + "\n\n...Result truncated.</pre>"
            )

        send_message(
            chat_id,
            telegram_message,
            parse_mode="HTML",
            reply_markup=main_keyboard(),
        )
        return

    # Default Invalid Input
    send_message(
        chat_id,
        "❌ Invalid input.\n\nPlease select an option from the menu.",
        reply_markup=main_keyboard(),
    )


# ============================================================
# MAIN LOOP
# ============================================================


def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is empty.")
        return

    print("====================================")
    print("Telegram Bot Started")
    print(f"Admin ID: {ADMIN_ID}")
    print(f"RapidAPI Host: {RAPIDAPI_HOST}")
    print("====================================")

    offset = 0

    while True:
        try:
            updates = get_updates(offset)

            if updates is None or not updates.get("ok", False):
                time.sleep(3)
                continue

            results = updates.get("result", [])

            for update in results:
                try:
                    update_id = update.get("update_id")
                    if update_id is not None:
                        offset = update_id + 1

                    if "message" in update:
                        handle_message(update["message"])

                except Exception as error:
                    print("Update processing error:", error)

            time.sleep(1)

        except KeyboardInterrupt:
            print("Bot stopped manually.")
            break
        except Exception as error:
            print("Main loop error:", error)
            time.sleep(5)


# ============================================================
# EXECUTION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
