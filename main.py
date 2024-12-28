from typing import Final
from telegram import Update, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import asyncio

TOKEN: Final = '7979270240:AAEzwvheVoyjqA71f9ErbYOAYCWfLWWHyt0'
BOT_USERNAME = '@planmarks_watchdog_bot'

# List of offensive words
OFFENSIVE_WORDS = ["neeger", "nigga", "nigger"]

# Dictionary to track user warnings
warnings = {}

# Welcome message function
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome, {member.full_name}! 🎉 Please follow the group rules.")

# Anti-Spam Management: Filter offensive words
async def filter_offensive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()
    chat_id = update.effective_chat.id

    if any(word in text for word in OFFENSIVE_WORDS):
        # Issue a warning or mute
        warnings[user_id] = warnings.get(user_id, 0) + 1
        if warnings[user_id] == 1:
            await update.message.reply_text(
                f"⚠️ Warning! Offensive language is not allowed. ({warnings[user_id]}/3)"
            )
        elif warnings[user_id] >= 3:
            warnings[user_id] = 0
            await context.bot.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(can_send_messages=False),
                until_date=asyncio.time() + 3600,
            )
            await update.message.reply_text(
                f"🚫 {update.effective_user.full_name} has been muted for 1 hour."
            )

# Command to show group rules
async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 Group Rules:\n1. Be respectful\n2. No offensive language\n3. Follow all Telegram guidelines")

# Command to show help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Available Commands:\n/rules - Show group rules\n/help - Show available commands")

# Command to warn a user
async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to warn a user.")
        return

    user_id = update.message.reply_to_message.from_user.id
    warnings[user_id] = warnings.get(user_id, 0) + 1
    await update.message.reply_text(f"⚠️ User has been warned! ({warnings[user_id]}/3)")

# Command to mute a user
async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to mute a user.")
        return

    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id

    await context.bot.restrict_chat_member(
        chat_id,
        user_id,
        ChatPermissions(can_send_messages=False),
        until_date=asyncio.time() + 3600,
    )
    await update.message.reply_text("🚫 User has been muted for 1 hour.")

# Mention management
async def mention_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.bot.username in update.message.text:
        await update.message.reply_text("👋 How can I assist you?")

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

# Main function
def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), filter_offensive))
    app.add_handler(CommandHandler("rules", rules_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("warn", warn_command))
    app.add_handler(CommandHandler("mute", mute_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("@"), mention_management))

    app.add_error_handler(error)

    # Run the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()