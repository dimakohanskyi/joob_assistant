import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from settings.logging_config import configure_logging
from handlers.start_handler import start_handler
from handlers.user_profile_handler import profile_handler
from handlers.create_profile import create_account
from handlers.menu_handler import main_menu_handler
from settings.logging_config import configure_logging


configure_logging()
logger = logging.getLogger(__name__)



router = Router()
router.message.register(start_handler, CommandStart())



@router.callback_query()
async def handle_callback(callback_query: CallbackQuery):
    command = callback_query.data

    try:
        if command == "profile":
            await profile_handler(callback_query)
        elif command == "create_profile":
            await create_account(callback_query)
        elif command == "main_menu":
            await main_menu_handler(callback_query)

    except Exception as ex:
        logger.error(f"Error executing command - {command}")
        print(ex)
