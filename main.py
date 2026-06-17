from telethon import TelegramClient, events
import conf.config as config
from utils import utils
import utils.msgs as msgs

client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)

@client.on(events.NewMessage(chats=config.SOURCE_CHANNELS))
async def handler(event):
    # Фильтр спама: если есть кнопки или это сообщение от бота - игнорируем
    if event.message.buttons or event.message.via_bot_id:
        return

    if event.message.text or event.message.media:
        msgs.log_event("NEWS", "Получена новая новость, начинаю рассылку...")
        translated_text = await utils.send_translated_news(client, event.message)
        
        # Публикуем в канал
        post_link = f"https://t.me/{event.message.chat.username}/{event.message.id}"
        await client.send_message(
            config.TARGET_CHANNEL, 
            translated_text, 
            file=event.message.media,
            buttons=[[utils.Button.url("📢 Источник", post_link)]]
        )
        msgs.log_info("Рассылка завершена успешно.")

@client.on(events.NewMessage(pattern='/start', outgoing=False))
async def start_handler(event):
    sender = await event.get_sender()
    # Установка языка по умолчанию 'en' для новых пользователей
    utils.update_user_data(event.sender_id, sender.first_name, 'en')
    msgs.log_event("NEW_CLIENT", f"Пользователь {sender.first_name}")
    await event.respond("Выберите язык:", buttons=utils.get_language_buttons())

@client.on(events.CallbackQuery(data=lambda d: d.startswith(b'lang:')))
async def callback(event):
    lang_code = event.data.decode('utf-8').split(':')[1]
    sender = await event.get_sender()
    msg = utils.update_user_data(event.sender_id, sender.first_name, lang_code)
    await event.answer(msg, alert=True)
    await event.edit(msg)

print("Система запущена...")
client.start()
client.run_until_disconnected()