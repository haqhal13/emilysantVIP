import os
from datetime import datetime
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Constants from environment
BOT_TOKEN = os.getenv("7561766699:AAGjpzhb8zDqc2-VrnzvXZZnu2-nEqfoXVU")
SUPPORT_CONTACT = os.getenv("SUPPORT_CONTACT", "@ZakiVip1")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "834523364"))

# Payment Info (hardcoded or replace with env if preferred)
PAYMENT_INFO = {
    "Apple Pay & Google Pay": "https://5fbqad-qz.myshopify.com/cart/50289205936474:1",
    "paypal": "@OFVIPFAN ON PAYPAL",
    "crypto": "https://t.me/+t5kEU2mSziQ1NTg0",
}

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# FastAPI app and global vars
app = FastAPI()
telegram_app = None
START_TIME = datetime.now()

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Apple Pay & Google Pay", web_app=WebAppInfo(url=PAYMENT_INFO["Apple Pay & Google Pay"]))],
        [InlineKeyboardButton("PayPal Payment", callback_data="payment_paypal")],
        [InlineKeyboardButton("Crypto Payment", callback_data="payment_crypto")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    await update.message.reply_text(
        "💎 **HoneyPot & Emily Sant!**\n\n"
        "⚡ 3 short videos + 1 lingerie pic included only! Access our Tele group with payment options below.\n\n"
        "⚡ ONLY £5 LIMITED TIME!\n\n"
        "⚡ Pay with Apple Pay or Google Pay emailed instantly!\n\n"
        "📌 Got questions? Contact support 🔍👀",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

async def handle_paypal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("✅ Thank You for Payment", callback_data="thank_you")],
        [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
    ]
    await query.edit_message_text(
        text=f"💸 **Pay with PayPal!**\n\n➡️ **Send Payment To:**\n`{PAYMENT_INFO['paypal']}`\n\n✅ After completing the payment, click 'Thank You for Payment'.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def handle_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("✅ Thank You for Payment", callback_data="thank_you")],
        [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
    ]
    await query.edit_message_text(
        text=f"⚡ **Pay with Crypto!**\n\n🔗 [Crypto Payment Link]({PAYMENT_INFO['crypto']})\n\n✅ After completing the payment, click 'Thank You for Payment'.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def handle_thank_you(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="✅ **Thank you for your payment!**\n\nOur team will process your request shortly. Show payment to @zakivip1. If you paid with Apple Pay or Google Pay, it has been emailed to you.",
        parse_mode="Markdown"
    )

async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=f"💬 Need help? Contact support at {SUPPORT_CONTACT}.",
        parse_mode="Markdown"
    )

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(query, context)

# Startup hook
@app.on_event("startup")
async def startup_event():
    global telegram_app
    telegram_app = Application.builder().token(BOT_TOKEN).build()

    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(handle_paypal, pattern="payment_paypal"))
    telegram_app.add_handler(CallbackQueryHandler(handle_crypto, pattern="payment_crypto"))
    telegram_app.add_handler(CallbackQueryHandler(handle_thank_you, pattern="thank_you"))
    telegram_app.add_handler(CallbackQueryHandler(handle_back, pattern="back"))
    telegram_app.add_handler(CallbackQueryHandler(handle_support, pattern="support"))

    logger.info("Telegram Bot Initialized!")
    await telegram_app.initialize()

# Telegram webhook endpoint
@app.post("/webhook")
async def telegram_webhook(request: Request):
    global telegram_app
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

# Health check route
@app.get("/healthz")
async def health_check():
    return JSONResponse(content={
        "status": "ok",
        "uptime_seconds": (datetime.now() - START_TIME).total_seconds()
    })
