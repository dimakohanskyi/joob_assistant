from aiogram.types import CallbackQuery, Message
from databese.models import User, Profile
from databese.settings import get_db
from settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from keyboards.profile_keyboard import get_create_profile_keyboard
from states.languages_state import LanguagesState
from aiogram.fsm.context import FSMContext



configure_logging()
logger = logging.getLogger(__name__)



async def add_languages(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.user_languages:
                await state.set_state(LanguagesState.waiting_for_update_confirmation)
                await callback.message.answer(
                    f"Your current languages are: {profile.user_languages}\n"
                    "Would you like to update them? (yes/no)"
                )
            else:
                await state.set_state(LanguagesState.waiting_for_languages)
                await callback.message.answer(
                    "Please enter your languages, separating each language with a comma (,).\n\n"
                    "Example:\n"
                    "English (Fluent), German (Intermediate), Norwegian (Basic)\n\n"
                    "Tips:\n"
                    "• Use commas to separate languages\n"
                    "• Include proficiency level in parentheses\n"
                    "• Common proficiency levels: Native, Fluent, Advanced, Intermediate, Basic"
                )

    except Exception as ex:
        logger.error(f"Error in add_languages: {ex}")
        await callback.message.answer("❌ An error occurred. Please try again.")





async def process_adding_languages(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        
        if current_state == LanguagesState.waiting_for_update_confirmation:
            if message.text.lower() in ['yes', 'y']:
                await state.set_state(LanguagesState.waiting_for_languages)
                await message.answer(
                    "Please enter your languages, separating each language with a comma (,).\n\n"
                    "Example:\n"
                    "English (Fluent), German (Intermediate), Norwegian (Basic)"
                )
            elif message.text.lower() in ['no', 'n']:
                await state.clear()
                await message.answer("Languages update cancelled.", reply_markup=get_create_profile_keyboard())
            else:
                await message.answer("Please answer with 'yes' or 'no'")
            return

        languages = message.text.strip()
        
        if not languages:
            await message.answer(
                "Please enter at least one language.\n"
                "Example: English (Fluent), German (Intermediate)"
            )
            return
            
        if len(languages) > 500:
            await message.answer(
                "❌ Your message is too long. Please keep it under 500 characters.\n"
                "Try to be more concise with your language entries.\n\n"
                "Example of good format:\n"
                "English (Fluent), German (Intermediate), Norwegian (Basic)"
            )
            return
            
        languages_list = [lang.strip() for lang in languages.split(',')]
        
        if len(languages_list) > 10:
            await message.answer(
                "❌ You've entered too many languages. Please limit to 10 languages maximum.\n"
                "Focus on your most proficient languages.\n\n"
                "Example of good format:\n"
                "English (Fluent), German (Intermediate), Norwegian (Basic)"
            )
            return
            
        for lang in languages_list:
            if len(lang) > 50:
                await message.answer(
                    f"❌ The language entry '{lang}' is too long. Please keep each entry under 50 characters.\n\n"
                    "Example of good format:\n"
                    "English (Fluent), German (Intermediate), Norwegian (Basic)"
                )
                return
            if len(lang) < 5:
                await message.answer(
                    "❌ Each language entry should be at least 5 characters long.\n\n"
                    "Example of good format:\n"
                    "English (Fluent), German (Intermediate), Norwegian (Basic)"
                )
                return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.update_profile(
                user_id=user.id,
                update_data={"user_languages": languages},
                session=session
            )

            if profile:
                await message.answer(
                    f"✅ Your languages have been saved!\nLanguages: {languages}",
                    reply_markup=get_create_profile_keyboard()
                )
            else:
                await message.answer(
                    "❌ Sorry, there was an error saving your languages. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing languages input: {ex}")
        await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )
        await state.clear()
