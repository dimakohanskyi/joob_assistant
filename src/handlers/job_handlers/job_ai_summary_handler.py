from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaDocument
from aiogram.fsm.context import FSMContext
import logging
import os

from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.job_keyboard import get_job_metadata_keyboard
from src.keyboards.profile_keyboard import get_create_profile_keyboard
from src.databese.models import Jobb
from src.ai_analyse.job_item_analyse import analyse_job_url
from src.utils.report_generator import pack_job_analyse_report

configure_logging()
logger = logging.getLogger(__name__)

async def job_ai_summary_handler(callback: CallbackQuery, state: FSMContext):
    """Handle the AI summary generation request"""
    try:
        # Get current job ID from state
        data = await state.get_data()
        job_id = data.get('current_job_id')
        
        if not job_id:
            logger.error("No job ID found in state")
            await callback.message.edit_caption(
                caption="❌ No job selected. Please add a job URL first.",
                reply_markup=get_create_profile_keyboard()
            )
            return

        # Get job from database
        async for session in get_db():
            job = await session.get(Jobb, job_id)
            if not job:
                logger.error(f"Job not found with ID: {job_id}")
                await callback.message.edit_caption(
                    caption="❌ Job not found.",
                    reply_markup=get_create_profile_keyboard()
                )
                return

            if not job.url:
                logger.error(f"Job URL is empty for job ID: {job_id}")
                await callback.message.edit_caption(
                    caption="❌ Job URL is missing. Please add a job URL first.",
                    reply_markup=get_job_metadata_keyboard()
                )
                return

            # Show processing message
            await callback.message.edit_caption(
                caption="🤖 Generating AI summary... Please wait.",
                reply_markup=get_job_metadata_keyboard()
            )

            # Generate AI summary
            ai_summary = await analyse_job_url(job.url)
            
            if not ai_summary:
                logger.error(f"Failed to generate AI summary for job ID: {job_id}")
                await callback.message.edit_caption(
                    caption="❌ Failed to generate AI summary. Please try again.",
                    reply_markup=get_job_metadata_keyboard()
                )
                return

            try:
                # Save AI summary to database
                job.ai_summary = ai_summary
                await session.commit()
                logger.info(f"Successfully saved AI summary for job ID: {job_id}")

                # Create report file
                report_path = pack_job_analyse_report(ai_summary)

                # Create FSInputFile from the local file
                file = FSInputFile(report_path, filename="job_analysis.txt")
                
                # Create InputMediaDocument
                media = InputMediaDocument(
                    media=file,
                    caption="✅ AI Summary generated and saved successfully!"
                )
                
                # Update the current message with the document
                await callback.message.edit_media(
                    media=media,
                    reply_markup=get_job_metadata_keyboard()
                )
            except Exception as e:
                await session.rollback()
                logger.error(f"Error saving AI summary to database: {str(e)}")
                raise
            finally:
                # Clean up the temporary file
                try:
                    if os.path.exists(report_path):
                        os.remove(report_path)
                except Exception as e:
                    logger.error(f"Error removing temporary file: {str(e)}")

    except Exception as e:
        logger.error(f"Error in job_ai_summary_handler: {str(e)}")
        await callback.message.edit_caption(
            caption="❌ An error occurred while generating AI summary. Please try again.",
            reply_markup=get_job_metadata_keyboard()
        ) 