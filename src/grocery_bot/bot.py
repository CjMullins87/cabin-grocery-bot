"""Telegram bot core components."""

from ast import parse
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from grocery_bot.utils import get_order_dict, get_token

logger = logging.getLogger(__name__)


# Define command handlers. Looks like these should always expect an Update and
# Context argument
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_txt = (
        "Right now, I know these commands:\n\n"
        + "`/help`     This displays the text you're reading now\n"
        + "`/order`    Use this command to request something"
    )
    await update.message.reply_text(help_txt, parse_mode="MarkdownV2")


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

    # Fetch the token the kickoff the bot
    token = get_token()
    logger.debug("Kicking off bot:")
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("order", order))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()
