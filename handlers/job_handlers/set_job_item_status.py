from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from settings.logging_config import configure_logging
import logging
from utils.valid_url_checker import is_valid_url
from databese.settings import get_db
from databese.models import User, Jobb
from keyboards.job_keyboard import get_add_job_keyboard, get_job_status_keyboard




configure_logging()
logger = logging.getLogger(__name__)



async def set_job_item_status(callback: CallbackQuery):
    user_id = callback.from_user.id
    # async for session in get_db():
    #     user = User.get_user(user_id=user_id, session=session)
    #     if not user:
    #         await callback.message.answer("❌ User not found. Please create a profile first.")
    #         return
        
    #     existing_job = Jobb.get_jobb_items()

    await callback.message.edit_text(
        f"Your Telegram ID: {user_id}\n\n"
        "Please select the status for your job application:",
        reply_markup=get_job_status_keyboard()
    )