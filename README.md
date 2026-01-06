# Telegram Bucket Bot

A Telegram bot for accessing my `Well API`. This is a telegram version of my
[Bucket](https://github.com/kungfusaini/bucket) script so I can have the same functionality on mobile

## Environment Variables

**Required:**
```bash
BUCKETBOT_TOKEN=your_telegram_bot_token
WELL_API_KEY=your_vulkan_api_key
TELEGRAM_ID=your_authorized_telegram_user_id
```

## Usage

1. Send `/start` to begin
2. Select entry type: Task, Note, or Bookmark
3. Enter your content
4. Bot posts it and shows the response
5. Ready for the next entry!

## Commands

- `/start` - Begin using the bot
- `/help` - Show help message
- `/cancel` - Cancel current operation

## Security

This bot is restricted to the Telegram user ID specified in the `TELEGRAM_ID` environment variable. Unauthorized users will receive an access denied message.
