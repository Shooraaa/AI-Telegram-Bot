import os
import requests

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

# Flask for Render
from flask import Flask
from threading import Thread

# Flask app
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run():
    app_flask.run(host='0.0.0.0', port=10000)

t = Thread(target=run)
t.start()

# Load ENV
load_dotenv("safe.env")

# Tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Groq AI setup
client = Groq(
    api_key=GROQ_API_KEY
)

# AI Image Generator
async def generate_image(update: Update, prompt: str):

    API_URL = (
        "https://api-inference.huggingface.co/models/"
        "stabilityai/stable-diffusion-2"
    )

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    try:

        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt
            },
            timeout=120
        )

        # Success
        if response.status_code == 200:

            with open("generated_image.png", "wb") as f:
                f.write(response.content)

            await update.message.reply_photo(
                photo=open("generated_image.png", "rb")
            )

        else:

            print(response.text)

            await update.message.reply_text(
                "❌ Image generation failed.\nTry again in 1 minute."
            )

    except Exception as e:

        await update.message.reply_text(
            f"Error: {e}"
        )

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "✨ Welcome to AiBuddy Bot 🚀"
    )

# Reply system
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_message = update.message.text

    # Image command
    if user_message.startswith("/image"):

        prompt = user_message.replace(
            "/image",
            ""
        ).strip()

        if not prompt:

            await update.message.reply_text(
                "Usage:\n/image futuristic lion king"
            )

            return

        await update.message.reply_text(
            "🎨 AI image bana raha hu..."
        )

        await generate_image(update, prompt)

        return

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

        bot_reply = (
            chat_completion
            .choices[0]
            .message
            .content
        )

        await update.message.reply_text(
            bot_reply
        )

    except Exception as e:

        await update.message.reply_text(
            f"Error: {e}"
        )

# Telegram app
app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .build()
)

# Handlers
app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        reply
    )
)

print("Bot Running...")

# Run bot
app.run_polling()