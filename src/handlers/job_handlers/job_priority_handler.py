from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.job_keyboard import get_job_metadata_keyboard, get_priority_keyboard
from src.keyboards.profile_keyboard import get_create_profile_keyboard
from src.databese.models import Jobb


configure_logging()
logger = logging.getLogger(__name__)




async def job_priority_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    job_id = data.get('current_job_id')
    
    if not job_id:
        await callback.message.edit_caption(
            caption="❌ No job selected. Please add a job URL first.",
            reply_markup=get_create_profile_keyboard()
            )
        return
        
    await callback.message.edit_caption(
        caption="Select job priority:",
        reply_markup=get_priority_keyboard()
    )



async def process_adding_job_priority(callback: CallbackQuery, state: FSMContext):
    priority = callback.data.split('_')[-1]
    
    data = await state.get_data()
    job_id = data.get('current_job_id')
    
    if not job_id:
        await callback.message.edit_caption(
            caption="❌ No job selected. Please add a job URL first.",
            reply_markup=get_create_profile_keyboard()
            )
        return

    async for session in get_db():
        job = await session.get(Jobb, job_id)
        if not job:
            await callback.message.edit_caption(
                caption="❌ Job not found.",
                reply_markup=get_create_profile_keyboard()
                )
            return
        
        job.priority = priority
        await session.commit()
        
        await callback.message.edit_caption(
            caption=f"✅ Priority updated to {priority}",
            reply_markup=get_job_metadata_keyboard()
        )