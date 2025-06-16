from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.main_keyboard import get_main_menu
from src.keyboards.job_keyboard import get_initial_job_keyboard
import logging
from src.databese.models import Jobb


configure_logging()
logger = logging.getLogger(__name__)



async def finish_adding_job(callback: CallbackQuery, state: FSMContext):
    try:
        # Get current job ID from state
        data = await state.get_data()
        job_id = data.get('current_job_id')
        
        if not job_id:
            await callback.message.answer("❌ No job selected. Please add a job URL first.")
            return

        # Get job data from database
        async for session in get_db():
            job = await session.get(Jobb, job_id)
            if not job:
                await callback.message.answer("❌ Job not found.")
                return
            
            # Create summary message
            summary = (
                "✅ Job successfully added!\n\n"
                f"🔗 URL: {job.url}\n"
                f"⭐️ Priority: {job.priority}\n"
                f"📊 Status: {job.status}\n"
            )
            
            if job.additional_info:
                summary += f"\n📝 Additional Info:\n{job.additional_info}"
            
            if job.ai_summary:
                summary += f"\n\n🤖 AI Summary:\n{job.ai_summary}"
            
            # Send summary
            await callback.message.answer(summary)
            
            # Clear state
            await state.clear()
            
            # Return to main menu
            await callback.message.answer(
                "You can now:\n"
                "• Add another job\n"
                "• View your jobs\n"
                "• Or return to main menu",
                reply_markup=get_main_menu()
            )
            
    except Exception as e:
        logger.error(f"Error in finish_adding_job: {str(e)}")
        await callback.message.answer(
            "❌ An error occurred while finishing job addition. Please try again.",
            reply_markup=get_initial_job_keyboard()
        )