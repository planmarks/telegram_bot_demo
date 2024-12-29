from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from collections import defaultdict
import time
import re

TOKEN: Final = '7979270240:AAEzwvheVoyjqA71f9ErbYOAYCWfLWWHyt0'  # Replace with your actual token
BOT_USERNAME = '@planmarks_watchdog_bot'

# Global variables for spam detection and warnings
user_warnings = defaultdict(int)
user_last_messages = defaultdict(list)
user_last_time = defaultdict(float)
FORBIDDEN_WORDS = ['neeger', 'nigger', 'nigga', 'hälvar', 'retard', 'russ']

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! How may I help you?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Here is a list of helpful commands.')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Please message aleks@planmarks.eu.')

# Welcome new members
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome, {member.full_name}! Glad to have you here!")

# Handle responses
def handle_response(text: str) -> str:
    processed = text.lower()
    if 'hello' in processed:
        return 'Hello there!'
    if 'how are you' in processed:
        return 'Good, thank you!'
    return 'I do not understand what you are trying to say...'

# Spam detection
def is_spam(text: str, user_id: int) -> bool:
    user_last_messages[user_id].append(text.lower())
    if len(user_last_messages[user_id]) > 5:
        user_last_messages[user_id].pop(0)

    if all(msg == text.lower() for msg in user_last_messages[user_id]):
        return True

    emoji_count = len(re.findall(r'[^\w\s]', text))
    if emoji_count > 5:
        return True

    current_time = time.time()
    if current_time - user_last_time[user_id] < 2:
        return True
    user_last_time[user_id] = current_time

    return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    username = update.message.from_user.username or update.message.from_user.first_name

    # Debugging
    print(f'User ({user_id}) in {message_type}: "{text}"')

    # Check for forbidden words
    if any(word in text.lower() for word in FORBIDDEN_WORDS):
        await update.message.delete()  # Delete the offending message
        user_warnings[user_id] += 1  # Increment the user's warning count

        if message_type in ['group', 'supergroup']:
            # Notify the group and the user
            if user_warnings[user_id] >= 3:
                # Mute the user for 1 hour if they reach 3 warnings
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    until_date=int(time.time()) + 3600  # Mute for 1 hour
                )
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"@{username}, your message was removed for using forbidden words. "
                        "You have been muted for 1 hour due to repeated offenses."
                    )
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"@{username}, your message was removed for using forbidden words. "
                        f"This is your {user_warnings[user_id]} warning. "
                        "Three warnings will result in a 1-hour mute."
                    )
                )
        elif message_type == 'private':
            # Notify the user directly in private chat
            if user_warnings[user_id] >= 3:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="You have been muted for 1 hour due to repeated offenses for using forbidden words."
                )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"Your message was removed for using forbidden words. "
                        f"This is your {user_warnings[user_id]} warning. "
                        "Three warnings will result in a 1-hour mute."
                    )
                )
        return

    # Only respond to mentions or commands
    if BOT_USERNAME in text or text.startswith('/'):
        # Process spam
        if is_spam(text, user_id):
            user_warnings[user_id] += 1
            if user_warnings[user_id] >= 3:
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    until_date=int(time.time()) + 3600
                )
                await context.bot.send_message(chat_id=chat_id, text="You have been muted for spamming.")
            else:
                await context.bot.send_message(chat_id=chat_id, text=f"Warning! This is your {user_warnings[user_id]} warning for spam.")
            return

        # Generate and send response
        response = handle_response(text)
        await context.bot.send_message(chat_id=chat_id, text=response)


# Error handling
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('contact', contact_command))

    # Welcome new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handling
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling()
