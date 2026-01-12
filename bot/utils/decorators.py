"""
Decorators for bot handlers.
"""
import functools
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import get_logger, settings

logger = get_logger(__name__)


# Rate limiting storage
_rate_limit_storage: Dict[int, list] = defaultdict(list)


def authorized_only(func: Callable) -> Callable:
    """
    Decorator to restrict command access to authorized users only.

    Args:
        func: Handler function to wrap

    Returns:
        Wrapped function
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Optional[any]:
        """Check authorization before executing handler."""
        # Handle both function and method calls
        if len(args) >= 2 and hasattr(args[0], '__class__') and not isinstance(args[0], Update):
            # Method call: (self, update, context)
            update = args[1]
            context = args[2] if len(args) > 2 else kwargs.get('context')
        else:
            # Function call: (update, context)
            update = args[0]
            context = args[1] if len(args) > 1 else kwargs.get('context')
        
        user = update.effective_user
        if not user:
            logger.warning("Received update without user information")
            return None

        allowed_ids = settings.allowed_user_ids

        if user.id not in allowed_ids:
            logger.warning(
                f"Unauthorized access attempt by user {user.id} ({user.username or user.first_name})"
            )
            await update.message.reply_text(
                f"🔒 Access denied. You are not authorized to use this bot.\n"
                f"Your user ID: {user.id}"
            )
            return None

        logger.info(f"Authorized user {user.id} ({user.username or user.first_name}) executing {func.__name__}")
        return await func(*args, **kwargs)

    return wrapper


def rate_limited(calls: int = 10, period: int = 60) -> Callable:
    """
    Decorator to rate limit command usage per user.

    Args:
        calls: Number of calls allowed
        period: Time period in seconds

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Optional[any]:
            """Check rate limit before executing handler."""
            # Handle both function and method calls
            if len(args) >= 2 and hasattr(args[0], '__class__') and not isinstance(args[0], Update):
                update = args[1]
            else:
                update = args[0]
            
            user = update.effective_user
            if not user:
                return None

            user_id = user.id
            now = time.time()

            # Clean old entries
            _rate_limit_storage[user_id] = [
                timestamp for timestamp in _rate_limit_storage[user_id] if now - timestamp < period
            ]

            # Check rate limit
            if len(_rate_limit_storage[user_id]) >= calls:
                oldest = _rate_limit_storage[user_id][0]
                wait_time = int(period - (now - oldest))
                logger.warning(f"Rate limit exceeded for user {user_id}")
                await update.message.reply_text(
                    f"⚠️ Rate limit exceeded. Please wait {wait_time} seconds before trying again."
                )
                return None

            # Add current timestamp
            _rate_limit_storage[user_id].append(now)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def log_execution(func: Callable) -> Callable:
    """
    Decorator to log handler execution time.

    Args:
        func: Handler function to wrap

    Returns:
        Wrapped function
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Optional[any]:
        """Log execution time."""
        # Handle both function and method calls
        if len(args) >= 2 and hasattr(args[0], '__class__') and not isinstance(args[0], Update):
            update = args[1]
        else:
            update = args[0]
        
        user = update.effective_user
        user_info = f"{user.id} ({user.username or user.first_name})" if user else "Unknown"

        start_time = time.time()
        logger.info(f"Handler {func.__name__} started by user {user_info}")

        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Handler {func.__name__} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Handler {func.__name__} failed after {execution_time:.2f}s: {e}")
            raise

    return wrapper


def error_handler(func: Callable) -> Callable:
    """
    Decorator to handle errors in handlers gracefully.

    Args:
        func: Handler function to wrap

    Returns:
        Wrapped function
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Optional[any]:
        """Handle errors gracefully."""
        # Handle both function and method calls
        if len(args) >= 2 and hasattr(args[0], '__class__') and not isinstance(args[0], Update):
            update = args[1]
        else:
            update = args[0]
        
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in handler {func.__name__}: {e}", exc_info=True)
            
            if update.message:
                await update.message.reply_text(
                    f"❌ An error occurred while processing your request:\n{str(e)[:200]}"
                )
            
            return None

    return wrapper


def typing_action(func: Callable) -> Callable:
    """
    Decorator to send typing action while processing.

    Args:
        func: Handler function to wrap

    Returns:
        Wrapped function
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Optional[any]:
        """Send typing action."""
        # Handle both function and method calls
        if len(args) >= 2 and hasattr(args[0], '__class__') and not isinstance(args[0], Update):
            update = args[1]
            context = args[2] if len(args) > 2 else kwargs.get('context')
        else:
            update = args[0]
            context = args[1] if len(args) > 1 else kwargs.get('context')
        
        if update.effective_chat and context:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action="typing"
            )
        
        return await func(*args, **kwargs)

    return wrapper


# Combined decorator for common use case
def standard_handler(func: Callable) -> Callable:
    """
    Combined decorator applying authorization, rate limiting, logging, and error handling.

    Args:
        func: Handler function to wrap

    Returns:
        Wrapped function
    """
    return (
        authorized_only(
            rate_limited(calls=settings.rate_limit_calls, period=settings.rate_limit_period)(
                log_execution(error_handler(typing_action(func)))
            )
        )
    )
