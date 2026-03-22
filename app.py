import logging
import os
import tempfile
from random import choice
from moviepy.editor import VideoFileClip
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from transformers import pipeline

from dotenv import load_dotenv
load_dotenv()
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

# список chat_id групп, где бот активен. Пусто = везде.
ALLOWED_CHATS: set[int] = set()
VOICE_NAMINGS = ["🎙 Аудиопослание", "🎙 Пальцы не работают",
    "🎙 Обращение к нации", "🎙 Лапша на уши", "🎙 Репортаж с места событий",
    "🎙 Экстренное включение"
]
VIDEO_NAMINGS = ["🎥 Видеопослание", "🎥 Ебальничек",
    "🎥 Печатать — не царское дело", "🎥 Живое выступление",
    "🎥 Экстренное включение", "🎥 Прямой эфир", "🎥 Репортаж с места событий",
    "🎥 Короткометражка"
]

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def on_added_to_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Я тут! Как хорошо, что Бог русский!"
    )


async def handle_voice_or_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat

    if ALLOWED_CHATS and chat.id not in ALLOWED_CHATS:
        return

    if message.voice:
        file_obj = message.voice
        label = choice(VOICE_NAMINGS)
        suffix = ".ogg"
    elif message.video_note:
        file_obj = message.video_note
        label = choice(VIDEO_NAMINGS)
        suffix = ".mp4"
        audio_suffix = ".mp3"
    else:
        return

    sender = message.from_user
    sender_name = sender.full_name if sender else "хз кто"

    tg_file = await context.bot.get_file(file_obj.file_id)

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = tmp.name

    try:
        await tg_file.download_to_drive(tmp_path)
        
        if suffix == ".mp4":
            with tempfile.NamedTemporaryFile(suffix=audio_suffix, delete=False) as audio_tmp:
                audio_path = audio_tmp.name
            video = VideoFileClip(tmp_path)
            video.audio.write_audiofile(audio_path)
            video.close()
        else:
            audio_path = tmp_path

        text = pipe(audio_path, return_timestamps=True)["text"].strip()

        if not text:
            text = "че там пизданул? я не понел :((("

        reply = f"{label} от <b>{sender_name}</b>:\n\n{text}"

        await message.reply_text(
            reply,
            parse_mode="HTML",
            reply_to_message_id=message.message_id,
        )

    except Exception as e:
        logger.exception("Ошибка при транскрипции")
        await message.reply_text(
            "⚠️ не могу понять настолько кучерявую речь",
            reply_to_message_id=message.message_id,
        )
    finally:
        os.unlink(tmp_path)
        if suffix == ".mp4" and audio_path != tmp_path:
            os.unlink(audio_path)


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            on_added_to_chat,
        )
    )
    
    app.add_handler(
        MessageHandler(
            filters.VOICE | filters.VIDEO_NOTE,
            handle_voice_or_video_note,
        )
    )
    
    logger.info("Бот запущен")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small"
    )
    
    main()