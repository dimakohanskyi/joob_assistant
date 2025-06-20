from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.job_keyboard import get_job_metadata_keyboard, get_job_status_keyboard
from src.keyboards.profile_keyboard import get_create_profile_keyboard
from src.databese.models import Jobb


configure_logging()
logger = logging.getLogger(__name__)



async def job_status_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    job_id = data.get('current_job_id')
    
    if not job_id:
        await callback.message.edit_caption(
            caption="❌ No job selected. Please add a job URL first.",
            reply_markup=get_create_profile_keyboard()
            )
        return
        
    await callback.message.edit_caption(
        caption="Select job status:",
        reply_markup=get_job_status_keyboard()
    )



async def process_adding_job_status(callback: CallbackQuery, state: FSMContext):
    try:
        status = callback.data.replace("set_status_", "")
        
        data = await state.get_data()
        job_id = data.get('current_job_id')
        
        if not job_id:
            logger.error("No job ID found in state")
            await callback.message.edit_caption(
                caption="❌ No job selected. Please add a job URL first.",
                reply_markup=get_job_status_keyboard()
                )
            return

        async for session in get_db():
            job = await session.get(Jobb, job_id)
            if not job:
                await callback.message.edit_caption(
                    caption="❌ Job not found.",
                    reply_markup=get_job_status_keyboard()
                    )
                return
            
            if job.status == status:
                await callback.message.edit_caption(
                    caption=f"Status is already set to {status}",
                    reply_markup=get_job_metadata_keyboard()
                )
                return
            
            try:
                job.status = status
                await session.commit()
                
                await callback.message.edit_caption(
                    caption=f"✅ Status updated to {status}",
                    reply_markup=get_job_metadata_keyboard()
                )
            except Exception as e:
                await session.rollback()
                await callback.message.edit_caption(
                    caption="❌ Failed to update status. Please try again.",
                    reply_markup=get_job_metadata_keyboard()
                )
            
    except Exception as e:
        logger.error(f"Error in process_adding_job_status: {str(e)}")
        await callback.message.edit_caption(
            caption="❌ An error occurred while updating status. Please try again.",
            reply_markup=get_job_metadata_keyboard()
        )

