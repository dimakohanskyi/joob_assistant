import pytest
from unittest.mock import patch
from handlers.start_handler import start_handler




@pytest.mark.asyncio
async def test_start_handler_new_user(mock_db_session, mock_telegram_message):
    mock_session, mock_get_db = mock_db_session
    
    with patch('handlers.start_handler.get_db', mock_get_db):
        await start_handler(mock_telegram_message)
        mock_telegram_message.answer_photo.assert_called_once()
        call_args = mock_telegram_message.answer_photo.call_args
        assert call_args[1]['photo'].path == "media/images/joob_assistent_logo.png"
        assert "Welcome to **Joob Assistant**" in call_args[1]['caption'] 