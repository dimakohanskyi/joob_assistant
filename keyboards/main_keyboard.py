from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_commands():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 User Profile", callback_data="profile")]
    ])

    return keyboard