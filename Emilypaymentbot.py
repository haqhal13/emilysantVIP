from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import logging
from datetime import datetime
from fastapi.responses import JSONResponse

# Constants
BOT_TOKEN = "8189375655:AAHsnhP49ZHqEK04uaEtcPeh3alikBhfVeY"
SUPPORT_CONTACT = "@ZakiVip1"
ADMIN_CHAT_ID = 834523364  # Replace with the admin's chat ID

# Payment Information
PAYMENT_INFO = {
    "paypal": "onlyvipfan@outlook.com",  # Replace with your PayPal address
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
    telegram_app.add_handler(CallbackQueryHandler(handle_payment, pattern="payment"))
    telegram_app.add_handler(CallbackQueryHandler(confirm_payment, pattern="paid"))
    telegram_app.add_handler(CallbackQueryHandler(handle_support, pattern="support"))

    logger.info("Telegram Bot Initialized!")
    await telegram_app.initialize()
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    await telegram_app.start()


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


# Start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("£8 Telegram Access", callback_data="payment")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    await update.message.reply_text(
        "🌟 **Welcome!**\n\n"
        "📹 Get access to Emily Sant's OnlyFans content for just **£8**!\n\n"
        "✨ Content includes:\n"
        "- 2 short videos from her OnlyFans wall posts\n"
        "- 1 PPV video\n\n"
        "💸 Make a payment to gain instant access to this exclusive content!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# Handle Payment
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message = (
        "💳 **Pay Securely via PayPal!**\n\n"
        "➡️ **Send Payment To:**\n"
        f"`{PAYMENT_INFO['paypal']}`\n\n"
        "💰 **Price:** £8.00\n\n"
        "✅ Once payment is complete, click 'I've Paid' to confirm and receive your access."
    )
    keyboard = [
        [InlineKeyboardButton("✅ I've Paid", callback_data="paid")],
        [InlineKeyboardButton("🔙 Go Back", callback_data="start")],
    ]
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# Confirm Payment and Notify Admin
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    username = query.from_user.username or "No Username"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Notify Admin
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"📝 **Payment Notification**\n"
            f"👤 **User:** @{username}\n"
            f"💰 **Amount:** £8.00\n"
            f"🕒 **Time:** {current_time}"
        ),
        parse_mode="Markdown",
    )

    # Acknowledge user
    await query.edit_message_text(
        text=(
            "✅ **Payment Received! Thank You!** 🎉\n\n"
            "📩 Please send your **PayPal transaction ID** to our support team for verification.\n"
            f"👉 {SUPPORT_CONTACT}\n\n"
            "⚡ Your access link will be sent shortly after verification."
        ),
        parse_mode="Markdown",
    )


# Support Handler
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=(
            "💬 **Need Assistance? We're Here to Help!**\n\n"
            f"📨 For support, contact us directly at:\n"
            f"👉 {SUPPORT_CONTACT}\n\n"
            "⚡ Our team will respond as quickly as possible."
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Go Back", callback_data="start")]
        ]),
        parse_mode="Markdown",
    )
