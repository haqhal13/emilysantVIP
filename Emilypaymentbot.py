from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging

# Constants
BOT_TOKEN = "8189375655:AAHsnhP49ZHqEK04uaEtcPeh3alikBhfVeY"  # Replace with your Telegram bot token
PAYPAL_EMAIL = "onlyvipfan@outlook.com"  # Replace with your PayPal email
MEDIA_APP_LINK = "https://google.com"  # Replace with your media app link

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# Start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Pay via PayPal", callback_data="paypal")],
        [InlineKeyboardButton("Pay via Media App", url=MEDIA_APP_LINK)]
    ]
    await update.message.reply_text(
        "💬 **Welcome to the Mini Payment Bot!**\n\n"
        "📜 Description:\n"
        "- Get access to exclusive content for just **£8**.\n\n"
        "💳 Choose a payment method below to proceed.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# PayPal Callback Handler
async def handle_paypal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message = (
        "💳 **Pay Securely via PayPal!**\n\n"
        f"➡️ **Send Payment To:**\n`{PAYPAL_EMAIL}`\n\n"
        "💰 **Price:** £8.00\n\n"
        "✅ Once payment is complete, contact support with your transaction ID to verify."
    )
    keyboard = [
        [InlineKeyboardButton("🔙 Go Back", callback_data="start")]
    ]
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Callback Handler for Go Back
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update.callback_query, context)

# Main Function to Run the Bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_paypal, pattern="paypal"))
    application.add_handler(CallbackQueryHandler(go_back, pattern="start"))

    # Start the bot
    logger.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
