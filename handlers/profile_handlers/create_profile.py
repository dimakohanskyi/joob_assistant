from aiogram.types import CallbackQuery
from databese.models import User
from databese.settings import get_db
from settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from keyboards.profile_keyboard import get_profile_keyboard, get_create_profile_keyboard



configure_logging()
logger = logging.getLogger(__name__)





async def create_account(callback: CallbackQuery):
    try:
        await callback.message.answer(
            "👤 Let's create your profile! Please fill in your details:",
            reply_markup=get_create_profile_keyboard()
        )
            
    except Exception as ex:
        logger.error(f"Error in create_account: {str(ex)}")
        await callback.message.answer(
            "❌ Sorry, something went wrong. Please try again later.",
            reply_markup=get_create_profile_keyboard()
        )
    