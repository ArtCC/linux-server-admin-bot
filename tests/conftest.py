"""
Shared pytest configuration and fixtures.
"""
import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_settings():
    """Create test settings."""
    from config import settings
    return settings


@pytest.fixture
def mock_telegram_update():
    """Create mock Telegram update for testing handlers."""
    from unittest.mock import Mock
    from telegram import User, Chat, Message, Update
    
    user = Mock(spec=User)
    user.id = 123456789
    user.username = "testuser"
    user.first_name = "Test"
    
    chat = Mock(spec=Chat)
    chat.id = 123456789
    
    message = Mock(spec=Message)
    message.chat = chat
    message.reply_text = Mock()
    message.reply_photo = Mock()
    
    update = Mock(spec=Update)
    update.effective_user = user
    update.effective_chat = chat
    update.message = message
    
    return update


@pytest.fixture
def mock_bot_context():
    """Create mock bot context for testing handlers."""
    from unittest.mock import Mock
    from telegram.ext import ContextTypes
    
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = []
    context.bot = Mock()
    context.bot.send_message = Mock()
    context.bot.send_chat_action = Mock()
    
    return context
