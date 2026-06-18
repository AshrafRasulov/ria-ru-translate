import os, json, datetime, shutil
from deep_translator import GoogleTranslator
from telethon import Button
import conf.config as config
from utils import msgs
from telethon.tl.types import ReplyKeyboardMarkup, KeyboardButton

# 1. Функция перевода (которую искал main.py)
async def translate_text(text, target_lang):
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except:
        return text

# 2. Функция обновления данных пользователя
def update_user_data(user_id, name, lang=None, menu_enabled=None):
    # Ищем пользователя, чтобы сохранить его текущую папку
    # 1. Определяем базовый язык, если пользователь новый
    # Если пользователь уже есть, он найдется по ID
    # ПРИНУДИТЕЛЬНО ИГНОРИРУЕМ КАНАЛЫ
    if int(user_id) < 0:
        return None

    user_data = {"telegram_id": user_id, "name": name, "lang": 'en', "menu_enabled": True}
    
    # 2. Ищем, где лежит файл пользователя (если он уже был)
    found_path = None
    for root, dirs, files in os.walk("conf/users"):
        if f"{user_id}.json" in files:
            found_path = os.path.join(root, f"{user_id}.json")
            with open(found_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            break
            
    # 3. Обновляем данные
    if lang: user_data['lang'] = lang
    if menu_enabled is not None: user_data['menu_enabled'] = menu_enabled
    
    # 4. Сохраняем (всегда в папку языка)
    target_lang = user_data['lang']
    lang_dir = f"conf/users/{target_lang}"
    os.makedirs(lang_dir, exist_ok=True)
    
    file_path = f"{lang_dir}/{user_id}.json"
    
    # Удаляем старый файл, если сменился язык
    if found_path and found_path != file_path:
        os.remove(found_path)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=4)
        
    return user_data

# 3. Функция получения списка всех пользователей с их настройками
# Возвращает список словарей, чтобы main.py мог ими управлять
def get_all_users():
    users = []
    users_root = "conf/users"
    if not os.path.exists(users_root):
        return users
    
    for lang_code in os.listdir(users_root):
        lang_dir = os.path.join(users_root, lang_code)
        if not os.path.isdir(lang_dir): continue
        for filename in os.listdir(lang_dir):
            if filename.endswith(".json"):
                with open(os.path.join(lang_dir, filename), 'r', encoding='utf-8') as f:
                    try:
                        user = json.load(f)
                        users.append(user)
                    except json.JSONDecodeError:
                        msgs.log_info(f"Ошибка чтения JSON файла: {filename}")
    return users


# 4. Функция отправки медиа-группы
async def send_media_group(client, target, text, media, buttons):
    await client.send_message(target, text, file=media, buttons=buttons)

# 5. Функции для кнопок
def get_language_buttons():
    # print(f"DEBUG: Config Languages: {config.LANGUAGES}")
    """
    Создает кнопки выбора языка из config.LANGUAGES.
    Добавляет кнопку подтверждения для скрытия меню.
    """
    try:
        # Создаем список кнопок, где каждый внутренний список - это ряд кнопок
        rows = []
        # Добавляем кнопки языков из вашего конфига
        for code, label in config.LANGUAGES.items():
            rows.append([KeyboardButton(text=f"Язык: {label}")])
        
        # Добавляем кнопку "Больше не показывать"
        rows.append([KeyboardButton(text="Больше не показывать")])
        
        return ReplyKeyboardMarkup(rows=rows, resize=True, single_use=False)
    
    except Exception as e:
        msgs.log_info(f"Ошибка при создании кнопок: {e}")
        return None

# 6. Функция для админских кнопок
def get_admin_buttons():
    return [[Button.inline("📊 Статистика", data="stats")]]

# 7. Функция для проверки доверенных источников
async def save_news_data(channel_id, message, images, client): # Добавили client
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    data_dir = f"news-links/{today}"
    img_dir = f"{data_dir}/img"
    os.makedirs(img_dir, exist_ok=True)
    
    file_path = f"news-links/{today}-news-links.json"
    news_list = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            news_list = json.load(f)

    image_paths = []
    for i, media in enumerate(images):
        path = f"{img_dir}/{message.id}_{i}.jpg"
        await client.download_media(media, file=path) # Теперь бот реально качает файл
        image_paths.append(path)

    news_list.append({
        "id": message.id, "text": message.text, "images": image_paths, "source": channel_id
    })
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, indent=4, ensure_ascii=False)

# 8. Функция для получения кнопки источника
def get_source_button(channel_username):
    # Загружаем настройки кнопок
    with open("conf/news_config.json", 'r') as f:
        cfg = json.load(f)
    source = cfg.get(channel_username, {"name": "Источник", "url": "https://t.me"})
    return Button.url(source['name'], source['url'])

# 9. Функция удаления новости и связанных медиа
def delete_news(date, news_id):
    path = f"news-links/{date}-news-links.json"
    if not os.path.exists(path):
        return f"Файл {path} не найден."

    with open(path, 'r', encoding='utf-8') as f:
        news_list = json.load(f)

    # Ищем новость
    found_item = None
    for item in news_list:
        if str(item['id']) == str(news_id):
            found_item = item
            break
    
    if found_item:
        # Удаляем картинки с диска
        for img_path in found_item.get('images', []):
            if os.path.exists(img_path):
                os.remove(img_path)
        
        # Удаляем запись из списка
        news_list.remove(found_item)
        
        # Сохраняем обновленный файл
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, indent=4, ensure_ascii=False)
            
        return f"Новость {news_id} и связанные с ней медиа удалены."
    
    return "Новость не найдена в архиве."

# 10. Функция получения данных админа
def get_admin_data():
    with open("conf/admin.json", 'r', encoding='utf-8') as f:
        return json.load(f)

# 11. Функция получения ID админа    
def get_admin_id():
    """Загружает ID админа из файла conf/admin.json"""
    try:
        with open("conf/admin.json", 'r', encoding='utf-8') as f:
            admin_data = json.load(f)
            return int(admin_data.get('telegram_id'))
    except Exception as e:
        print(f"Ошибка чтения admin.json: {e}")
        return None

# 12. Функция получения кнопок основного меню
def get_reply_menu(menu_enabled=True):
    if not menu_enabled:
        return None # Если меню скрыто, возвращаем None
    
    rows = []
    for code, label in config.LANGUAGES.items():
        rows.append([KeyboardButton(text=f"Язык: {label}")])
    rows.append([KeyboardButton(text="❌ Больше не показывать")])
    return ReplyKeyboardMarkup(rows=rows, resize=True, single_use=False)