# --- Конфигурационный файл для бота ---

# API ID и HASH - ключи вашего приложения с сайта my.telegram.org
API_ID = 38983025
API_HASH = '4903b962cac1058c0663f14c57509e60'

# Имя сессии (создается автоматически, не меняйте без нужды)
SESSION_NAME = 'my_session'

# Каналы: ID или юзернейм канала, из которого копируем
SOURCE_CHANNELS = [
    'rian_ru',
    'vremya_novosti',
    'okaytrend',
    'kommentarii_medved',
    'IT_Portal',
    'nadivaneworkbot',
    'RVvoenkor'
    ]
TARGET_CHANNEL = 'riantestru' # ID или юзернейм вашего канала, куда отправляем

# Настройки перевода:
# Язык, на который нужно переводить (например, 'uz' - узбекский, 'en' - английский)
# Настройка языков (добавьте сюда любые новые языки)
LANGUAGES = {
    'uz': '🇺🇿 Uzbek',
    'en': '🇬🇧 English',
    'ru': '🇷🇺 Russian',
    'kk': '🇰🇿 Kazakh',
    'ky': '🇰🇬 Kyrgyz',
    'tg': '🇹🇯 Tajik',
    'az': '🇦🇿 Azerbaijani',
    'tr': '🇹🇷 Turkish',
    'uk': '🇺🇦 Ukrainian',
    'de': '🇩🇪 German'
}

# --- НАСТРОЙКИ ДЛЯ ОБЛАЧНОГО СЕРВЕРА (RENDER.COM / VPS) ---
# Раскомментируйте эти строки при запуске на постоянной основе (через 3 месяца или при переходе на платный тариф)
# PROXY_URL = 'http://your-proxy-server:port'
# LOG_LEVEL = 'INFO'
# AUTO_RESTART = True 
# --------------------------------------------------------

# Настройки сервера (для будущего переноса):
# Если вы перенесете скрипт на VPS, эти параметры останутся прежними,
# так как они относятся к API Telegram, а не к расположению сервера.