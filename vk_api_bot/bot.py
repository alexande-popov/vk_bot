import random
import datetime
import signal
import sys
import json
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from vk_api_bot.config import GROUP_TOKEN, GROUP_ID, ADMIN_ID


class Cmd:
    """Константы команд"""
    GREETING_RU = "greeting_ru"
    GREETING_EN = "greeting_en"
    GREETING_ES = "greeting_es"
    
    START = "/start"

class VkClient:
    """API клиент, сессия для ВКонтакте, использующая Long Poll API.

    Long Poll — один из двух основных способов получения событий
    от VK (альтернатива Callback API). В отличие от Callback API,
    где сервер VK отправляет события на ваш URL, Long Poll — это
    клиентский подход: бот сам запрашивает у сервера события
    и получает их, когда они появляются. Это удобно для простых
    ботов без собственного сервера.

    Аргументы:
        token: Токен группы, полученный в настройках VK.
        group_id: ID сообщества (число).

    Методы:
        send_message: Отправить сообщение пользователю через API.
    """
    def __init__(self, token, group_id):
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id=group_id)

    def send_message(self, user_id, text, keyboard=None):
        try:
            self.vk.messages.send(
                user_id=user_id,
                message=text,
                random_id=random.getrandbits(32),
                keyboard=keyboard
            )
        except vk_api.exceptions.ApiError as e:
            if e.code == 901:  # пользователь запретил сообщения
                print(f"User {user_id} blocked bot")
            else:
                raise


class KeyboardBuilder:
    """Фабрика клавиатур."""
    @staticmethod
    def main_menu():
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(
            'Привет! 👋',
            color=VkKeyboardColor.POSITIVE,
            payload=json.dumps({"cmd": Cmd.GREETING_RU})
        )
        keyboard.add_line()
        keyboard.add_button(
            'Hello! 🌍',
            color=VkKeyboardColor.PRIMARY,
            payload=json.dumps({"cmd": Cmd.GREETING_EN})
        )
        keyboard.add_button(
            'Hola! 🌎',
            color=VkKeyboardColor.NEGATIVE,
            payload=json.dumps({"cmd": Cmd.GREETING_ES})
        )
        return keyboard.get_keyboard()


class CommandHandler:
    """Регистрация и обработка команд."""
    def __init__(self):
        self.commands = {}           # текстовые команды (например, /start)
        self.payload_commands = {}   # команды по payload

    def register(self, command: str, func):
        self.commands[command] = func

    def register_payload(self, cmd: str, func):
        self.payload_commands[cmd] = func

    def handle(self, user_id: int, text: str = None, payload: dict = None):
        """Обработать команду (по тексту или payload). Возвращает True, если команда найдена."""
        if payload and "cmd" in payload:
            cmd = payload["cmd"]
            if cmd in self.payload_commands:
                self.payload_commands[cmd](user_id)
                return True
        if text and text in self.commands:
            self.commands[text](user_id)
            return True
        return False
    

class VkBot:
    """Бот для ВКонтакте.

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
        self.admin_id = ADMIN_ID
        self.vk_client = VkClient(GROUP_TOKEN, GROUP_ID)
        self.command_handler = CommandHandler()

        self._register_handlers()

    def _register_handlers(self):
        """Зарегистрировать все команды и их обработчики."""
        self.command_handler.register(Cmd.START, self._send_main_menu)

        self.command_handler.register_payload(Cmd.GREETING_RU, self._greeting_ru)
        self.command_handler.register_payload(Cmd.GREETING_EN, self._greeting_en)
        self.command_handler.register_payload(Cmd.GREETING_ES, self._greeting_es)

        signal.signal(signal.SIGINT, self._on_shutdown)

    def send_message(self, user_id, text, keyboard=None):
        """Обертка для vk_client.send_message"""
        self.vk_client.send_message(user_id, text, keyboard)
    
    def _send_main_menu(self, user_id):
        """Отправить главное меню (клавиатуру)."""
        keyboard = KeyboardBuilder.main_menu()
        self.send_message(user_id, '👋 Приветствие!', keyboard)

    def _greeting_ru(self, user_id):
        self.send_message(user_id, 'И тебе привет! 😊')

    def _greeting_en(self, user_id):
        self.send_message(user_id, 'Hello to you too! 🌟')

    def _greeting_es(self, user_id):
        self.send_message(user_id, '¡Hola a ti también! 🌟')

    def _notify_admin(self, message):
        text = f"{datetime.datetime.now().strftime('%d-%b-%Y %H:%M:%S')}> {message}"
        try:
            self.send_message(self.admin_id, text)
        except Exception as e:
            print(f"Не удалось отправить уведомление: {e}")

    def _on_shutdown(self, sig, frame) -> None:
        """Вежливое завершение работы."""
        print("\n🛑 Бот остановлен.")
        self._notify_admin("🤖 🛑 Бот остановлен.")
        sys.exit(0)


    def handle_message(self, event) -> None:
        """Обработать входящее сообщение."""
        if not event.from_user:
            return

        user_id = event.object.message["from_id"]
        user_text = event.object.message.get("text", "")
        payload_raw = event.object.message.get("payload")

        payload = None
        if payload_raw:
            try:
                payload = json.loads(payload_raw)
            except json.JSONDecodeError:
                payload = None

        print(f"Получено сообщение: <{user_text}> от {user_id} (payload={payload})")

        # Пытаемся обработать команду
        if self.command_handler.handle(user_id, text=user_text, payload=payload):
            return

        # Стандартный ответ, если команда не распознана
        answer = f"Я бот. Я получил твое сообщение: <{user_text}>"
        self.send_message(user_id, answer)

    def run(self) -> None:
        """Запустить цикл прослушки Long Poll."""
        print("✅ Бот запущен. Нажмите Ctrl+C для остановки.")
        self._notify_admin("🤖 ✅ Бот запущен.")

        try:
            for event in self.vk_client.longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
                    self.handle_message(event)
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            sys.exit(1)


def main():
    bot = VkBot()
    bot.run()


if __name__ == "__main__":
    main()
