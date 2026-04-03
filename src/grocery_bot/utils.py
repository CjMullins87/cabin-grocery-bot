"""Helper functions/handlers."""

from functools import wraps
import os
import re
from datetime import datetime
import logging
from typing import Union

from telegram import Update
from telegram.ext import ContextTypes

from grocery_bot import ROOT_DIR
from grocery_bot.config import TOKEN
from grocery_bot.db.manager import DBManager
from grocery_bot.db.schema import Admin, Order

logger = logging.getLogger(__name__)


def get_token() -> Union[str, None]:
    """Feetches the bot token"""

    # If a token is provided in the config, use that
    if TOKEN:
        logger.info("Retrieving token from config")
        return TOKEN

    # Otherwise, look for it in the environment
    env_token = os.getenv("GROCERY_BOT_TOKEN")
    if env_token:
        logger.info("Retrieving token from environment variable")
        return env_token

    # Finally, we can check our .gitignored sandbox directory
    tar_path = os.path.join(ROOT_DIR / "sandbox" / "token.txt")
    if os.path.exists(tar_path):
        logger.info("Retrieving token from sandbox/token.txt")
        with open(tar_path, "r") as t:
            token = t.read().strip()
            return token


def extract_text(text: str) -> str:
    """Extract the grocery item requested from the command text."""

    match = re.match(r"(/order )(.*)", text)
    if match:
        return match.group(2).strip()
    return ""


def extract_orderid_from_text(text: str) -> int:
    """Extract the orderID from the command plain text"""
    match = re.search(r"Order #: (\d+)", text)
    if match:
        return int(match.group(1))
    logger.warning("Unable to extract match!")
    return 0


def get_order_dict(update: Update) -> dict:
    """Get a dictionary of the order details from the update."""

    container = {}

    # Just kick off with a createddate
    container["createddate"] = datetime.now().isoformat()

    # The User object looks like it's a dataclass, so I can probably access
    # its attributes directly
    user = update.effective_user
    container["username"] = user.username
    container["userid"] = user.id

    # Then the Message object has our text and message_id, which we can
    # use to build our order number
    msg = update.message
    container["txt"] = extract_text(msg.text)

    # This should be unique, since TG message IDs are unique per chat
    container["id"] = int(str(msg.chat_id) + str(msg.message_id))

    return container


def is_admin(userid: int, db_manager: DBManager) -> bool:
    """Helper function to determine if the given user is an Admin

    Args:
        userid (int): A user's TG ID
        db_manager (DBManager): An active DBManager

    Returns:
        bool: True if user is in the Admin table; False otherwise
    """
    with db_manager.get_session() as session:
        if session.get(Admin, userid):
            logger.debug("is_admin: TRUE")
            return True
        else:
            logger.debug("is_admin: FALSE")
            return False


def is_request_owner(userid: int, orderid: int, db_manager: DBManager) -> bool | None:
    """Helper function to determine if a user calling a command on an order
    is the order owner

    Args:
        userid (int): Current user's ID
        order_id (int): Target order's ID #
        db_manager (DBManager): An active DBManager

    Returns:
        bool | None: If an order is retrieved, True if the user is the order owner,
        False if not. If no order is retrieved, None is returned.
    """

    with db_manager.get_session() as session:
        logger.debug("Looking for order ID: %s", orderid)
        order: Order = session.get(Order, orderid)
        if order:
            logger.debug("Order successfully retrieved")
            if userid == order.userid:
                logger.debug("is_owner: TRUE")
                return True
            logger.debug("is_owner: FALSE")
            return False
        else:
            logger.warning("Order not found")
            # Technically if we're here it means that session.get() failed to
            # retrieve anything for the specified order
            return None


def admin_only(func) -> None:
    """Require admin permission to execute a bot command"""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes, *args, **kwargs):
        userid = update.effective_user.id
        db_manager = context.bot_data["db_manager"]

        # If is_admin is true, proceed to execute the expected behavior
        if is_admin(userid, db_manager):
            logger.debug("User is admin, proceed")
            return await func(update, context, *args, **kwargs)

        # Otherwise, fall back to saying No
        logger.debug("User is not admin, decline")
        await update.message.reply_text("Sorry, you don't have the right permissions")
        return

    return func
