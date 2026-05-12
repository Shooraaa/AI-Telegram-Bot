import os
from dotenv import load_dotenv
from groq import Groq

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load ENV
load_dotenv("safe.env")

# Tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq setup
client = Groq(
    api_key=GROQ_API_KEY
)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Bot Active\n\nMujhe koi bhi question bhejo."
    )

# Reply system
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model="llama-3.3-70b-versatile",
        )

        bot_reply = chat_completion.choices[0].message.content

        await update.message.reply_text(bot_reply)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Telegram app
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        reply
    )
)

print("Bot Running...")

# Run bot
app.run_polling()