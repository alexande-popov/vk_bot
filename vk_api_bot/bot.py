import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import datetime
import signal
import sys

from vk_api_bot.config import GROUP_TOKEN, GROUP_ID, ADMIN_ID


class VkBot:
    """Бот для ВКонтакте, использующий Long Poll API.

    Long Poll — один из двух основных способов получения событий
    от VK (альтернатива Callback API). В отличие от Callback API,
    где сервер VK отправляет события на ваш URL, Long Poll — это
    клиентский подход: бот сам запрашивает у сервера события
    и получает их, когда они появляются. Это удобно для простых
    ботов без собственного сервера.

    Аргументы:
        GROUP_TOKEN: Токен группы, полученный в настройках VK.
        GROUP_ID: ID сообщества (число).
        ADMIN_ID: ID администратора для уведомлений.

    Пример использования::

        bot = VkBot()
        bot.run()

    Методы:
        send_message: Отправить сообщение пользователю.
        handle_message: Обработать входящее сообщение.
        run: Запустить цикл прослушки Long Poll.
    """

    def __init__(self):
        self.vk_session = vk_api.VkApi(token=GROUP_TOKEN)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id=GROUP_ID)
        self.admin_id = ADMIN_ID

        signal.signal(signal.SIGINT, self._on_shutdown)

    def send_message(self, user_id: int, message: str) -> None:
        """Отправить сообщение пользователю."""
        self.vk.messages.send(
            user_id=user_id,
            message=message,
            random_id=random.getrandbits(32),
        )

    def handle_message(self, event) -> None:
        """Обработать входящее сообщение."""
        if not event.from_user:
            return

        user_id = event.object.message["from_id"]
        user_text = event.object.message["text"]
        print(f"Получено сообщение: <{user_text}> от {user_id}")

        answer = f"Я бот. Я получил твое сообщение: <{user_text}>"
        self.send_message(user_id, answer)

    def _on_shutdown(self, sig, frame) -> None:
        """Вежливое завершение работы."""
        print("\n🛑 Бот остановлен.")
        try:
            self.send_message(
                self.admin_id,
                f"🤖 Бот остановлен в {datetime.datetime.now().strftime('%d-%b-%Y %H:%M:%S')}",
            )
        except Exception as e:
            print(f"Не удалось отправить уведомление: {e}")
        sys.exit(0)

    def run(self) -> None:
        """Запустить цикл прослушки Long Poll."""
        print("✅ Бот запущен. Нажмите Ctrl+C для остановки.")

        try:
            for event in self.longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
                    self.handle_message(event)
        except KeyboardInterrupt:
            print("\n⚠️ Бот остановлен вручную.")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            sys.exit(1)


def main():
    bot = VkBot()
    bot.run()


if __name__ == "__main__":
    main()
