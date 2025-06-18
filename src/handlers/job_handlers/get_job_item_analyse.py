from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaDocument
from aiogram.fsm.context import FSMContext
import logging
import os

from src.keyboards.profile_keyboard import get_profile_keyboard
from src.ai_analyse.job_item_analyse import analyse_job_url
from src.states.job_states.job_analyse_state import JobAnalyseState
from src.settings.logging_config import configure_logging
from src.utils.valid_url_checker import is_valid_url
from src.utils.report_generator import pack_job_analyse_report
from src.rate_limit.ai_summaty_rate_limit import check_job_item_limit




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
    await message.delete()
    
    state_data = await state.get_data()
    last_bot_message_id = state_data.get('last_bot_message')

    can_process = await check_job_item_limit(message.from_user.id)
    if not can_process:
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="⏰ Rate limit exceeded. Please wait 60 seconds before requesting another job analysis.",
            reply_markup=get_profile_keyboard()
        )
        return

    
    if not is_valid_url(url):
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="❌ Invalid URL format. Please enter a valid URL.",
            reply_markup=get_profile_keyboard()
        )
        return

    await message.bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=last_bot_message_id,
        caption="🔄 Analyzing job posting... Please wait.",
        reply_markup=get_profile_keyboard()
    )
    
    try:
        analysis_result = await analyse_job_url(url)
        if not analysis_result:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Sorry, I couldn't analyze this job posting. Please make sure the URL is correct and try again.",
                reply_markup=get_profile_keyboard()
            )
            return

        file_path = pack_job_analyse_report(analysis_result)
        
        try:
            await message.bot.edit_message_media(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                media=InputMediaDocument(
                    media=FSInputFile(file_path),
                    caption="✅ Here's your job analysis report"
                ),
                reply_markup=get_profile_keyboard()
            )
        finally:
            try:
                os.remove(file_path)
                logger.info(f"Temporary file {file_path} has been deleted")
            except Exception as e:
                logger.error(f"Error deleting temporary file {file_path}: {str(e)}")
        
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="✅ Analysis complete! I've sent you the report as a file.",
            reply_markup=get_profile_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error processing job URL: {str(e)}")
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="❌ An error occurred while processing your request. Please try again.",
            reply_markup=get_profile_keyboard()
        )
    
    await state.clear()

