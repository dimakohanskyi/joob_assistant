from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def get_profile_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_menu")],
    ])
    return keyboard


def get_create_profile_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Experience", callback_data="profile_experience")],
        [InlineKeyboardButton(text="🛠 Hard Skills", callback_data="profile_hard_skills")],
        [InlineKeyboardButton(text="🤝 Soft Skills", callback_data="profile_soft_skills")],
        [InlineKeyboardButton(text="🎓 Education", callback_data="profile_education")],
        [InlineKeyboardButton(text="🌍 Languages", callback_data="profile_languages")],
        [InlineKeyboardButton(text="📂 Projects", callback_data="profile_projects")],
        [InlineKeyboardButton(text="📧 Email", callback_data="profile_email")],
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_menu")],
    ])
    return keyboard


