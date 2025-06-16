from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton






def get_job_item_actions_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Get Job Item Info", callback_data="get_job_item_info")],
        [InlineKeyboardButton(text="✏️ Update Job Item", callback_data="update_job_item")],
        [InlineKeyboardButton(text="🔙 Back to Main Menu", callback_data="main_menu")]
    ])
    return keyboard 