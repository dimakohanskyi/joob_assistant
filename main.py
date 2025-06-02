import asyncio
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from routes.routes import router
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")



dp = Dispatcher()
dp.include_router(router)



async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())