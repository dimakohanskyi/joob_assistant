from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging

from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.job_keyboard import get_job_metadata_keyboard
from src.keyboards.profile_keyboard import get_profile_keyboard
from src.databese.models import User, Jobb
from src.utils.valid_url_checker import is_valid_url
from src.states.job_states.job_item_url_state import JobUrlState




configure_logging()
logger = logging.getLogger(__name__)





async def add_job_item_url(callback_query: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(JobUrlState.waiting_for_item_url)
        await state.update_data(last_bot_message=callback_query.message.message_id)
        
        await callback_query.message.edit_caption(
            caption="Please enter the job posting URL.\n\n"
            "Example: https://www.linkedin.com/jobs/view/1234567890",
            reply_markup=get_profile_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in add_job_item_url: {str(e)}")
        await callback_query.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_profile_keyboard()
        )




async def process_job_item_url(message: Message, state: FSMContext):
    try:
        url = message.text.strip()
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        # Delete user's message
        await message.delete()

        if not is_valid_url(url):
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Invalid URL format. Please enter a valid URL.",
                reply_markup=get_profile_keyboard()
            )
            return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ User not found. Please create a profile first.",
                    reply_markup=get_profile_keyboard()
                )
                return

            existing_job = await Jobb.check_url_exists(session=session, user_id=user.id, url=url)
            if existing_job:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ This job URL is already in your list",
                    reply_markup=get_profile_keyboard()
                )
                return

            new_job = Jobb(
                user_id=user.id,
                url=url
            )
            
            session.add(new_job)
            await session.commit()
            await session.refresh(new_job)

            await state.update_data(current_job_id=new_job.id)
            
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption=(
                    f"✅ Job URL added successfully!\n\n"
                    f"Now you can:\n"
                    f"• Set priority\n"
                    f"• Set status\n"
                    f"• Generate AI summary\n"
                    f"• Add additional info\n"
                    f"• Or finish adding the job"
                ),
                reply_markup=get_job_metadata_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error in process_job_item_url: {str(e)}")
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="❌ An error occurred while processing the URL. Please try again.",
            reply_markup=get_profile_keyboard()
        )









