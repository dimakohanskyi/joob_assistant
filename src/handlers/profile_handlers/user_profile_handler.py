import os
from aiogram.types import CallbackQuery, InputMediaDocument, FSInputFile
import logging

from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.profile_keyboard import get_create_profile_keyboard
from src.utils.report_generator import pack_job_analyse_report


configure_logging()
logger = logging.getLogger(__name__)


async def profile_handler(callback: CallbackQuery):
    async for session in get_db():
        try:
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            
            if user:
                profile = await Profile.get_user_profile(session=session, user_id=user.id)
                experience = f"{profile.user_experience} years" if profile.user_experience else "Not specified"
                languages = profile.user_languages if profile.user_languages else "Not specified"
                hard_skills = profile.hard_skills if profile.hard_skills else "Not specified"
                soft_skills = profile.soft_skills if profile.soft_skills else "Not specified"
                education = profile.education if profile.education else "Not specified"
                github = profile.user_git_hub if profile.user_git_hub else "Not specified"
                linkedin = profile.user_linkedin if profile.user_linkedin else "Not specified"

                profile_message = (
                    f"👤 <b>Professional Profile</b>\n\n"
                    f"<b>Basic Information:</b>\n"
                    f"• Username: {user.tg_user_name}\n"
                    f"• Email: {user.user_login}\n"
                    f"• Profile Created: {user.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"<b>Professional Details:</b>\n"
                    f"• Experience: {experience}\n"
                    f"• Languages: {languages}\n"
                    f"• Hard Skills: {hard_skills}\n"
                    f"• Soft Skills: {soft_skills}\n"
                    f"• Education: {education}\n"
                    f"<b>Professional Links:</b>\n"
                    f"• GitHub: {github}\n"
                    f"• LinkedIn: {linkedin}"
                )

                if profile.projects and profile.projects != "Not specified":
                    projects_str = str(profile.projects) if not isinstance(profile.projects, str) else profile.projects
                    file_path = pack_job_analyse_report(projects_str)
                    try:
                        await callback.message.edit_media(
                            media=InputMediaDocument(
                                caption=profile_message,
                                media=FSInputFile(file_path),
                                parse_mode="HTML"
                            ),
                            reply_markup=get_create_profile_keyboard()
                        )
                    finally:
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            logger.error(f"Error deleting temporary file {file_path}: {str(e)}")
                else:
                    await callback.message.edit_caption(
                        caption=profile_message,
                        reply_markup=get_create_profile_keyboard(),
                        parse_mode="HTML"
                    )
            else:
                await callback.message.edit_caption(
                    caption="❌ Sorry, we couldn't find your profile data.\n"
                    "Please try creating a profile first or contact support if you believe this is an error.",
                    reply_markup=get_create_profile_keyboard()
                )
        except Exception as ex:
            logger.error(f"Error in profile_handler: {str(ex)}")
            await callback.message.edit_caption(
                caption="❌ Please try again later or contact support if the problem persists.",
                reply_markup=get_create_profile_keyboard()
            )














