import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
import yt_dlp

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
COOKIES_CONTENT = os.environ.get("YOUTUBE_COOKIES")
COOKIES_FILE = "/tmp/cookies.txt"
if COOKIES_CONTENT:
    with open(COOKIES_FILE, "w") as f:
        f.write(COOKIES_CONTENT)

DOWNLOAD_DIR = "/data/data/com.termux/files/home/telebot/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلين! ابعتلي رابط أي فيديو وبنزلّهولك 🎥")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("هاد مو رابط صحيح، ابعت رابط فيديو.")
        return

    msg = await update.message.reply_text("⏳ عم نزّل الفيديو...")

    try:
        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
            "format": "bv*+ba/best",
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }
        if COOKIES_CONTENT:
            ydl_opts["cookiefile"] = COOKIES_FILE

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            title = info.get("title", "video")

        filesize = os.path.getsize(filepath) / (1024 * 1024)

        if filesize > 50:
            await msg.edit_text(f"❌ الفيديو حجمه {filesize:.1f} ميجا، أكبر من حد تليغرام (50 ميجا). ما بقدر ابعتلك ياه.")
            os.remove(filepath)
            return

        await msg.edit_text(f"✅ تم التنزيل: {title}\nعم بعتلك الفيديو...")

        with open(filepath, "rb") as f:
            await update.message.reply_video(video=f, caption=title)

        os.remove(filepath)

    except Exception as e:
        await msg.edit_text(f"❌ صار خطأ: {str(e)}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("البوت شغال...")
app.run_polling()
