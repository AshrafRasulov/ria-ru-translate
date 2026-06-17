import conf.config as config

def is_trusted_source(event):
    """
    Проверяет, пришло ли сообщение из доверенного источника.
    Игнорирует спам и заблокированные каналы.
    """
    # 1. Проверяем, является ли сообщение сообщением из канала
    if not event.is_channel:
        return False
    
    chat = event.chat
    if not chat:
        return False
        
    # 2. Получаем идентификатор (username или ID)
    source = chat.username if hasattr(chat, 'username') and chat.username else str(chat.id)
    
    # 3. Блокировка: если канал в черном списке
    if source in getattr(config, 'SOURCE_CHANNELS_BAN', []):
        return False
        
    # 4. Белый список: разрешаем ТОЛЬКО те, что в SOURCE_CHANNELS
    return source in config.SOURCE_CHANNELS