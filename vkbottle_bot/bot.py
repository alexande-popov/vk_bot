import asyncio
from vkbottle.bot import Bot, Message

# Импортируем ваши секреты из существующего config.py
from config import GROUP_TOKEN


# Создаём экземпляр бота с токеном группы
bot = Bot(token=GROUP_TOKEN)


# Обработчик на любое текстовое сообщение
@bot.on.message(text=["привет", "Привет", "Здравствуй", "хай", "hello"])
async def greeting_handler(message: Message):
    """Ответить приветствием на приветствие пользователя."""
    await message.answer("Привет! 😊 Как дела?")


# Можно добавить обработчик на команду /start
@bot.on.message(text="/start")
async def start_handler(message: Message):
    """Приветственное сообщение при старте."""
    await message.answer(
        "👋 Добро пожаловать! Я простой бот на vkbottle.\n"
        "Напиши 'привет', и я отвечу!"
    )


# Запуск бота
if __name__ == "__main__":
    bot.run()