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
        "lifetime": "https://5fbqad-qz.myshopify.com/cart/50160363766106:1",
    },
    "media": "https://5fbqad-qz.myshopify.com/cart/50160363766106:1",  # Replace with your media app URL
    "paypal": "onlyvipfan@outlook.com",
}

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()
telegram_app = None
START_TIME = datetime.now()


# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Lifetime (£10.00)", callback_data="select_lifetime")],
        [InlineKeyboardButton("Media App", web_app=WebAppInfo(url=PAYMENT_INFO["media"]))],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    await update.message.reply_text(
        "💎 **Welcome to the VIP Bot!**\n\n"
        "💎 *Get lifetime access to thousands of creators!*\n"
        "⚡ *Instant access to the VIP link sent directly to your email!*\n"
        "⭐ *Don’t see the model you’re looking for? We’ll add them within 24–72 hours!*\n\n"
        "📌 Got questions? VIP link not working? Contact support 🔍👀",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def handle_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_text = "LIFETIME"
    keyboard = [
        [InlineKeyboardButton("💳 Pay Now via Shopify", web_app=WebAppInfo(url=PAYMENT_INFO["shopify"]["lifetime"]))],
        [InlineKeyboardButton("📧 PayPal Option", callback_data="payment_paypal")],
        [InlineKeyboardButton("💬 Support", callback_data="support")],
        [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
    ]

    message = (
        f"⭐ You have chosen the **{plan_text}** plan.\n\n"
        "💳 **Pay Now via Shopify:** Instant VIP access delivered to your email.\n"
        "📧 **PayPal Option:** Manually processed, VIP link sent manually.\n\n"
        "🎉 Choose your preferred payment method below and get access today!"
    )
    await query.edit_message_text(
        text=message, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "payment_paypal":
        message = (
            "💸 **Easy Payment with PayPal!**\n\n"
            "➡️ **Send Payment To:**\n"
            f"`{PAYMENT_INFO['paypal']}`\n\n"
            "💎 **Lifetime Access:** **£10.00 GBP** 🎉\n\n"
            "✅ Once payment is complete, click 'I've Paid' to confirm."
        )
        keyboard = [
            [InlineKeyboardButton("✅ I've Paid", callback_data="paid")],
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
        ]
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )


async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    username = query.from_user.username or "No Username"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await query.edit_message_text(
        text="✅ Payment received! Your VIP link will be sent soon.",
        parse_mode="Markdown"
    )

    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"📝 **Payment Notification**\n"
            f"👤 **User:** @{username}\n"
            f"📋 **Plan:** Lifetime\n"
            f"🕒 **Time:** {current_time}"
        ),
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

    async with httpx.AsyncClient() as client:
        response = await client.get(UPTIME_MONITOR_URL)
        logger.info(f"Uptime Monitoring Response: {response.status_code}")

    await telegram_app.initialize()


@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}


@app.get("/uptime")
async def get_uptime():
    current_time = datetime.now()
    uptime_duration = current_time - START_TIME
    return JSONResponse(content={
        "status": "online",
        "uptime": str(uptime_duration),
        "start_time": START_TIME.strftime("%Y-%m-%d %H:%M:%S")
    })
