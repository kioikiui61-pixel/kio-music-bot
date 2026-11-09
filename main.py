import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, HighQualityAudio
from yt_dlp import YoutubeDL
from pymongo import MongoClient

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")
STRING_SESSION = os.getenv("STRING_SESSION", "")

mongo = MongoClient(MONGO_URI) if MONGO_URI else None
db = mongo["kio"] if mongo else None

app = Client("kio-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("kio-user", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION) if STRING_SESSION else None
call = PyTgCalls(user) if user else None

ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True, "extract_flat": "in_playlist"}
queues = {}

def search(query):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)
        v = info["entries"][0]
        return v["title"], v["webpage_url"], v["duration"]

@app.on_message(filters.command("start") & filters.private)
async def start(_, m: Message):
    await m.reply("اهلا بيك ببوت كيو للموسيقى 🎵\nضيفني لكروب وشغل اغنية بـ /play + اسم الاغنية")

@app.on_message(filters.command("play") & filters.group)
async def play(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("اكتب اسم الاغنية: /play عمرو دياب")
    query = " ".join(m.command[1:])
    await m.reply(f"جاري البحث عن: {query}...")
    try:
        title, url, dur = search(query)
        with YoutubeDL({"format": "bestaudio/best", "quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info["url"]
        await call.join_group_call(m.chat.id, AudioPiped(audio_url, HighQualityAudio()))
        await m.reply(f"🎵 يشغل الان:\n**{title}**")
    except Exception as e:
        await m.reply(f"صار خطأ: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop(_, m: Message):
    try:
        await call.leave_group_call(m.chat.id)
        await m.reply("تم ايقاف الاغنية ⏹️")
    except:
        await m.reply("ماكو شي يشتغل")

@app.on_message(filters.command("skip") & filters.group)
async def skip(_, m: Message):
    await m.reply("خاصية التخطي قريبا، استخدم /stop وبعدها /play")

async def main():
    await app.start()
    if call:
        await call.start()
    print("KIO BOT STARTED")
    await app.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
