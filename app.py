import os, time, logging, requests
from dotenv import load_dotenv
from random import choice
from telegram import Update
from telegram.ext import (ApplicationBuilder, MessageHandler,
                            filters, ContextTypes
)

load_dotenv()
logging.basicConfig(level=logging.INFO)

TG_TOKEN = os.environ["TELEGRAM_TOKEN"]
AAI_KEY = os.environ["ASSEMBLY_AI_KEY"]
AAI_HEADERS = {"authorization": AAI_KEY}
AAI_BASE = "https://api.assemblyai.com"
VOICE_NAMINGS = ["🎙 Аудиопослание", "🎙 Пальцы не работают",
    "🎙 Обращение к нации", "🎙 Лапша на уши", "🎙 Репортаж с места событий",
    "🎙 Экстренное включение"
]
VIDEO_NAMINGS = ["🎥 Видеопослание", "🎥 Ебальничек",
    "🎥 Печатать — не царское дело", "🎥 Живое выступление",
    "🎥 Экстренное включение", "🎥 Прямой эфир", "🎥 Репортаж с места событий",
    "🎥 Короткометражка"
]


def upload_and_transcribe(audio_bytes: bytes) -> str:
    url = requests.post(f"{AAI_BASE}/v2/upload", 
                        headers=AAI_HEADERS, data=audio_bytes
    )
    url.raise_for_status()
    audio_url = url.json()["upload_url"]
    
    job = requests.post(f"{AAI_BASE}/v2/transcript", headers=AAI_HEADERS, json={
        "audio_url": audio_url,
        "language_detection": True,
        "speech_models": ["universal-2"],
    })
    job.raise_for_status()
    poll = f"{AAI_BASE}/v2/transcript/{job.json()['id']}"
    
    while True:
        r = requests.get(poll, headers=AAI_HEADERS).json()
        if r["status"] == "completed":
            return r["text"] or "Сорри, во рту член застрял, не могу говорить"
        elif r["status"] == "error":
            raise RuntimeError(r["error"])
        time.sleep(3)


async def on_added_to_chat(update: Update) -> None:
    await update.effective_message.reply_text(
        "Я тут! Как хорошо, что Бог русский!"
    )


async def on_voice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    file_obj = msg.voice or msg.audio or msg.video_note
    
    if not file_obj:
        return
    
    sender = update.message.from_user.full_name
    sender = sender if sender else "Хз кто"
    tg_file = await ctx.bot.get_file(file_obj.file_id)
    audio = await tg_file.download_as_bytearray()
    
    if update.message.voice:
        reply_starters = VOICE_NAMINGS
    else:
        reply_starters = VIDEO_NAMINGS
    
    try:
        text = upload_and_transcribe(bytes(audio))
        reply = f"{choice(reply_starters)} от {sender}:\n\n{text}"
        await update.message.reply_text(reply)
    except Exception as e:
        logging.exception("transcription error")
        await update.message.reply_text(f"❌ Произошла ошибочка: {e}")


app = ApplicationBuilder().token(TG_TOKEN).build()
app.add_handler(MessageHandler(
    filters.VOICE | filters.AUDIO | filters.VIDEO_NOTE, on_voice
    )
)
app.add_handler(MessageHandler(
    filters.StatusUpdate.NEW_CHAT_MEMBERS, on_added_to_chat,
    )
)
app.run_polling()