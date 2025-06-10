from aiogram.types import CallbackQuery, Message
from keyboards.profile_keyboard import get_profile_keyboard
from ai_analyse.job_item_analyse import analyse_job_url
from aiogram.fsm.context import FSMContext
from states.job_states.job_analyse_state import JobAnalyseState
from settings.logging_config import configure_logging
import logging
from utils.valid_url_checker import is_valid_url



configure_logging()
logger = logging.getLogger(__name__)



async def job_analyse_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JobAnalyseState.waiting_for_url)
    await callback.message.answer(
        "Please enter the job posting URL you want to analyze.\n\n"
        "Example:\n"
        "https://www.linkedin.com/jobs/view/123456789"
    )




async def process_job_url(message: Message, state: FSMContext):
    url = message.text.strip()
    
    if not is_valid_url(url):
        await message.answer("❌ Invalid URL format. Please enter a valid URL.")
        return

    processing_message = await message.answer("🔄 Analyzing job posting... Please wait.")
    analysis_result = await analyse_job_url(url)
    if not analysis_result:
        await processing_message.edit_text("❌ Sorry, I couldn't analyze this job posting. Please make sure the URL is correct and try again.")
        return
    await processing_message.edit_text(f"✅ Job Analysis Results:\n\n{analysis_result}")
    await state.clear()

