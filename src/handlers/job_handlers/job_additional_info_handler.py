from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging

from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.job_keyboard import get_job_metadata_keyboard
from src.keyboards.profile_keyboard import get_create_profile_keyboard
from src.databese.models import Jobb
from src.states.job_states.job_item_url_state import JobUrlState



configure_logging()
logger = logging.getLogger(__name__)





async def job_additional_info_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    job_id = data.get('current_job_id')
    
    if not job_id:
        await callback.message.edit_caption(
            caption="❌ No job selected. Please add a job URL first.",
            reply_markup=get_create_profile_keyboard()
        )
        return

    # Store the message ID for later use
    await state.update_data(last_bot_message=callback.message.message_id)
    
    await state.set_state(JobUrlState.waiting_for_additional_info)
    await callback.message.edit_caption(
        caption=(
            "Please enter additional information about the job posting.\n"
            "You can include:\n"
            "• Salary expectations\n"
            "• Company details\n"
            "• Application notes\n"
            "• Any other relevant information\n\n"
            "Or click 'Back' to return to job options"
        ),
        reply_markup=get_job_metadata_keyboard()
    )


async def process_additional_info(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        job_id = data.get('current_job_id')
        last_bot_message_id = data.get('last_bot_message')
        
        if not job_id:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ No job selected. Please add a job URL first.",
                reply_markup=get_create_profile_keyboard()
            )
            return

        additional_info = message.text.strip()
        
        async for session in get_db():
            job = await session.get(Jobb, job_id)
            if not job:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Job not found.",
                    reply_markup=get_create_profile_keyboard()
                )
                return
            
            job.additional_info = additional_info
            await session.commit()
            
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="✅ Additional information saved successfully!",
                reply_markup=get_job_metadata_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error in process_additional_info: {str(e)}")
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="❌ An error occurred while saving additional information. Please try again.",
            reply_markup=get_job_metadata_keyboard()
        )