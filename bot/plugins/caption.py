import logging
from pyrogram import filters
from bot.client import CaptionBot
from bot.config import Config

logger = logging.getLogger(__name__)
app = CaptionBot()

def get_human_size(bytes_size):
    """Convert bytes to a human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024

@app.on_message(
    filters.channel & 
    (filters.document | filters.video | filters.audio | filters.photo) & 
    ~filters.edited
)
async def auto_caption(client, message):
    try:
        media = message.document or message.video or message.audio or message.photo
        if not media:
            return

        # 1. Base information (Filename and Size)
        file_name = getattr(media, 'file_name', 'Media File')
        # Clean filename: replace "_" with " " and ensure it's readable
        clean_name = file_name.replace("_", " ").replace(".mp4", "").replace(".mkv", "")
        
        file_size = get_human_size(media.file_size) if hasattr(media, 'file_size') else "Unknown"

        # 2. Construct the core caption
        core_caption = (
            f"📂 **File:** `{clean_name}`\n"
            f"📦 **Size:** `{file_size}`"
        )

        # 3. Add custom caption text from config
        caption_text = Config.CAPTION_TEXT
        position = Config.CAPTION_POSITION
        
        if position == "top":
            final_caption = f"{caption_text}\n\n{core_caption}" if caption_text else core_caption
        elif position == "bottom":
            final_caption = f"{core_caption}\n\n{caption_text}" if caption_text else core_caption
        else:
            final_caption = caption_text or core_caption
        
        # 4. Apply editing
        await message.edit_caption(
            caption=final_caption,
            parse_mode="markdown"
        )
        logger.info(f"Successfully updated caption for: {clean_name}")
        
    except Exception as e:
        logger.error(f"Error editing caption: {e}")