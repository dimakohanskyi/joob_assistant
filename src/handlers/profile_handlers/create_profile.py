from aiogram.types import CallbackQuery
import logging
from src.settings.logging_config import configure_logging
from src.keyboards.profile_keyboard import get_create_profile_keyboard



configure_logging()
logger = logging.getLogger(__name__)





async def create_account(callback: CallbackQuery):
    try:
        await callback.message.edit_caption(
            caption="👤 Let's create your profile! Please fill in your details:",
            reply_markup=get_create_profile_keyboard()
        )
            
    except Exception as ex:
        logger.error(f"Error in create_account: {str(ex)}")
        await callback.message.edit_text(
            "❌ Sorry, something went wrong. Please try again later.",
            reply_markup=get_create_profile_keyboard()
        )
    