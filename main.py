from telethon import TelegramClient, events
from googletrans import Translator
import config

client = TelegramClient('my_session', config.API_ID, config.API_HASH)
translator = Translator()

@client.on(events.NewMessage(chats=config.SOURCE_CHANNEL))
async def handler(event):
    text = event.message.text or ""
    
    # Перевод текста
    if text:
        translated = translator.translate(text, dest=config.TARGET_LANG)
        new_text = f"{translated.text}\n\n[Источник: РИА Новости](https://t.me/{config.SOURCE_CHANNEL}/{event.message.id})"
    else:
        new_text = f"[Пост из РИА Новости](https://t.me/{config.SOURCE_CHANNEL}/{event.message.id})"

    # Отправка
    await client.send_message(config.TARGET_CHANNEL, new_text, file=event.message.media)
    print(f"Новость обработана и отправлена в {config.TARGET_CHANNEL}")

print("Бот запущен и готов к работе...")
client.start()
client.run_until_disconnected()