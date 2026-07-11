import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import datetime
import signal
import sys

# --- КОНФИГУРАЦИЯ ---
# Сюда вставьте ваш токен, полученный на шаге 3
GROUP_TOKEN = "vk1.a.1WlLiTeUCDYDjPUP6rtIgc6n8ClktEwOG566-k17XkBL4xmfiPVXMDPbUniMRy5UVK3BRAMZ9PxYQD8BLO6QNPM141qKs36eguPsabSYUbR6jUNRwEYN_GMz11v27jAu6A66NPMHJNKs1W16fjdd_b-B9giUnZo5ZQRFUI5tU5qs1nw8GwmVQRPb6zN4BtQ_UlcF4_kjZyL-5VML0F8iuA"
# ID вашей группы (число). Для club240139679 это 240139679
GROUP_ID = 240139679
ADMIN_ID = 690525


# --- ИНИЦИАЛИЗАЦИЯ ---
# Авторизуемся как сообщество
vk_session = vk_api.VkApi(token=GROUP_TOKEN)
# Получаем объект для работы с API
vk = vk_session.get_api()
# Создаем объект для работы с Long Poll
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

# --- ОБРАБОТЧИК ВЕЖЛИВОГО ЗАВЕРШЕНИЯ ---
def graceful_shutdown(sig, frame):
    print("\n🛑 Получен сигнал остановки. Бот завершает работу...")
    # Попытка отправить уведомление админу (не гарантирует доставку, если соединение уже рвется)
    try:
        vk.messages.send(
            user_id=ADMIN_ID,
            message=f"🤖 Бот остановлен в {datetime.datetime.now().strftime('%d-%b-%Y %H:%M:%S')}",
            random_id=random.getrandbits(32)
        )
    except Exception as e:
        print(f"Не удалось отправить уведомление: {e}")
    sys.exit(0)
    
# Регистрируем обработчик
signal.signal(signal.SIGINT, graceful_shutdown)

# --- ОСНОВНОЙ ЦИКЛ БОТА ---
print("✅ Бот запущен и ждет сообщений... (нажмите Ctrl+C для остановки)")

try:
    # Бесконечно слушаем сервер VK на наличие новых событий
    for event in longpoll.listen():

        # Проверяем, является ли событие новым сообщением
        if event.type == VkBotEventType.MESSAGE_NEW:
            # Проверяем, что сообщение пришло в личные сообщения бота
            # (а не в общий чат, где бот может быть упомянут)
            if event.from_user:
                # Получаем текст сообщения (можно использовать для логики)
                user_text = event.object.message['text']
                print(f"Получено сообщение: <{user_text}> от пользователя {event.object.message['from_id']}")

                answer = f"Я бот. Я получил твое сообщение: <{user_text}>"

                # Отправляем ответ
                vk.messages.send(
                    user_id=event.object.message['from_id'],  # Кому отправляем
                    message=answer,                           # Текст сообщения
                    random_id=random.getrandbits(32)          # Уникальный ID для избежания дублей
                )
except KeyboardInterrupt:
    # Если обработчик сигнала почему-то не сработал (например, из-за блокировки)
    print("\n⚠️ Бот остановлен вручную (KeyboardInterrupt).")
    sys.exit(0)
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    sys.exit(1)