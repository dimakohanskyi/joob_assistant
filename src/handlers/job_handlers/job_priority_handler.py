from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.job_keyboard import get_job_metadata_keyboard, get_priority_keyboard
import logging
from src.databese.models import Jobb


configure_logging()
logger = logging.getLogger(__name__)




async def job_priority_handler(callback: CallbackQuery, state: FSMContext):
    # Get current job ID from state
    data = await state.get_data()
    job_id = data.get('current_job_id')
    
    if not job_id:
        await callback.message.answer("❌ No job selected. Please add a job URL first.")
        return
        
    # Show keyboard with priority options
    await callback.message.answer(
        "Select job priority:",
        reply_markup=get_priority_keyboard()
    )



async def process_adding_job_priority(callback: CallbackQuery, state: FSMContext):
    # Get priority from callback data (e.g., "set_priority_high" -> "high")
    priority = callback.data.split('_')[-1]
    
    # Get current job ID from state
    data = await state.get_data()
    job_id = data.get('current_job_id')
    
    if not job_id:
        await callback.message.answer("❌ No job selected. Please add a job URL first.")
        return

    # Update priority in database
    async for session in get_db():
        job = await session.get(Jobb, job_id)
        if not job:
            await callback.message.answer("❌ Job not found.")
            return
        
        job.priority = priority
        await session.commit()
        
        await callback.message.answer(
            f"✅ Priority updated to {priority}",
            reply_markup=get_job_metadata_keyboard()
        )