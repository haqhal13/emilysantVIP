from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
from datetime import datetime

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

START_TIME = datetime.now()

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


# Main Application
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_payment, pattern="payment"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern="paid"))
    application.add_handler(CallbackQueryHandler(handle_support, pattern="support"))

    # Start Long Polling
    logger.info("Bot is starting with long polling...")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
