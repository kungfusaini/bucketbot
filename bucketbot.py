#!/usr/bin/env python3

import os
import sys
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# States for conversation
WAITING_FOR_CONTENT = 1

def load_config():
    """Load API key and bot token from environment variables"""
    bot_token = os.getenv('BUCKETBOT_TOKEN')
    api_key = os.getenv('WELL_API_KEY')
    
    if not bot_token:
        print("Error: BUCKETBOT_TOKEN environment variable not set")
        sys.exit(1)
    
    if not api_key:
        print("Error: WELL_API_KEY environment variable not set")
        sys.exit(1)
    
    return bot_token, api_key

def get_type_by_choice(choice):
    """Convert choice text to entry type"""
    choice_map = {'Task': 'task', 'Note': 'note', 'Bookmark': 'bookmark'}
    return choice_map.get(choice)

def post_entry(base_url, headers, entry_type, content):
    """Post entry to API"""
    try:
        response = requests.post(
            base_url,
            json={'type': entry_type, 'body': content},
            headers=headers
        )
        return response.status_code, response.text
    except Exception as e:
        return 0, f"Network error: {str(e)}"

# Create keyboard for type selection
TYPE_KEYBOARD = ReplyKeyboardMarkup(
    [["Task"], ["Note"], ["Bookmark"]],
    resize_keyboard=True,
    one_time_keyboard=False
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the bot and show type selection"""
    await update.message.reply_text(
        "🚀 *Bucket Bot Ready!*\n\n"
        "Select entry type:",
        reply_markup=TYPE_KEYBOARD,
        parse_mode='Markdown'
    )
    return WAITING_FOR_CONTENT

async def handle_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle type selection and ask for content"""
    choice = update.message.text
    entry_type = get_type_by_choice(choice)
    
    if not entry_type:
        await update.message.reply_text(
            "❌ Invalid selection. Please choose Task, Note, or Bookmark.",
            reply_markup=TYPE_KEYBOARD
        )
        return WAITING_FOR_CONTENT
    
    # Store the selected type
    context.user_data['entry_type'] = entry_type
    context.user_data['type_display'] = choice
    
    await update.message.reply_text(
        f"✅ Selected: *{choice}*\n\n"
        f"Now enter your {choice.lower()} content:",
        parse_mode='Markdown'
    )
    return WAITING_FOR_CONTENT

async def handle_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle content entry and post to API"""
    content = update.message.text.strip()
    entry_type = context.user_data.get('entry_type')
    type_display = context.user_data.get('type_display', 'Entry')
    
    # Check if this is a type selection or content
    if get_type_by_choice(update.message.text):
        return await handle_type_selection(update, context)
    
    # Validate content
    if not content:
        await update.message.reply_text(
            "❌ Content cannot be empty. Please enter some text:",
            parse_mode='Markdown'
        )
        return WAITING_FOR_CONTENT
    
    # Post to API
    api_config = context.bot_data.get('api_config')
    if not api_config:
        await update.message.reply_text(
            "❌ API configuration error. Please restart the bot with /start",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    base_url, headers = api_config
    status_code, response_text = post_entry(base_url, headers, entry_type, content)
    
    # Display result
    if status_code in [200, 201]:
        await update.message.reply_text(
            f"✅ *{type_display} posted successfully!*\n\n"
            f"Status: {status_code}\n"
            f"Response: {response_text}\n\n"
            f"Select next entry type:",
            reply_markup=TYPE_KEYBOARD,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ *Failed to post {type_display.lower()}*\n\n"
            f"Status: {status_code}\n"
            f"Response: {response_text}\n\n"
            f"Please try again or select a different type:",
            reply_markup=TYPE_KEYBOARD,
            parse_mode='Markdown'
        )
    
    # Clear stored data and return to type selection
    context.user_data.clear()
    return WAITING_FOR_CONTENT

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message"""
    await update.message.reply_text(
        "🤖 *Bucket Bot Help*\n\n"
        "1. Select an entry type: Task, Note, or Bookmark\n"
        "2. Enter your content\n"
        "3. Bot posts it and shows the result\n"
        "4. Repeat!\n\n"
        "Commands:\n"
        "/start - Begin using the bot\n"
        "/help - Show this help message\n\n"
        "Ready to post!",
        reply_markup=TYPE_KEYBOARD,
        parse_mode='Markdown'
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current operation"""
    await update.message.reply_text(
        "Operation cancelled. Use /start to begin again.",
        reply_markup=TYPE_KEYBOARD
    )
    context.user_data.clear()
    return ConversationHandler.END

def main():
    """Main bot function"""
    # Load configuration
    bot_token, api_key = load_config()
    
    # API configuration
    base_url = "https://vulkan.sumeetsaini.com/well"
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Store API config in bot_data
    application.bot_data['api_config'] = (base_url, headers)
    
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_CONTENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_content)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_user=True,
        per_chat=True,
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))
    
    # Start the bot
    print("🚀 Starting Bucket Bot...")
    application.run_polling()

if __name__ == '__main__':
    main()