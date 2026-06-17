import os
import json
import uuid
from telethon import Button
from deep_translator import GoogleTranslator
import conf.config as config

def update_user_data(user_id, name, lang_code):
    found_path = None
    for root, dirs, files in os.walk("conf/users"):
        for file in files:
            p = os.path.join(root, file)
            with open(p, 'r', encoding='utf-8') as f:
                d = json.load(f)
                if d.get("telegram_id") == user_id:
                    found_path = p
                    break
    
    if found_path:
        with open(found_path, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        os.remove(found_path)
    else:
        user_data = {"telegram_id": user_id, "name": name, "uuid": str(uuid.uuid4())}
    
    user_data["lang"] = lang_code
    lang_dir = f"conf/users/{lang_code}"
    os.makedirs(lang_dir, exist_ok=True)
    
    with open(f"{lang_dir}/{user_data['uuid']}.json", 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)
    return f"✅ Язык изменен на: {config.LANGUAGES.get(lang_code)}"

async def send_translated_news(client, message):
    text = message.text or ""
    # Удаляем упоминания каналов из текста
    for channel in config.SOURCE_CHANNELS:
        text = text.replace(channel, "")
    
    # Кнопка для перехода к источнику
    post_link = f"https://t.me/{message.chat.username}/{message.id}"
    buttons = [[Button.url("📢 Перейти к источнику", post_link)]]
    
    # Перевод для публикации в канал (на английский)
    main_translation = GoogleTranslator(source='auto', target='en').translate(text)

    # Рассылка пользователям
    for lang_code in os.listdir("conf/users"):
        lang_dir = f"conf/users/{lang_code}"
        if not os.path.isdir(lang_dir): continue
        
        translated_text = GoogleTranslator(source='auto', target=lang_code).translate(text)
        
        for user_file in os.listdir(lang_dir):
            with open(f"{lang_dir}/{user_file}", 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                try:
                    await client.send_message(
                        user_data['telegram_id'], 
                        f"{translated_text}\n\n➖➖➖➖➖", 
                        file=message.media, 
                        buttons=buttons
                    )
                except Exception as e:
                    print(f"Ошибка отправки: {e}")
    
    return main_translation

def get_language_buttons():
    return [[Button.inline(label, data=f"lang:{code}")] for code, label in config.LANGUAGES.items()]