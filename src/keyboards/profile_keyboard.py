from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_profile_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_menu")],
    ])
    return keyboard


def get_create_profile_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Experience", callback_data="add_user_experience")],
        [InlineKeyboardButton(text="🛠 Hard Skills", callback_data="profile_hard_skills")],
        [InlineKeyboardButton(text="🤝 Soft Skills", callback_data="profile_soft_skills")],
        [InlineKeyboardButton(text="🎓 Education", callback_data="profile_education")],
        [InlineKeyboardButton(text="🌍 Languages", callback_data="profile_languages")],
        [InlineKeyboardButton(text="📂 Projects", callback_data="profile_projects")],
        [InlineKeyboardButton(text="📧 Email", callback_data="profile_email")],
        [InlineKeyboardButton(text="💻 GitHub", callback_data="profile_github")],
        [InlineKeyboardButton(text="🔗 LinkedIn", callback_data="profile_linkedin")],
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_menu")],
    ])
    return keyboard



def get_confirmation_keyboard(
    confirm_callback: str,
    cancel_callback: str,
    back_callback: str = "create_profile",
    confirm_text: str = "✅ Yes",
    cancel_text: str = "❌ No",
    back_text: str = "⬅️ Back"
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=confirm_text, callback_data=confirm_callback),
            InlineKeyboardButton(text=cancel_text, callback_data=cancel_callback)
        ],
        [InlineKeyboardButton(text=back_text, callback_data=back_callback)]
    ])
    return keyboard


def get_experience_confirmation_keyboard():
    return get_confirmation_keyboard(
        confirm_callback="confirm_experience_update",
        cancel_callback="cancel_experience_update"
    )

def get_hard_skills_confirmation_keyboard():
    return get_confirmation_keyboard(
        confirm_callback="confirm_hard_skills_update",
        cancel_callback="cancel_hard_skills_update"
    )


def get_soft_skills_confirmation_keyboard():
    return get_confirmation_keyboard(
        confirm_callback="confirm_soft_skills_update",
        cancel_callback="cancel_soft_skills_update"
    )


def get_education_confirmation_keyboard():
    return get_confirmation_keyboard(
        confirm_callback="confirm_education_update",
        cancel_callback="cancel_education_update"
    )


def get_languages_confirmation_keyboard():
    return get_confirmation_keyboard(
        confirm_callback="confirm_languages_update",
        cancel_callback="cancel_languages_update"
    )


def get_projects_confirmation_keyboard():
    return get_confirmation_keyboard(
        confirm_callback="confirm_projects_update",
        cancel_callback="cancel_projects_update"
    )


def get_email_confirmation_keyboard():
    return get_confirmation_keyboard(
        confirm_callback="confirm_email_update",
        cancel_callback="cancel_email_update"
    )


def get_github_confirmation_keyboard():
    return get_confirmation_keyboard(
        confirm_callback="confirm_github_update",
        cancel_callback="cancel_github_update"
    )


def get_linkedin_confirmation_keyboard():
    return get_confirmation_keyboard(
        confirm_callback="confirm_linkedin_update",
        cancel_callback="cancel_linkedin_update"
    )








