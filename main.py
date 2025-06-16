import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from src.routes.routes import router
from src.settings.logging_config import configure_logging


configure_logging()
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

dp = Dispatcher()
dp.include_router(router)


async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())