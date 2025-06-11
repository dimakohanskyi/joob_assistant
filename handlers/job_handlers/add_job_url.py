from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from settings.logging_config import configure_logging
import logging
from utils.valid_url_checker import is_valid_url
from databese.settings import get_db
from databese.models import User, Jobb
from states.job_states.job_item_url_state import JobUrlState
from keyboards.job_keyboard import get_add_job_keyboard

configure_logging()
logger = logging.getLogger(__name__)



async def add_job_item_url(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JobUrlState.waiting_for_item_url)
    await callback.message.answer(
        "Please enter the job posting URL you want to add.\n\n"
        "Example:\n"
        "https://www.linkedin.com/jobs/view/123456789"
    )



async def process_job_item_url(message: Message, state: FSMContext):
    url = message.text.strip()
    
    if not is_valid_url(url):
        await message.answer("❌ Invalid URL format. Please enter a valid URL.")
        return
        

    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)

            if not user:
                await message.answer("❌ User not found. Please create a profile first.")
                return

            existing_job = await Jobb.get_jobb_items(user_id=user.id, session=session)
            
            if existing_job:
                await message.answer("ℹ️ This job URL is already in your list.", reply_markup=get_add_job_keyboard())
                await state.clear()
                return

            new_job = Jobb(
                user_id=user.id,
                url=url,
                priority='low'  
            )
            
            session.add(new_job)
            await session.commit()
            
            await message.answer(
                "✅ Job URL added successfully!\n\n"
                "You can now:\n"
                "• Set priority\n"
                "• Update status\n"
                "• Add additional info\n"
                "• Generate AI summary",
                reply_markup=get_add_job_keyboard()
            )

    except Exception as ex:
        logger.error(f"Error processing job URL: {str(ex)}")
        await message.answer("❌ An error occurred while processing the URL. Please try again.")
    
    finally:
        await state.clear()









