from aiogram.types import CallbackQuery, Message, InputMediaDocument, FSInputFile
from aiogram.fsm.context import FSMContext
import logging
from sqlalchemy import select 
import os

from src.settings.logging_config import configure_logging
from src.utils.report_generator import pack_job_analyse_report
from src.ai_cover_letter.ai_cover_letter_generation import ai_cover_letter_generation
from src.states.cover_lettter_states.cover_letter_state import CoverLetterState
from src.keyboards.profile_keyboard import get_profile_keyboard
from src.databese.settings import get_db
from src.databese.models import User, Jobb, Profile


configure_logging()
logger = logging.getLogger(__name__)



async def cover_letter_handler(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(CoverLetterState.waiting_for_job_item_id)
        await state.update_data(last_bot_message=callback.message.message_id)

        await callback.message.edit_caption(
            caption=(
                "Please enter the Job Item ID for which you would like to generate a personalized cover letter.\n\n"
                "Our AI will use your profile and the job summary to create a tailored cover letter."
                ),
            reply_markup=get_profile_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in creating cover letter: {str(e)}")
        await callback.message.edit_caption(
            caption=(
                "❌ An unexpected error occurred while processing your request."
                "Please try again later or contact support if the issue persists."
            ),
            reply_markup=get_profile_keyboard()
        )
    


async def process_creting_cover_letter(message: Message, state: FSMContext):
    try:
        job_id = int(message.text)
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        await message.delete()


        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="📝 Generating your personalized cover letter. Please wait a moment while we prepare your document...",
            reply_markup=get_profile_keyboard()
        )


        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ We couldn't find your user profile in our system. Please create your profile before requesting a cover letter.",
                    reply_markup=get_profile_keyboard()
                )
                return
            

            result = await session.execute(
                select(Jobb)
                .where(Jobb.id == job_id)
                .where(Jobb.user_id == user.id)
            )
            user_job_item = result.scalar()

            if not user_job_item:
                logger.error("Error to find user")
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ The specified Job Item ID was not found in your account. Please double-check the ID and try again.",
                    reply_markup=get_profile_keyboard()
                )
                return
            

            result = await session.execute(
                select(Profile)
                .where(Profile.user_id == user.id)
            )

            user_profile = result.scalar()
            if not user_profile:
                logger.error("Error to find user profile")
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Your profile information could not be found. Please ensure your profile is complete before generating a cover letter.",
                    reply_markup=get_profile_keyboard()
                )
                return


            user_data_set = {
                "user": {
                    "email": user.user_login,
                    "user_experience": user_profile.user_experience,
                    "user_languages": user_profile.user_languages,
                    "hard_skills": user_profile.hard_skills,
                    "soft_skills": user_profile.soft_skills,
                    "education": user_profile.education,
                    "user_previous_projects": user_profile.projects
                },
                "job_description":{
                    "job_summary": user_job_item.ai_summary
                }
            }  


            cover_letter = await ai_cover_letter_generation(user_data_set)
            cover_letter_file_path = pack_job_analyse_report(cover_letter)

            try:
                await message.bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    media=InputMediaDocument(
                        media=FSInputFile(cover_letter_file_path),
                        caption=f"✅ Your personalized cover letter for Job Item ID {user_job_item.id} is ready! Please review the attached document."
                    ),
                    reply_markup=get_profile_keyboard()
                )
            finally:
                try:
                    os.remove(cover_letter_file_path)
                    logger.info(f"Temporary file {cover_letter_file_path} has been deleted")
                except Exception as e:
                    logger.error(f"Error deleting temporary file {cover_letter_file_path}: {str(e)}")
                    
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="🎉 Your cover letter has been successfully generated and sent as a file. If you need another one, simply provide a new Job Item ID.",
                reply_markup=get_profile_keyboard()
            )



    except Exception as e:
        logger.error(f"Error in process_job_item_url: {str(e)}")
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=last_bot_message_id,
            caption="❌ An unexpected error occurred while generating your cover letter. Please try again later or contact support if the issue persists.",
            reply_markup=get_profile_keyboard()
        )
        












