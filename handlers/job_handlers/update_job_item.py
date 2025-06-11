from aiogram.types import CallbackQuery
from settings.logging_config import configure_logging
import logging
from databese.settings import get_db
from databese.models import Jobb
from keyboards.job_keyboard import (
    get_job_status_keyboard,
    get_priority_keyboard,
    get_job_item_actions_keyboard
)
from sqlalchemy import select, update



configure_logging()
logger = logging.getLogger(__name__)



async def show_status_update(callback: CallbackQuery):
    job_id = int(callback.data.split("_")[-1])
    await callback.message.edit_text(
        "Select new status for this job application:",
        reply_markup=get_job_status_keyboard(job_id)
    )



async def show_priority_update(callback: CallbackQuery):
    job_id = int(callback.data.split("_")[-1])
    await callback.message.edit_text(
        "Select new priority for this job application:",
        reply_markup=get_priority_keyboard(job_id)
    )




async def update_job_status(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data.split("_")
    status = data[2]
    job_id = int(data[-1])
    
    async for session in get_db():
        try:
            result = await session.execute(
                select(Jobb).where(Jobb.id == job_id, Jobb.user_id == user_id)
            )
            job = result.scalar_one_or_none()
            
            if not job:
                await callback.message.edit_text("Job application not found.")
                return
            
            await session.execute(
                update(Jobb)
                .where(Jobb.id == job_id)
                .values(status=status)
            )
            await session.commit()
            
            await callback.message.edit_text(
                f"Status updated successfully to: {status}",
                reply_markup=get_job_item_actions_keyboard(job_id)
            )
            
        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
            await callback.message.edit_text(
                "Sorry, there was an error updating the status. Please try again later."
            )




async def update_job_priority(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data.split("_")
    priority = data[2]
    job_id = int(data[-1])
    
    async for session in get_db():
        try:
            result = await session.execute(
                select(Jobb).where(Jobb.id == job_id, Jobb.user_id == user_id)
            )
            job = result.scalar_one_or_none()
            
            if not job:
                await callback.message.edit_text("Job application not found.")
                return
            
            await session.execute(
                update(Jobb)
                .where(Jobb.id == job_id)
                .values(priority=priority)
            )
            await session.commit()
            
            await callback.message.edit_text(
                f"Priority updated successfully to: {priority}",
                reply_markup=get_job_item_actions_keyboard(job_id)
            )
            
        except Exception as e:
            logger.error(f"Error updating job priority: {str(e)}")
            await callback.message.edit_text(
                "Sorry, there was an error updating the priority. Please try again later."
            ) 