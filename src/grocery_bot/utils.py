"""Helper functions/handlers."""

import os
import re
from datetime import datetime
from telegram import Update
import logging

from grocery_bot import ROOT_DIR
from grocery_bot.config import TOKEN

logger = logging.getLogger(__name__)


def get_token() -> str:
    """Feetches the bot token"""

    # If a token is provided in the config, use that
    if TOKEN:
        logger.debug("Retrieving token from config")
        return TOKEN

    # Othwertise, look for it in the environment
    env_token = os.getenv("GROCERY_BOT_TOKEN")
    if env_token:
        logger.debug("Retrieving token from environment variable")
        return env_token

    # Finally, we can check our .gitignored sandbox directory
    if os.path.exists(os.path.join(ROOT_DIR / "sandbox" / "token.txt")):
        logger.debug("Retrieving token from sandbox/token.txt")
        with open(os.path.join(ROOT_DIR / "sandbox" / "token.txt"), "r") as t:
            token = t.read().strip()
            return token


def extract_text(text: str) -> str:
    """Extract the grocery item requested from the command text."""

    match = re.match(r"(/order )(.*)", text)
    if match:
        return match.group(2).strip()
    return ""


def get_order_dict(update: Update) -> dict:
    """Get a dictionary of the order details from the update."""

    container = {}

    # Just kick off with a createddate
    container["createddate"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # The User object looks like it's a dataclass, so I can probably access
    # its attributes directly
    user = update.effective_user
    container["username"] = user.username
    container["userid"] = user.id

    # Then the Message object has our text and message_id, which we can
    # use to build our order number
    msg = update.message
    container["txt"] = extract_text(msg.text)

    # By combining the user ID and message ID, we can get a unique order ID
    # This should be unique, since TG message IDs are unique per chat
    container["orderid"] = int(str(user.id) + str(msg.message_id))

    return container
