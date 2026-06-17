from telethon import TelegramClient, events, types  # Импортируем модули Telethon
import conf.config as config                      # Импортируем конфигурационный файл
from utils import security, utils, msgs           # Импортируем модули безопасности, утилит и логирования
import os
import json

# Инициализация клиента Telethon
client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)

# --- ФУНКЦИЯ РАССЫЛКИ ПОДПИСЧИКАМ ---
async def broadcast_to_users(event_message):
    """Отправляет переведенную новость каждому пользователю на его языке."""
    users_dir = "conf/users"
    if not os.path.exists(users_dir):
        return

    # Подготовка данных источника
    chat = event_message.chat
    chat_username = chat.username if hasattr(chat, 'username') and chat.username else None
    post_link = f"https://t.me/{chat_username}/{event_message.id}" if chat_username else None

    for filename in os.listdir(users_dir):
        if filename.endswith(".json"):
            with open(os.path.join(users_dir, filename), 'r', encoding='utf-8') as f:
                user = json.load(f)
            
            # Переводим текст под конкретного пользователя
            translated_text = await utils.translate_text(event_message.text or "", user.get('lang', 'en'))
            
            # Формируем кнопки
            btns = []
            if post_link:
                btns.append([utils.Button.url("🔗 Читать оригинал", post_link)])
            if chat_username:
                btns.append([utils.Button.url("📢 Подписаться на источник", f"https://t.me/{chat_username}")])
            
            # Отправка пользователю
            try:
                await client.send_message(user['user_id'], translated_text, file=event_message.media, buttons=btns)
            except Exception as e:
                msgs.log_info(f"Не удалось отправить пользователю {user['user_id']}: {e}")

# --- ОБРАБОТЧИК НОВЫХ СООБЩЕНИЙ (КАНАЛЫ) ---
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # Если это команда (начинается с /), пропускаем этот обработчик, чтобы сработали команды
    if event.raw_text and event.raw_text.startswith('/'):
        return 

    # ПРОВЕРКА БЕЗОПАСНОСТИ: Если источник не в списке SOURCE_CHANNELS или в списке БАН - игнорируем
    if not security.is_trusted_source(event):
        return

    # Фильтр спама: если есть кнопки или это сообщение от бота - игнорируем
    if event.message.buttons or event.message.via_bot_id:
        return

    if event.message.text or event.message.media:
        msgs.log_event("NEWS", "Получена новая новость, начинаю рассылку...")
        
        # Рассылка всем пользователям из базы
        await broadcast_to_users(event.message)
        
        # Основная публикация в главный целевой канал
        chat = event.message.chat
        chat_username = chat.username if hasattr(chat, 'username') and chat.username else None
        post_link = f"https://t.me/{chat_username}/{event.message.id}" if chat_username else None
        
        btns = []
        if post_link:
            btns.append([utils.Button.url("🔗 Читать оригинал", post_link)])
        if chat_username:
            btns.append([utils.Button.url("📢 Подписаться на источник", f"https://t.me/{chat_username}")])

        translated_text = await utils.send_translated_news(client, event.message)
        await client.send_message(config.TARGET_CHANNEL, translated_text, file=event.message.media, buttons=btns)
        msgs.log_info("Рассылка завершена успешно.")

        # Уведомление Админа с защитой от ошибок Entity
        if config.ADMIN_ID:
            try:
                admin_entity = await client.get_input_entity(config.ADMIN_ID)
                await client.send_message(admin_entity, f"✅ Опубликована новость из {chat.title if hasattr(chat, 'title') else 'канала'}")
            except Exception as e:
                msgs.log_info(f"Ошибка уведомления админа: {e}")

# --- ОБРАБОТЧИК КОМАНДЫ /START ---
@client.on(events.NewMessage(pattern='/start', outgoing=False))
async def start_handler(event):
    sender = await event.get_sender()
    utils.update_user_data(event.sender_id, sender.first_name, 'en')
    msgs.log_event("NEW_CLIENT", f"Пользователь {sender.first_name}")
    await event.respond("Добро пожаловать! Выберите язык:", buttons=utils.get_language_buttons())

# --- ОБРАБОТЧИК КОМАНДЫ /ADMIN ---
@client.on(events.NewMessage(pattern='/admin', from_users=config.ADMIN_ID))
async def admin_handler(event):
    await event.respond("Админ-панель активна.", buttons=utils.get_admin_buttons())

# --- ОБРАБОТЧИК ВЫБОРА ЯЗЫКА ---
@client.on(events.CallbackQuery())
async def callback(event):
    data = event.data.decode('utf-8')
    if data.startswith('lang:'):
        lang_code = data.split(':')[1]
        sender = await event.get_sender()
        msg = utils.update_user_data(event.sender_id, sender.first_name, lang_code)
        await event.answer(msg, alert=True)
        await event.edit(msg)

print("Система запущена...")
client.start()
client.run_until_disconnected()