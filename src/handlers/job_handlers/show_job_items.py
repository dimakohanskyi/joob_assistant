from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from src.settings.logging_config import configure_logging
import logging
from src.databese.settings import get_db
from src.databese.models import Jobb, User
from src.utils.report_generator import generate_excel_report, generate_pdf_report
from sqlalchemy import select
import os

configure_logging()
logger = logging.getLogger(__name__)




async def show_job_items(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    async for session in get_db():
        try:
            user = await User.get_user(tg_user_id=user_id, session=session)
            result = await session.execute(select(Jobb).where(Jobb.user_id == user.id))
            job_items = result.scalars().all()

            if not job_items:
                await callback.message.answer(
                    "You don't have any job applications yet.\n"
                )
                return
            
            # Generate and send Excel report
            excel_file = generate_excel_report(job_items)
            await callback.message.answer_document(
                document=FSInputFile(excel_file),
                caption="📋 Your Job Applications in Excel format!"
            )
            # Delete Excel file after sending
            os.remove(excel_file)
            
            # Generate and send PDF report
            pdf_file = generate_pdf_report(job_items)
            await callback.message.answer_document(
                document=FSInputFile(pdf_file),
                caption="📄 Your Job Applications in PDF format!"
            )
            # Delete PDF file after sending
            os.remove(pdf_file)

        except Exception as e:
            logger.error(f"Error showing job items: {str(e)}")
            await callback.message.answer(
                "Sorry, there was an error loading your job applications. Please try again later."
            )
