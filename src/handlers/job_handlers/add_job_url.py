from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.job_keyboard import get_initial_job_keyboard, get_job_metadata_keyboard
import logging
from src.databese.models import User, Jobb
from src.utils.valid_url_checker import is_valid_url
from src.states.job_states.job_item_url_state import JobUrlState




configure_logging()
logger = logging.getLogger(__name__)





async def add_job_item_url(callback_query: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(JobUrlState.waiting_for_item_url)
        
        await callback_query.message.answer(
            "Please enter the job posting URL.\n\n"
            "Example: https://www.linkedin.com/jobs/view/1234567890",
        )

    except Exception as e:
        logger.error(f"Error in add_job_item_url: {str(e)}")
        await callback_query.message.answer(
            "❌ An error occurred. Please try again.",
            reply_markup=get_initial_job_keyboard()
        )




async def process_job_item_url(message: Message, state: FSMContext):
    try:
        url = message.text.strip()
        logger.info(url)

        if not is_valid_url(url):
            await message.answer(
                "❌ Invalid URL format. Please enter a valid URL.",
                reply_markup=get_initial_job_keyboard()
            )
            return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.answer(
                    "❌ User not found. Please create a profile first.",
                    reply_markup=get_initial_job_keyboard()
                )
                return

            existing_job = await Jobb.check_url_exists(session=session, user_id=user.id, url=url)
            if existing_job:
                await message.answer(
                    "❌ This job URL is already in your list",
                    reply_markup=get_initial_job_keyboard()
                )
                return

            new_job = Jobb(
                user_id=user.id,
                url=url
            )

            logger.info(f"Creating new job with URL: {url} for user_id: {user.id}")
            
            session.add(new_job)
            await session.commit()
            await session.refresh(new_job)

            logger.info(f"Successfully created job with ID: {new_job.id}")

            await state.update_data(current_job_id=new_job.id)
            
            await message.answer(
                f"✅ Job URL added successfully!\n\n"
                f"Now you can:\n"
                f"• Set priority\n"
                f"• Set status\n"
                f"• Generate AI summary\n"
                f"• Add additional info\n"
                f"• Or finish adding the job",
                reply_markup=get_job_metadata_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error in process_job_item_url: {str(e)}")
        await message.answer(
            "❌ An error occurred while processing the URL. Please try again.",
            reply_markup=get_initial_job_keyboard()
        )









