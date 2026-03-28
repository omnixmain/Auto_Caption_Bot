import logging
import re
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

def get_metadata(filename):
    """Extract Season, Episode, Quality and Type from filename."""
    # Season & Episode: S01E01, S1 E1, etc.
    se_match = re.search(r'[S|s](\d+)\s?[E|e](\d+)', filename)
    season_episode = se_match.group(0).upper() if se_match else "N/A"
    
    # Quality: 480p, 720p, 1080p, 2160p, 4k
    q_match = re.search(r'(480p|720p|1080p|2160p|4k|HDR)', filename, re.IGNORECASE)
    quality = q_match.group(0).upper() if q_match else "N/A"
    
    # File Type: Extension
    parts = filename.split(".")
    file_type = parts[-1].upper() if len(parts) > 1 else "N/A"
    
    return season_episode, quality, file_type

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

        # 1. Extract Metadata
        file_name = getattr(media, 'file_name', 'Media File')
        # Clean name for display (remove underscores, dots, and quality tags for the title line)
        display_name = file_name.replace("_", " ").replace(".", " ")
        # Remove extension from display name
        if "." in file_name:
            display_name = " ".join(display_name.split(" ")[:-1])

        season_episode, quality, file_type = get_metadata(file_name)
        file_size = get_human_size(media.file_size) if hasattr(media, 'file_size') else "N/A"

        # 2. Construct the core caption as per user request
        # 📁 {file_name}
        # 🎬 {season_episode}
        # 📺 {quality} | 📦 {file_size} | 📂 {file_type}
        
        core_caption = (
            f"📁 **{display_name}**\n"
            f"🎬 **{season_episode}**\n"
            f"📺 **{quality}** | 📦 **{file_size}** | 📂 **{file_type}**\n"
            f"\n"
            f"⚡ **OMNIX EMPIRE** https://t.me/omnix_Empire"
        )

        # 3. Add custom caption text from config (if any)
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
        logger.info(f"Successfully updated caption for: {file_name}")
        
    except Exception as e:
        logger.error(f"Error editing caption: {e}")