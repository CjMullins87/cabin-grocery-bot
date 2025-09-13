"""Helper functions/handlers."""

import re
from datetime import datetime
from telegram import Update


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
