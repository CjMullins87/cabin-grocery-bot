"""Telegram bot core components."""

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from grocery_bot.utils import *


# Define command handlers. Looks like these should always expect an Update and
# Context argument
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("That's gay!")


async def order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gets the grocery item request and preps it for the cache and db."""
    order = get_order_dict(update)

    # Some handling here to make sure that the order is reasonably shaped (EG please
    # do not send me the script of THE ROOM as a grocery item)
    if not len(order["txt"]) <= 85:
        await update.message.reply_text("Please keep your request under 85 characters.")
    else:
        await update.message.reply_text(f"'{order['txt']}' successfully requested!")
        # TEMP debugging info TODO remove later
        await update.message.reply_text(
            f"```\n{str(order)}```", parse_mode="MarkdownV2"
        )


def bot_core_setup() -> None:
    """Set up the bot core components."""
    # Create the Application and pass it the token.
    application = Application.builder().token(get_token()).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("order", order))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()
