from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import logging
import httpx
from datetime import datetime
from fastapi.responses import JSONResponse

# Constants
BOT_TOKEN = "8189375655:AAHsnhP49ZHqEK04uaEtcPeh3alikBhfVeY"
UPTIME_MONITOR_URL = "https://emilysantvip.onrender.com/uptime"
SUPPORT_CONTACT = "@ZakiVip1"
ADMIN_CHAT_ID = 834523364  # Replace with the admin's chat ID

# Payment Information
PAYMENT_INFO = {
    "shopify": {
        "1_month": "https://5fbqad-qz.myshopify.com/cart/50086610207066:1",
        "lifetime": "https://5fbqad-qz.myshopify.com/cart/50160363766106:1",
    },
    "crypto": {"link": "https://t.me/+t5kEU2mSziQ1NTg0"},
    "paypal": "onlyvipfan@outlook.com",
}

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()
telegram_app = None
START_TIME = datetime.now()

@app.on_event("startup")
async def startup_event():
    global telegram_app
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(handle_subscription, pattern="select_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_payment, pattern="payment_.*"))
    telegram_app.add_handler(CallbackQueryHandler(confirm_payment, pattern="paid"))
    telegram_app.add_handler(CallbackQueryHandler(handle_back, pattern="back"))
    telegram_app.add_handler(CallbackQueryHandler(handle_support, pattern="support"))

    logger.info("Telegram Bot Initialized!")

    # Uptime Robot Monitoring
    async with httpx.AsyncClient() as client:
        await client.get(UPTIME_MONITOR_URL)
        logger.info("Uptime Monitoring Reintegrated!")

    await telegram_app.initialize()
    await telegram_app.start_polling()

@app.get("/uptime")
async def get_uptime():
    current_time = datetime.now()
    uptime_duration = current_time - START_TIME
    return JSONResponse(content={
        "status": "online",
        "uptime": str(uptime_duration),
        "start_time": START_TIME.strftime("%Y-%m-%d %H:%M:%S")
    })

# Start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1 Month (£6.75)", callback_data="select_1_month")],
        [InlineKeyboardButton("Lifetime (£10.00)", callback_data="select_lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    await update.message.reply_text(
        "💎 **Welcome to the VIP Bot!**\n\n"
        "💎 *Get access to thousands of creators every month!*\n"
        "⚡ *Instant access to the VIP link sent directly to your email!*\n"
        "⭐ *Don’t see the model you’re looking for? We’ll add them within 24–72 hours!*\n\n"
        "📌 Got questions ? VIP link not working ? Contact support 🔍👀",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

# Other handlers (handle_subscription, handle_payment, confirm_payment, handle_support, handle_back) remain the same
