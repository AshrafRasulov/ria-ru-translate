from telethon import TelegramClient, events, types  # Импортируем модули Telethon
import conf.config as config                        # Импортируем конфигурацию
from utils import security, utils, msgs             # Импортируем утилиты для безопасности, общих функций и логирования
import os
import json


# Инициализация сессии
session_dir = "session/user_sessionForeachUsers"
os.makedirs(session_dir, exist_ok=True)
client = TelegramClient(os.path.join(session_dir, config.SESSION_NAME), config.API_ID, config.API_HASH)


# --- ФУНКЦИЯ РАССЫЛКИ ПОДПИСЧИКАМ ---
async def broadcast_to_users(event_message, media_list=None):
    all_users = utils.get_all_users()
    
    for user in all_users:
        user_id = int(user.get('telegram_id'))
        if user_id <= 0: continue
            
        lang = user.get('lang', 'en')
        menu_enabled = user.get("menu_enabled", True)
        
        translated_text = await utils.translate_text(event_message.text or "", lang)
        btns = utils.get_reply_menu(menu_enabled) if menu_enabled else None
        
        try:
            # Получаем сущность пользователя для стабильной отправки
            user_entity = await client.get_input_entity(user_id)
            
            if media_list and len(media_list) > 0:
                await client.send_file(user_entity, media_list, caption=translated_text, buttons=btns)
            else:
                await client.send_message(user_entity, translated_text, buttons=btns)
        except Exception as e:
            msgs.log_info(f"Ошибка при рассылке пользователю {user_id}: {e}")

# --- ОБРАБОТЧИК КАНАЛОВ ---
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if event.raw_text and event.raw_text.startswith('/'):
        return

    if not security.is_trusted_source(event):
        return

    if event.message.text or event.message.media:
        # 1. Обработка медиа
        media_list = []
        if event.grouped_id:
            messages = await client.get_messages(event.chat_id, ids=event.grouped_id)
            media_list = [msg.media for msg in messages]
        elif event.media:
            media_list = [event.media]
            
        # 2. Сохранение новости
        await utils.save_news_data(event.chat.username, event.message, media_list, client)
        msgs.log_info(f"Новость из {event.chat.username} сохранена.")

        # 3. Рассылка
        await broadcast_to_users(event.message, media_list)
        msgs.log_info("Новость обработана и разослана.")

# --- ОБРАБОТЧИК START ---
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id
    if user_id > 0:
        utils.update_user_data(user_id, "User", lang='en', menu_enabled=True)
        await event.respond("👋 Привет! Выберите язык:", buttons=utils.get_reply_menu(True))

# --- ОБРАБОТЧИК КОМАНД АДМИНА ---
@client.on(events.NewMessage(pattern='/delete'))
async def delete_handler(event):
    args = event.raw_text.split()
    if len(args) == 3:
        result = utils.delete_news(args[1], args[2])
        await event.reply(result)

# --- ОБРАБОТЧИК КНОПОК МЕНЮ (Reply) ---
@client.on(events.NewMessage(func=lambda e: e.raw_text and e.raw_text.startswith("Язык:")))
async def menu_handler(event):
    lang_name = event.raw_text.replace("Язык: ", "").strip()
    selected_code = next((code for code, name in config.LANGUAGES.items() if name == lang_name), None)
    
    if selected_code:
        utils.update_user_data(event.sender_id, "User", lang=selected_code, menu_enabled=True)
        await event.respond(f"✅ Язык установлен: {lang_name}", buttons=utils.get_reply_menu(True))

@client.on(events.NewMessage(func=lambda e: e.raw_text == "❌ Больше не показывать"))
async def hide_menu_handler(event):
    utils.update_user_data(event.sender_id, "User", menu_enabled=False)
    from telethon.tl.types import ReplyKeyboardRemove
    await event.respond("Меню скрыто. Чтобы вернуть, напишите /start", buttons=ReplyKeyboardRemove())

# --- ОБРАБОТЧИК CALLBACK (если используете Inline) ---
@client.on(events.CallbackQuery())
async def callback(event):
    data = event.data.decode()
    if data.startswith('lang:'):
        lang_code = data.split(':')[1]
        utils.update_user_data(event.sender_id, "User", lang=lang_code)
        await event.answer(f"Язык изменен на {lang_code}")
    elif data == "hide_menu":
        utils.update_user_data(event.sender_id, "User", menu_enabled=False)
        await event.edit("✅ Меню скрыто.")

client.start()
client.run_until_disconnected()