from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from settings.logging_config import configure_logging
import logging
from databese.settings import get_db
from databese.models import Jobb, User
import pandas as pd
from datetime import datetime
import os



configure_logging()
logger = logging.getLogger(__name__)




async def create_or_update_job_items_excel(job_items, user_id: int):
    try:
        data = {
            'ID': [job_items.id],
            'URL': [job_items.url],
            'Status': [job_items.status],
            'Priority': [job_items.priority],
            'Created Date': [job_items.created_at.strftime('%Y-%m-%d %H:%M')],
            'AI Summary': [job_items.ai_summary if job_items.ai_summary else ''],
            'Additional Info': [job_items.additional_info if job_items.additional_info else '']
        }
        
        df = pd.DataFrame(data)
        os.makedirs('exports', exist_ok=True)
        filename = f'exports/job_items_{user_id}.xlsx'

        if os.path.exists(filename):
            existing_df = pd.read_excel(filename)
            df = pd.concat([existing_df, df], ignore_index=True)
            df = df.drop_duplicates(subset=['ID'], keep='last')
        
        writer = pd.ExcelWriter(filename, engine='openpyxl')
        
        df.to_excel(writer, sheet_name='Job Applications', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Job Applications']
        
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
        
        writer.close()
        
        return filename
        
    except Exception as e:
        logger.error(f"Error creating/updating Excel file: {str(e)}")
        raise





async def show_job_items(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    async for session in get_db():
        try:
            user = await User.get_user(tg_user_id=user_id, session=session)
            job_items = await Jobb.get_jobb_items(user_id=user.id, session=session)

            if not job_items:
                await callback.message.answer(
                    "You don't have any job applications yet.\n"
                )
                return
            
            excel_file = await create_or_update_job_items_excel(job_items, user_id)
            
            await callback.message.answer_document(
                document=FSInputFile(excel_file),
                caption="📋 Your Job Applications in Excel format!"
            )

        except Exception as e:
            logger.error(f"Error showing job items: {str(e)}")
            await callback.message.answer(
                "Sorry, there was an error loading your job applications. Please try again later."
            )
