from aiogram.types import CallbackQuery, FSInputFile, InputMediaDocument
from aiogram.fsm.context import FSMContext
import logging
import os

from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.main_keyboard import get_main_menu
from src.databese.models import Jobb
from src.utils.report_generator import pack_job_analyse_report


configure_logging()
logger = logging.getLogger(__name__)


async def finish_adding_job(callback: CallbackQuery, state: FSMContext):
    try:
        # Get current job ID from state
        data = await state.get_data()
        job_id = data.get('current_job_id')
        
        if not job_id:
            await callback.message.edit_caption(
                caption="❌ No job selected. Please add a job URL first.",
                reply_markup=get_main_menu()
            )
            return

        # Get job data from database
        async for session in get_db():
            job = await session.get(Jobb, job_id)
            if not job:
                await callback.message.edit_caption(
                    caption="❌ Job not found.",
                    reply_markup=get_main_menu()
                )
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
            
            # If AI summary exists and is long, send it as a document
            if job.ai_summary:
                if len(job.ai_summary) > 1000:  # If summary is longer than 1000 characters
                    # Create report file
                    report_path = pack_job_analyse_report(job.ai_summary)
                    
                    try:
                        # Create FSInputFile and InputMediaDocument
                        file = FSInputFile(report_path, filename="job_analysis.txt")
                        media = InputMediaDocument(
                            media=file,
                            caption=summary
                        )
                        
                        # Update the message with the document
                        await callback.message.edit_media(
                            media=media,
                            reply_markup=get_main_menu()
                        )
                    finally:
                        # Clean up the temporary file
                        try:
                            if os.path.exists(report_path):
                                os.remove(report_path)
                        except Exception as e:
                            logger.error(f"Error removing temporary file: {str(e)}")
                else:
                    # If summary is short, include it in the message
                    summary += f"\n\n🤖 AI Summary:\n{job.ai_summary}"
                    await callback.message.edit_caption(
                        caption=summary,
                        reply_markup=get_main_menu()
                    )
            else:
                # If no AI summary, just update the caption
                await callback.message.edit_caption(
                    caption=summary,
                    reply_markup=get_main_menu()
                )
            
            # Clear state
            await state.clear()
            
    except Exception as e:
        logger.error(f"Error in finish_adding_job: {str(e)}")
        await callback.message.edit_caption(
            caption="❌ An error occurred while finishing job addition. Please try again.",
            reply_markup=get_main_menu()
        )