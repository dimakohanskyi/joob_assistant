from aiogram.types import Message, FSInputFile



async def start_handler(message: Message):
    bot_images_path = "media/images/joob_assistent_logo.png"
    await message.answer_photo(
        photo=FSInputFile(bot_images_path),
        caption=(
            "👋 Hey there! I'm **Joob Assistant** — your smart job-hunting buddy 💼🤖\n\n"
            "Here's what I can help you with:\n"
            "👤 Build your profile\n"
            "🔍 Analyze job posts with AI\n"
            "✉️ Generate custom cover letters\n"
            "📂 Track your applications\n"
            "📄 Save multiple CVs\n"
            "📊 Organize your job search like a pro\n\n"
            "Let's land your next job together! 🚀"
        ),
        parse_mode="Markdown"
    )
