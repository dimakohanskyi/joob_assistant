from aiogram.types import CallbackQuery
from keyboards.main_keyboard import get_main_menu


async def main_menu_handler(callback: CallbackQuery):
    menu_message = "🏠 Main Menu"
    
    await callback.message.answer(
        text=menu_message,
        reply_markup=get_main_menu()
    ) 