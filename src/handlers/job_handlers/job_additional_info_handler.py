from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.job_keyboard import get_job_metadata_keyboard
import logging
from src.databese.models import Jobb
from src.states.job_states.job_item_url_state import JobUrlState



configure_logging()
logger = logging.getLogger(__name__)





async def job_additional_info_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    job_id = data.get('current_job_id')
    
    if not job_id:
        await callback.message.answer("❌ No job selected. Please add a job URL first.")
        return
        
    # Set state to wait for additional info
    await state.set_state(JobUrlState.waiting_for_additional_info)
    
    await callback.message.answer(
        "Please enter additional information about the job posting.\n"
        "You can include:\n"
        "• Salary expectations\n"
        "• Company details\n"
        "• Application notes\n"
        "• Any other relevant information"
    )


async def process_additional_info(message: Message, state: FSMContext):
    try:
        # Get current job ID from state
        data = await state.get_data()
        job_id = data.get('current_job_id')
        
        if not job_id:
            await message.answer("❌ No job selected. Please add a job URL first.")
            return

        # Get the additional info text
        additional_info = message.text.strip()
        
        # Update additional_info in database
        async for session in get_db():
            job = await session.get(Jobb, job_id)
            if not job:
                await message.answer("❌ Job not found.")
                return
            
            job.additional_info = additional_info
            await session.commit()
            
            await message.answer(
                "✅ Additional information saved successfully!",
                reply_markup=get_job_metadata_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error in process_additional_info: {str(e)}")
        await message.answer(
            "❌ An error occurred while saving additional information. Please try again.",
            reply_markup=get_job_metadata_keyboard()
        )