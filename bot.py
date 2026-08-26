import requests
import json
import time


# ============================================================
# CONFIGURATION
# ============================================================

# IMPORTANT:
# Use a NEW token generated from @BotFather.
BOT_TOKEN = "8996541145:AAHAee6lM28XbeuASDRf1wTgdKehZT30-Yg"

# Put your Telegram numeric Admin ID here.
# Example:
# ADMIN_ID = 123456789
ADMIN_ID = 8755636383

# Your external HTTPS API URL.
# Example:
# EXTERNAL_API_URL = "https://example.com/api"
EXTERNAL_API_URL = "num to info"

# Telegram Bot API
TELEGRAM_API = "https://api.telegram.org/bot" + BOT_TOKEN


# ============================================================
# SEND MESSAGE
# ============================================================

def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = TELEGRAM_API + "/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": str(text)
    }

    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup)

    if parse_mode is not None:
        data["parse_mode"] = parse_mode

    try:
        response = requests.post(
            url,
            data=data,
            timeout=30
        )

        return response.json()

    except requests.exceptions.RequestException as error:
        print("sendMessage request error:", error)
        return None

    except ValueError as error:
        print("sendMessage JSON error:", error)
        return None

    except Exception as error:
        print("sendMessage unexpected error:", error)
        return None


# ============================================================
# GET UPDATES
# ============================================================

def get_updates(offset):
    url = TELEGRAM_API + "/getUpdates"

    params = {
        "offset": offset,
        "timeout": 30
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=35
        )

        return response.json()

    except requests.exceptions.RequestException as error:
        print("getUpdates request error:", error)
        return None

    except ValueError as error:
        print("getUpdates JSON error:", error)
        return None

    except Exception as error:
        print("getUpdates unexpected error:", error)
        return None


# ============================================================
# MAIN KEYBOARD
# ============================================================

def main_keyboard():
    keyboard = {
        "keyboard": [
            [
                {
                    "text": "📱 Phone Lookup"
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    return keyboard


# ============================================================
# ADMIN KEYBOARD
# ============================================================

def admin_keyboard():
    keyboard = {
        "keyboard": [
            [
                {
                    "text": "📱 Phone Lookup"
                }
            ],
            [
                {
                    "text": "👑 Admin"
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    return keyboard


# ============================================================
# WELCOME MESSAGE
# ============================================================

def send_welcome(chat_id, user_id):

    if user_id == ADMIN_ID and ADMIN_ID != 8755636383:

        message = (
            "👋 Welcome, Admin!\n\n"
            "🤖 Bot is online.\n"
            "👇 Choose an option:"
        )

        send_message(
            chat_id,
            message,
            reply_markup=admin_keyboard()
        )

    else:

        message = (
            "👋 Welcome!\n\n"
            "👇 Please choose an option:"
        )

        send_message(
            chat_id,
            message,
            reply_markup=main_keyboard()
        )


# ============================================================
# EXTERNAL API REQUEST
# ============================================================

def call_external_api(phone_number):

    if EXTERNAL_API_URL == "":
        return {
            "success": False,
            "error": "External API URL is not configured."
        }

    try:

        response = requests.get(
            EXTERNAL_API_URL,
            params={
                "phone": phone_number
            },
            timeout=30
        )

        response.raise_for_status()

        try:
            result = response.json()
        except ValueError:
            return {
                "success": False,
                "error": "API did not return valid JSON.",
                "response": response.text[:2000]
            }

        return result

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "External API request timed out."
        }

    except requests.exceptions.HTTPError as error:
        return {
            "success": False,
            "error": "External API returned an HTTP error.",
            "details": str(error)
        }

    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "error": "External API request failed.",
            "details": str(error)
        }

    except Exception as error:
        return {
            "success": False,
            "error": "Unexpected API error.",
            "details": str(error)
        }


# ============================================================
# FORMAT JSON
# ============================================================

def format_json(data):

    try:

        return json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        )

    except Exception:

        return str(data)


# ============================================================
# HANDLE MESSAGE
# ============================================================

def handle_message(message):

    if "chat" not in message:
        return

    chat_id = message["chat"]["id"]

    user_id = message.get(
        "from",
        {}
    ).get(
        "id",
        0
    )

    text = message.get(
        "text",
        ""
    )

    if not text:
        return

    print(
        "Message:",
        text,
        "| User ID:",
        user_id
    )


    # ========================================================
    # /start
    # ========================================================

    if text == "/start":

        send_welcome(
            chat_id,
            user_id
        )

        return


    # ========================================================
    # ADMIN COMMAND
    # ========================================================

    if text == "/admin":

        if user_id != ADMIN_ID or ADMIN_ID == 0:

            send_message(
                chat_id,
                "❌ You are not authorized to use admin commands."
            )

            return

        send_message(
            chat_id,
            "👑 Admin Panel\n\n"
            "✅ Bot is running.\n"
            "📡 Long polling: Active\n"
            "🔐 Admin verification: Active",
            reply_markup=admin_keyboard()
        )

        return


    # ========================================================
    # ADMIN BUTTON
    # ========================================================

    if text == "👑 Admin":

        if user_id != ADMIN_ID or ADMIN_ID == 8755636383:

            send_message(
                chat_id,
                "❌ Admin access denied."
            )

            return

        send_message(
            chat_id,
            "👑 Admin Panel\n\n"
            "🤖 Bot Status: Online\n"
            "📡 Polling: Active\n"
            "🔐 You are the administrator.",
            reply_markup=admin_keyboard()
        )

        return


    # ========================================================
    # PHONE LOOKUP BUTTON
    # ========================================================

    if text == "📱 Phone Lookup":

        send_message(
            chat_id,
            "📞 Send 10 digit mobile number:",
            reply_markup=main_keyboard()
        )

        return


    # ========================================================
    # PHONE NUMBER VALIDATION
    # ========================================================

    if text.isdigit():

        if len(text) != 10:

            send_message(
                chat_id,
                "❌ Invalid mobile number.\n\n"
                "Please send exactly 10 digits.\n\n"
                "Example:\n"
                "9876543210"
            )

            return


        # ====================================================
        # PROCESS REQUEST
        # ====================================================

        send_message(
            chat_id,
            "⏳ Processing your request..."
        )

        result = call_external_api(text)

        formatted_result = format_json(result)


        # ====================================================
        # TELEGRAM MESSAGE
        # ====================================================

        telegram_message = (
            "📋 Result:\n\n"
            + formatted_result
        )


        # Telegram messages have a size limit.
        # Keep very large API responses from failing.
        if len(telegram_message) > 3900:

            telegram_message = (
                telegram_message[:3900]
                + "\n\n...Result truncated."
            )


        send_message(
            chat_id,
            telegram_message,
            reply_markup=main_keyboard()
        )

        return


    # ========================================================
    # INVALID INPUT
    # ========================================================

    send_message(
        chat_id,
        "❌ Invalid input.\n\n"
        "Please select an option from the menu.",
        reply_markup=main_keyboard()
    )


# ============================================================
# START BOT
# ============================================================

def main():

    if BOT_TOKEN == "" or BOT_TOKEN == "8996541145:AAHAee6lM28XbeuASDRf1wTgdKehZT30-Yg":

        print("ERROR: BOT_TOKEN is not configured.")

        return


    print("====================================")
    print("Telegram Bot Started")
    print("====================================")
    print("Bot API:", TELEGRAM_API)
    print("Admin ID:", ADMIN_ID)
    print("External API:", EXTERNAL_API_URL)
    print("Polling: Active")
    print("====================================")


    # Offset for Telegram getUpdates
    offset = 0


    # ========================================================
    # LONG POLLING LOOP
    # ========================================================

    while True:

        try:

            updates = get_updates(offset)


            if updates is None:

                print(
                    "No response from Telegram. "
                    "Retrying in 3 seconds..."
                )

                time.sleep(3)

                continue


            if not updates.get("ok", False):

                print(
                    "Telegram API error:",
                    updates
                )

                time.sleep(3)

                continue


            results = updates.get(
                "result",
                []
            )


            for update in results:

                try:

                    # Move offset forward
                    update_id = update.get(
                        "update_id"
                    )

                    if update_id is not None:

                        offset = update_id + 1


                    # Process normal messages
                    if "message" in update:

                        handle_message(
                            update["message"]
                        )


                except Exception as error:

                    print(
                        "Update processing error:",
                        error
                    )


            # Small delay
            time.sleep(1)


        except KeyboardInterrupt:

            print(
                "Bot stopped manually."
            )

            break


        except Exception as error:

            print(
                "Main loop error:",
                error
            )

            time.sleep(5)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()    
    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup)

    if parse_mode is not None:
        data["parse_mode"] = parse_mode

    try:
        response = requests.post(
            url,
            data=data,
            timeout=30
        )

        return response.json()

    except Exception as error:
        print("sendMessage error:", error)
        return None


# ============================================================
# GET UPDATES
# ============================================================

def get_updates(offset):
    url = TELEGRAM_API + "/getUpdates"

    params = {
        "offset": offset,
        "timeout": 30
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=35
        )

        return response.json()

    except Exception as error:
        print("getUpdates error:", error)
        return None


# ============================================================
# MAIN KEYBOARD
# ============================================================

def main_keyboard():
    keyboard = {
        "keyboard": [
            [
                {
                    "text": "📱 Phone Lookup"
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    return keyboard


# ============================================================
# ADMIN KEYBOARD
# ============================================================

def admin_keyboard():
    keyboard = {
        "keyboard": [
            [
                {
                    "text": "📱 Phone Lookup"
                }
            ],
            [
                {
                    "text": "👑 Admin"
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    return keyboard


# ============================================================
# WELCOME MESSAGE
# ============================================================

def send_welcome(chat_id, user_id):
    if user_id == ADMIN_ID and ADMIN_ID != 8755636383:
        message = (
            "👋 Welcome, Admin!\n\n"
            "🤖 Bot is online.\n"
            "👇 Choose an option:"
        )

        send_message(
            chat_id,
            message,
            reply_markup=admin_keyboard()
        )

    else:
        message = (
            "👋 Welcome!\n\n"
            "👇 Please choose an option:"
        )

        send_message(
            chat_id,
            message,
            reply_markup=main_keyboard()
        )


# ============================================================
# EXTERNAL API REQUEST
# ============================================================

def call_external_api(phone_number):

    if EXTERNAL_API_URL == "":
        return {
            "success": False,
            "error": "External API URL is not configured."
        }

    try:
        response = requests.get(
            EXTERNAL_API_URL,
            params={
                "phone": phone_number
            },
            timeout=30
        )

        # Convert API response into JSON
        result = response.json()

        return result

    except ValueError:
        return {
            "success": False,
            "error": "API did not return valid JSON."
        }

    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "error": "API request failed.",
            "details": str(error)
        }

    except Exception as error:
        return {
            "success": False,
            "error": "Unexpected error.",
            "details": str(error)
        }


# ============================================================
# FORMAT JSON
# ============================================================

def format_json(data):
    try:
        return json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        )

    except Exception:
        return str(data)


# ============================================================
# HANDLE MESSAGE
# ============================================================

def handle_message(message):

    if "chat" not in message:
        return

    chat_id = message["chat"]["id"]

    user_id = message.get("from", {}).get("id", 0)

    text = message.get("text", "")

    if not text:
        return

    print(
        "Message:",
        text,
        "| User ID:",
        user_id
    )

    # ========================================================
    # /start
    # ========================================================

    if text == "/start":
        send_welcome(
            chat_id,
            user_id
        )
        return

    # ========================================================
    # ADMIN COMMAND
    # ========================================================

    if text == "/admin":

        if user_id != ADMIN_ID or ADMIN_ID == 8755636383:
            send_message(
                chat_id,
                "❌ You are not authorized to use admin commands."
            )
            return

        send_message(
            chat_id,
            "👑 Admin Panel\n\n"
            "✅ Bot is running.\n"
            "📡 Long polling: Active\n"
            "🔐 Admin verification: Active",
            reply_markup=admin_keyboard()
        )

        return

    # ========================================================
    # ADMIN BUTTON
    # ========================================================

    if text == "👑 Admin":

        if user_id != ADMIN_ID or ADMIN_ID == 8755636383:
            send_message(
                chat_id,
                "❌ Admin access denied."
            )
            return

        send_message(
            chat_id,
            "👑 Admin Panel\n\n"
            "🤖 Bot Status: Online\n"
            "📡 Polling: Active\n"
            "🔐 You are the administrator."
        )

        return

    # ========================================================
    # PHONE LOOKUP BUTTON
    # ========================================================

    if text == "📱 Phone Lookup":

        send_message(
            chat_id,
            "📞 Send 10 digit mobile number:",
            reply_markup=main_keyboard()
        )

        return

    # ========================================================
    # PHONE NUMBER VALIDATION
    # ========================================================

    if text.isdigit():

        if len(text) != 10:

            send_message(
                chat_id,
                "❌ Invalid mobile number.\n\n"
                "Please send exactly 10 digits.\n\n"
                "Example:\n"
                "9876543210"
            )

            return

        # ====================================================
        # PROCESS REQUEST
        # ====================================================

        send_message(
            chat_id,
            "⏳ Processing your request..."
        )

        result = call_external_api(text)

        formatted_result = format_json(result)

        # Telegram HTML <pre> block
        telegram_message = (
            "<pre>"
            + formatted_result
            + "</pre>"
        )

        send_message(
            chat_id,
            telegram_message,
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

        return

    # ========================================================
    # INVALID INPUT
    # ========================================================

    send_message(
        chat_id,
        "❌ Invalid input.\n\n"
        "Please select an option from the menu.",
        reply_markup=main_keyboard()
    )


# ============================================================
# START BOT
# ============================================================

def main():

    if BOT_TOKEN == "":
        print("ERROR: BOT_TOKEN is empty.")
        return

    print("====================================")
    print("Telegram Bot Started")
    print("====================================")
    print("Bot API:", TELEGRAM_API)
    print("Admin ID:", ADMIN_ID)
    print("External API:", EXTERNAL_API_URL)
    print("Polling: Active")
    print("====================================")

    # Offset for Telegram getUpdates
    offset = 0

    # ========================================================
    # LONG POLLING LOOP
    # ========================================================

    while True:

        updates = get_updates(offset)

        if updates is None:
            time.sleep(3)
            continue

        if not updates.get("ok"):

            print(
                "Telegram API error:",
                updates
            )

            time.sleep(3)
            continue

        results = updates.get(
            "result",
            []
        )

        for update in results:

            try:

                # Move offset forward
                offset = update["update_id"] + 1

                # Process normal messages
                if "message" in update:

                    handle_message(
                        update["message"]
                    )

            except Exception as error:

                print(
                    "Update processing error:",
                    error
                )

        # Small delay
        time.sleep(1)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()        
    { "keyboard": [...] }
    [
                {
                    "text": "📱 Phone Lookup"
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False


# ============================================================
# WELCOME MESSAGE
# ============================================================

def send_welcome(chat_id):
    message = (
        "👋 Welcome!\n\n"
        "Please choose an option from the menu below."
    )

    send_message(
        chat_id,
        message,
        reply_markup=main_keyboard()
    )


# ============================================================
# EXTERNAL API
# ============================================================

def call_external_api(phone_number):
    if EXTERNAL_API_URL == "":
        return {
            "success": False,
            "error": "EXTERNAL_API_URL is not configured."
        }

    try:
        # Adjust the parameter name to match your own authorized API.
        response = requests.get(
            EXTERNAL_API_URL,
            params={
                "phone": phone_number
            },
            timeout=30
        )

        # Convert API response to JSON
        return response.json()

    except ValueError:
        return {
            "success": False,
            "error": "External API did not return valid JSON."
        }

    except Exception as error:
        return {
            "success": False,
            "error": "External API request failed.",
            "details": str(error)
        }


# ============================================================
# HANDLE TEXT MESSAGES
# ============================================================

def handle_message(message):
    if "chat" not in message:
        return

    chat_id = message["chat"]["id"]

    text = message.get("text", "")

    if not text:
        return

    # --------------------------------------------------------
    # /start command
    # --------------------------------------------------------

    if text == "/start":
        send_welcome(chat_id)
        return

    # --------------------------------------------------------
    # Phone Lookup button
    # --------------------------------------------------------

    if text == "📱 Phone Lookup":
        send_message(
            chat_id,
            "📞 Send 10 digit mobile number:",
            reply_markup=main_keyboard()
        )
        return

    # --------------------------------------------------------
    # Validate mobile number
    # --------------------------------------------------------

    if text.isdigit():

        if len(text) != 10:
            send_message(
                chat_id,
                "❌ Invalid number.\n\n"
                "Please send exactly 10 digits."
            )
            return

        # ----------------------------------------------------
        # Call authorized external API
        # ----------------------------------------------------

        send_message(
            chat_id,
            "⏳ Processing your request..."
        )

        result = call_external_api(text)

        # Convert Python object to formatted JSON
        formatted_json = json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )

        # Telegram HTML message
        output = "<pre>" + formatted_json + "</pre>"

        send_message(
            chat_id,
            output,
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

        return

    # --------------------------------------------------------
    # Invalid input
    # --------------------------------------------------------

    send_message(
        chat_id,
        "❌ Invalid input.\n\n"
        "Please use the menu or send a valid 10-digit number.",
        reply_markup=main_keyboard()
    )


# ============================================================
# MAIN LONG-POLLING LOOP
# ============================================================

def main():
    if BOT_TOKEN == "":
        print("ERROR: Please enter your BOT_TOKEN.")
        return

    print("Bot started.")
    print("Long polling is running...")

    offset = 0

    while True:

        updates = get_updates(offset)

        if updates is None:
            time.sleep(3)
            continue

        if not updates.get("ok"):
            print("Telegram API error:", updates)
            time.sleep(3)
            continue

        for update in updates.get("result", []):

            # Move offset forward so the same update
            # is not processed again.
            offset = update["update_id"] + 1

            try:
                if "message" in update:
                    handle_message(update["message"])

            except Exception as error:
                print("Message handling error:", error)

        # Small delay prevents excessive CPU usage.
        time.sleep(1)


# ============================================================
# START BOT
# ============================================================

if __name__ == "__main__":
    main()
