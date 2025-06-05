import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from settings.logging_config import configure_logging
from handlers.start_handler import start_handler
from handlers.user_profile_handler import profile_handler





router = Router()
router.message.register(start_handler, CommandStart())



@router.callback_query()
async def handle_callback(callback_query: CallbackQuery):
    command = callback_query.data

    try:
        if command == "profile":
            await profile_handler(callback_query)
    except Exception as ex:
        # logger.error(f"Error executing command {command}: {str(ex)}", exc_info=True)
        print(ex)
