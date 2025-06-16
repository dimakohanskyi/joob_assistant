from aiogram.types import CallbackQuery, Message
from src.keyboards.profile_keyboard import get_profile_keyboard
from src.ai_analyse.job_item_analyse import analyse_job_url
from aiogram.fsm.context import FSMContext
from src.states.job_states.job_analyse_state import JobAnalyseState
from src.settings.logging_config import configure_logging
import logging
from src.utils.valid_url_checker import is_valid_url
from src.databese.settings import get_db
from sqlalchemy import select



configure_logging()
logger = logging.getLogger(__name__)



async def job_analyse_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JobAnalyseState.waiting_for_url)
    await state.update_data(last_bot_message=callback.message.message_id)
    await callback.message.edit_caption(
        caption="Please enter the job posting URL you want to analyze.\n\n"
        "Example:\n"
        "https://www.linkedin.com/jobs/view/123456789",
        reply_markup=get_profile_keyboard()
    )



async def process_job_url(message: Message, state: FSMContext):
    url = message.text.strip()
    # Delete user's message with URL
    await message.delete()
    
    state_data = await state.get_data()
    last_bot_message_id = state_data.get('last_bot_message')
    
    if not is_valid_url(url):
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="❌ Invalid URL format. Please enter a valid URL.",
            reply_markup=get_profile_keyboard()
        )
        return

    # Update the bot's message to show processing
    await message.bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=last_bot_message_id,
        caption="🔄 Analyzing job posting... Please wait.",
        reply_markup=get_profile_keyboard()
    )
    
    analysis_result = await analyse_job_url(url)
    if not analysis_result:
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="❌ Sorry, I couldn't analyze this job posting. Please make sure the URL is correct and try again.",
            reply_markup=get_profile_keyboard()
        )
        return

    await message.bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=last_bot_message_id,
        caption=f"✅ Job Analysis Results:\n\n{analysis_result}",
        reply_markup=get_profile_keyboard()
    )
    await state.clear()

