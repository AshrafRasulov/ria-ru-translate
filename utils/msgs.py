from datetime import datetime

def get_time():
    """Возвращает текущее время в формате [HH:MM:SS]"""
    return datetime.now().strftime("%H:%M:%S")

def log_info(message):
    """Выводит информационное сообщение"""
    print(f"[{get_time()}] [INFO] {message}")

def log_event(event_type, details):
    """Выводит сообщение о событиях системы"""
    print(f"[{get_time()}] [EVENT] {event_type.upper()}: {details}")

def log_error(error_msg):
    """Выводит ошибку"""
    print(f"[{get_time()}] [ERROR] {error_msg}")