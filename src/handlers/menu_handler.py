from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto
from src.keyboards.main_keyboard import get_main_menu





async def main_menu_handler(callback: CallbackQuery):
    bot_images_path = "media/images/joob_assistent_logo.png"
    menu_message = "🏠 Main Menu"
    
    await callback.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(bot_images_path), caption=menu_message),
        reply_markup=get_main_menu()
    )

