import os
import shutil  # Import shutil for file operations
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Replace these with your actual Telegram credentials
API_ID = "22859056"
API_HASH = "806af07e96ee652a999dc795a4949708"
BOT_TOKEN = "7699377705:AAEPx4MLn90HtJCnMTOKP07UFzDXlf7TkUM"

# Initialize Pyrogram Client
bot = Client("FileRenamerBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Progress bar function
async def progress_bar(current, total, message, text):
    progress = int(25 * current / total)  # Number of '▰' blocks
    bar = f"{'▰' * progress}{'▱' * (25 - progress)}"  # Single-line progress bar (straight)
    percentage = f"{current * 100 / total:.2f} %"

    downloaded_mb = current / (1024 * 1024)  # Convert bytes to MB
    total_mb = total / (1024 * 1024)  # Convert bytes to MB
    speed = downloaded_mb / (time.time() - progress_bar.start_time)  # KB/s
    remaining_time = (total - current) / (speed * 1024) if speed > 0 else 0  # Seconds

    await message.edit(
        f"📥 **{text}**\n\n"
        f"📁 **File Name:** {progress_bar.file_name}\n\n"
        f"{bar} **{percentage}**\n\n"
        f"🚝 **Downloaded:** {downloaded_mb:.2f} MB / {total_mb:.2f} MB\n\n"
        f"⚡️ **Speed:** {speed * 1024:.2f} KB/s\n\n"
        f"🕑 **Time Elapsed:** {time.time() - progress_bar.start_time:.2f} seconds\n\n"
        f"⏳ **Time Remaining:** {remaining_time:.2f} seconds\n\n"
        "📮 @YourChannelName"
    )

# Start command
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "**👋 Welcome to the File Renamer Bot!**\n\n"
        "🔹 Upload any file, and I will rename it for you.\n"
        "🔹 Files up to **4GB** are supported.\n\n"
        "🚀 Let's get started!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Bot Info", callback_data="info")],
            [InlineKeyboardButton("📨 Support", url="https://t.me/YourSupportChannel")]
        ])
    )

# Info callback
@bot.on_callback_query(filters.regex("info"))
async def info_callback(client, callback_query):
    await callback_query.message.edit(
        "**🤖 Bot Info**\n\n"
        "This bot can rename files up to **4GB** quickly using Telegram's servers.\n\n"
        "Developed with ❤️ by [Your Name or Team].",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="back")]
        ])
    )

# Back button callback
@bot.on_callback_query(filters.regex("back"))
async def back_callback(client, callback_query):
    await start(client, callback_query.message)

# File handler
@bot.on_message(filters.document | filters.video | filters.audio)
async def handle_file(client, message):
    file = message.document or message.video or message.audio
    file_size = file.file_size / (1024 ** 3)  # File size in GB

    # Check file size (Telegram's limit is 4GB)
    if file_size > 4:
        await message.reply("⚠️ The file size exceeds 4GB. I cannot process this file.")
        return

    progress_bar.start_time = time.time()  # Initialize start time for progress
    progress_bar.file_name = file.file_name  # Set the file name
    await message.reply(
        f"**File Received:** `{file.file_name}`\n"
        f"**Size:** {file_size:.2f} GB\n\n"
        "💬 **Please send the new name for this file (including extension):**"
    )

    @bot.on_message(filters.reply & filters.text & filters.user(message.from_user.id))
    async def rename_file(client, reply_message):
        new_name = reply_message.text

        # Inform the user
        status_message = await message.reply("📥 **Downloading file...**")

        # Download the file
        downloaded_path = await client.download_media(message, progress=progress_bar, progress_args=(status_message, "Downloading File"))

        renamed_path = f"./downloads/{new_name}"

        # Move the file instead of renaming (to avoid cross-device link error)
        shutil.move(downloaded_path, renamed_path)

        # Upload the renamed file
        await status_message.edit("📤 **Uploading renamed file...**")
        await client.send_document(
            message.chat.id,
            renamed_path,
            caption=f"**Renamed File:** `{new_name}`",
            progress=progress_bar,
            progress_args=(status_message, "Uploading File to Telegram")
        )

        # Cleanup
        os.remove(renamed_path)
        await status_message.delete()

# Run the bot
if __name__ == "__main__":
    bot.run()