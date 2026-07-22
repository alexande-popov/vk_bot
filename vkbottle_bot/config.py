"""Конфигурация бота.

Секреты (токен) читаются из .env через переменные окружения.
Публичные настройки (ID) тоже можно задать через .env,
но имеют значения по умолчанию.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ID сообщества (можно переопределить через переменную окружения)
GROUP_ID = int(os.getenv("VK_GROUP_ID", "240139679"))

# ID администратора (обязательно задать в .env)
ADMIN_ID = int(os.getenv("VK_ADMIN_ID"))

# Секретные настройки (никогда не коммитить!)
GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")
if not GROUP_TOKEN:
    raise RuntimeError("Не задан VK_GROUP_TOKEN. Создайте файл .env")
