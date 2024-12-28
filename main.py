import time
from typing import Final
from telegram import Update, ChatMemberUpdated
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = '7979270240:AAEzwvheVoyjqA71f9ErbYOAYCWfLWWHyt0'
BOT_USERNAME = '@planmarks_watchdog_bot'

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('How may I help you?')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Please message aleks@planmarks.eu')

# Response handler
def handle_response(text: str) -> str:
    processed: str = text.lower()
    if 'hello' in processed:
        return 'Hello there!'
    if 'how are you' in processed:
        return 'Good, thank you!'
    return 'I do not understand what you are trying to say...'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text

    # Debug messages
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Log the error
    print(f"Update {update} caused error {context.error}")

# New attempt start - Delete if not working
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome, {member.full_name}! Glad to have you here!")
# New attempt end - Delete if not working
# New attempt start - Delete if not working
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text

    # Debug messages
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            if 'rules' in new_text or 'reeglid' in new_text:
                rules_response = "Here are the rules of the group:\n1. Be respectful.\n2. No spamming.\n3. Follow the topics.\n..."
                await update.message.reply_text(rules_response)
                return
            
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

# New attempt end - Delete if not working
# New attempt start - Delete if not working
from collections import defaultdict

user_warnings = defaultdict(int)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text

    # Debug messages
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            if 'rules' in new_text or 'reeglid' in new_text:
                rules_response = "Here are the rules of the group:\n1. Be respectful.\n2. No spamming.\n3. Follow the topics.\n..."
                await update.message.reply_text(rules_response)
                return
            
            response: str = handle_response(new_text)
        else:
            # Check for spam (e.g., repeated messages or excessive emojis)
            if is_spam(text):
                user_warnings[update.message.from_user.id] += 1
                if user_warnings[update.message.from_user.id] >= 3:
                    await context.bot.restrict_chat_member(
                        chat_id=update.message.chat.id,
                        user_id=update.message.from_user.id,
                        until_date=int(time.time()) + 3600  # Mute for 1 hour
                    )
                    await update.message.reply_text("You have been muted for spamming.")
                else:
                    await update.message.reply_text(f"Warning! This is your {user_warnings[update.message.from_user.id]} warning for spam.")
                return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

def is_spam(text: str) -> bool:
    # Basic spam detection logic (e.g., too many identical messages)
    # Implement your own logic based on your requirements
    return text.lower().count("spam") > 2  # Example: Replace with actual logic

# New attempt end - Delete if not working
# New attempt start - Delete if not working
FORBIDDEN_WORDS = ['neeger', 'nigger']

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text

    # Debug messages
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if any(word in text.lower() for word in FORBIDDEN_WORDS):
        await update.message.delete()
        user_warnings[update.message.from_user.id] += 1
        if user_warnings[update.message.from_user.id] >= 3:
            await context.bot.restrict_chat_member(
                chat_id=update.message.chat.id,
                user_id=update.message.from_user.id,
                until_date=int(time.time()) + 3600  # Mute for 1 hour
            )
            await update.message.reply_text("You have been muted for using forbidden words.")
        else:
            await update.message.reply_text(f"Warning! This is your {user_warnings[update.message.from_user.id]} warning for using forbidden words.")
        return

# New attempt end - Delete if not working

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('contact', contact_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Errors
    app.add_error_handler(error)

    # Check for messages every 3 seconds
    print('Polling...')
    app.run_polling(poll_interval=3)
