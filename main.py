import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------- Config (read from Railway environment variables) ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_API_KEY = os.getenv("DATA_API_KEY")
# Example endpoint — replace with your chosen provider's real URL
DATA_API_URL = os.getenv("DATA_API_URL", "https://api.fxmacrodata.com/v1/calendar/usd")

if not BOT_TOKEN:
    raise SystemExit("ERROR: BOT_TOKEN environment variable is not set.")

# ---------- Command handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to FX Compass!\n\n"
        "Commands:\n"
        "/news — latest forex economic event\n"
        "/help — show this menu"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Available commands:\n"
        "/start — welcome message\n"
        "/news — fetch the latest high-impact forex event\n"
        "/help — this menu"
    )

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not DATA_API_KEY:
        await update.message.reply_text("⚠️ Data API key is not configured on the server.")
        return

    try:
        headers = {"X-API-Key": DATA_API_KEY}
        resp = requests.get(DATA_API_URL, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # Adapt this block to your provider's actual JSON structure.
        events = data.get("data") or data.get("events") or []
        if not events:
            await update.message.reply_text("📭 No upcoming forex events found right now.")
            return

        event = events[0]
        indicator = event.get("indicator", event.get("title", "N/A"))
        actual = event.get("actual", "N/A")
        expected = event.get("expected", "N/A")
        currency = event.get("currency", "N/A")
        when = event.get("date", event.get("time", "N/A"))

        msg = (
            f"📊 Forex Update\n"
            f"Currency: {currency}\n"
            f"Event: {indicator}\n"
            f"Actual: {actual}  |  Expected: {expected}\n"
            f"Time: {when}"
        )
        await update.message.reply_text(msg)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Network/API error: {str(e)[:200]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Unexpected error: {str(e)[:200]}")

# ---------- Entry point ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("news", news))
    print("FX Compass bot is running (long polling)...")
    app.run_polling()

if __name__ == "__main__":
    main()  
