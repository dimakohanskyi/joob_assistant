import os
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaDocument
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
import logging

from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.job_item_actions_keyboard import get_job_item_actions_keyboard
from src.keyboards.job_keyboard import get_job_metadata_keyboard
from src.keyboards.main_keyboard import get_main_menu
from src.databese.models import Jobb, User
from src.states.job_states.job_get_update_state import JobGetUpdateState
from src.utils.report_generator import pack_job_analyse_report



configure_logging()
logger = logging.getLogger(__name__)



async def get_update_job_handler(callback: CallbackQuery):
    await callback.message.edit_caption(
        caption="Please choose what you want to do with the job item:",
        reply_markup=get_job_item_actions_keyboard()
    )


async def get_job_item_info_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JobGetUpdateState.waiting_for_item_id)
    await state.update_data(last_bot_message=callback.message.message_id)
    await callback.message.edit_caption(
        caption="Please enter the job item ID you want to get information about:",
        reply_markup=get_job_item_actions_keyboard()
    )


async def process_get_job_item_info(message: Message, state: FSMContext):
    try:
        # Delete user's message
        await message.delete()
        
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        try:
            job_id = int(message.text.strip())
        except ValueError:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Please enter a valid job ID (numbers only).",
                reply_markup=get_job_item_actions_keyboard()
                )
            return

        user_id = message.from_user.id

        async for session in get_db():
            user = await User.get_user(tg_user_id=user_id, session=session)
            if not user:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ User not found. Please create a profile first.",
                    reply_markup=get_job_item_actions_keyboard()
                    )
                return

            result = await session.execute(
                select(Jobb)
                .where(
                    Jobb.user_id == user.id,
                    Jobb.id == job_id
                )
            )
            job = result.scalar_one_or_none()

            if not job:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Job item not found or you don't have access to it.",
                    reply_markup=get_job_item_actions_keyboard()
                    )
                return

            # Build job info for caption (basic info only)
            job_info = (
                f"📋 Job Application Details\n\n"
                f"🔗 URL: {job.url}\n"
                f"⭐️ Priority: {job.priority}\n"
                f"📊 Status: {job.status}\n"
                f"📅 Created: {job.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            )

            if job.additional_info:
                job_info += f"\n📝 Additional Information:\n{job.additional_info}\n"

            # Handle AI summary separately - create file if it exists
            file_path = None
            if job.ai_summary:
                # Create file with only AI summary
                file_path = pack_job_analyse_report(job.ai_summary)
                
                try:
                    # Update the original message with file and basic info
                    await message.bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=last_bot_message_id,
                        media=InputMediaDocument(
                            media=FSInputFile(file_path),
                            caption=job_info
                        ),
                        reply_markup=get_job_item_actions_keyboard()
                    )
                finally:
                    # Clean up the temporary file
                    try:
                        os.remove(file_path)
                        logger.info(f"Temporary file {file_path} has been deleted")
                    except Exception as e:
                        logger.error(f"Error deleting temporary file {file_path}: {str(e)}")
            else:
                # No AI summary, just update caption with basic info
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption=job_info,
                    reply_markup=get_job_item_actions_keyboard()
                )

            await state.clear()

    except Exception as e:
        logger.error(f"Error in process_get_job_item_info: {str(e)}")
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="❌ An error occurred while retrieving job information. Please try again.",
            reply_markup=get_main_menu()
        )
        await state.clear()

    

async def update_job_item_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JobGetUpdateState.waiting_for_update_item_id)
    await state.update_data(last_bot_message=callback.message.message_id)
    await callback.message.edit_caption(
        caption="Please enter the job item ID you want to update:",
        reply_markup=get_job_item_actions_keyboard()
    )


async def process_update_job_item_info(message: Message, state: FSMContext):
    try:
        # Delete user's message
        await message.delete()
        
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        try:
            job_id = int(message.text.strip())
        except ValueError:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Please enter a valid job ID (numbers only).",
                reply_markup=get_job_item_actions_keyboard()
                )
            return

        user_id = message.from_user.id

        async for session in get_db():
            user = await User.get_user(tg_user_id=user_id, session=session)
            if not user:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ User not found. Please create a profile first.",
                    reply_markup=get_job_item_actions_keyboard()
                    )
                return

            result = await session.execute(
                select(Jobb)
                .where(
                    Jobb.user_id == user.id,
                    Jobb.id == job_id
                )
            )
            job = result.scalar_one_or_none()

            if not job:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Job item not found or you don't have access to it.",
                    reply_markup=get_job_item_actions_keyboard()
                    )
                return

            # Store the job ID in state for further updates
            await state.update_data(current_job_id=job_id)
            
            # Show current job info and update options
            job_info = (
                f"📋 Current Job Information\n\n"
                f"🔗 URL: {job.url}\n"
                f"⭐️ Priority: {job.priority}\n"
                f"📊 Status: {job.status}\n"
                f"📅 Created: {job.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                f"Select what you want to update:"
            )

            
            
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption=job_info,
                reply_markup=get_job_metadata_keyboard()
                )

    except Exception as e:
        logger.error(f"Error in process_update_job_item_info: {str(e)}")
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="❌ An error occurred while retrieving job information. Please try again.",
            reply_markup=get_main_menu()
        )
        await state.clear()

    

