from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.job_keyboard import get_job_metadata_keyboard
from src.keyboards.job_item_actions_keyboard import get_job_item_actions_keyboard
from src.keyboards.main_keyboard import get_main_menu
import logging
from src.databese.models import Jobb, User
from src.states.job_states.job_get_update_state import JobGetUpdateState




configure_logging()
logger = logging.getLogger(__name__)




async def get_update_job_handler(callback: CallbackQuery):
    await callback.message.answer(
        text="Please choose what you want to do with the job item:",
        reply_markup=get_job_item_actions_keyboard()
    )



async def get_job_item_info_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JobGetUpdateState.waiting_for_item_id)
    await callback.message.answer(
        "Please enter the job item ID you want to get information about:"
    )


async def process_get_job_item_info(message: Message, state: FSMContext):
    try:
        try:
            job_id = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Please enter a valid job ID (numbers only).")
            return

        user_id = message.from_user.id

        async for session in get_db():
            user = await User.get_user(tg_user_id=user_id, session=session)
            if not user:
                await message.answer("❌ User not found. Please create a profile first.")
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
                await message.answer("❌ Job item not found or you don't have access to it.")
                return

            job_info = (
                f"📋 Job Application Details\n\n"
                f"🔗 URL: {job.url}\n"
                f"⭐️ Priority: {job.priority}\n"
                f"📊 Status: {job.status}\n"
                f"📅 Created: {job.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            )

            if job.ai_summary:
                job_info += f"\n🤖 AI Analysis:\n{job.ai_summary}\n"

            if job.additional_info:
                job_info += f"\n📝 Additional Information:\n{job.additional_info}\n"

            await message.answer(job_info, reply_markup=get_main_menu())
            await state.clear()

    except Exception as e:
        logger.error(f"Error in process_get_job_item_info: {str(e)}")
        await message.answer(
            "❌ An error occurred while retrieving job information. Please try again.",
            reply_markup=get_main_menu()
        )
        await state.clear()


    

async def update_job_item_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JobGetUpdateState.waiting_for_item_id)
    await callback.message.answer(
        "Please enter the job item ID you want to update:"
    )



