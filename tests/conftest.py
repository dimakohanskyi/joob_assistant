import pytest
from unittest.mock import AsyncMock
from databese.settings import get_db
from databese.models import User

@pytest.fixture
async def mock_db_session():
    """Fixture that provides a mock database session"""
    mock_session = AsyncMock()

    async def mock_get_db():
        yield mock_session
    
    return mock_session, mock_get_db

@pytest.fixture
async def mock_user():
    """Fixture that provides a mock user"""
    return AsyncMock(spec=User)


@pytest.fixture
def mock_telegram_message():
    """Fixture that provides a mock Telegram message"""
    from aiogram.types import Message, User as TelegramUser
    from unittest.mock import MagicMock
    
    # Create mock message
    mock_message = MagicMock(spec=Message)
    mock_message.from_user = MagicMock(spec=TelegramUser)
    mock_message.from_user.id = 123
    mock_message.from_user.username = "test_user"
    
    return mock_message 