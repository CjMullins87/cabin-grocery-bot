"""Telegram bot core components."""

from ast import parse
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from grocery_bot.db.manager import DBManager
from grocery_bot.db.schema import Order, Admin
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

    # Fetch the db manager from cache
    db_manager: DBManager = context.bot_data["db_manager"]

    # Prep the order dict
    order_dict = get_order_dict(update)

    # Some handling here to make sure that the order is reasonably shaped (EG please
    # do not send me the script of THE ROOM as a grocery item)
    if not len(order_dict["txt"]) <= 85:
        await update.message.reply_text("Please keep your request under 85 characters.")
        return
    else:
        try:
            # Write the data to the DB
            new_order = Order(
                id=order_dict["id"],
                createddate=order_dict["createddate"],
                username=order_dict["username"],
                userid=order_dict["userid"],
                txt=order_dict["txt"],
            )
            with db_manager.get_session() as session:
                session.add(new_order)

            # Send a confirmation
            reply_text = (
                "Successfully requested:\n"
                f"```Order\nOrder #: {order_dict['id']}\n'{order_dict['txt']}'```"
            )

            await update.message.reply_text(reply_text, parse_mode="MarkdownV2")
            return

        except Exception as e:
            logger.error("Failed to write to DB: %s", e)
            await update.message.reply_text(
                "Sorry, something went wrong saving your order"
            )
            return


def bot_core_setup() -> None:
    """Set up the bot core components."""
    # DB setup
    db_manager = DBManager(demo=True)
    db_manager.connect()

    # Kick off the bot by fetching the token and caching the db_manager
    # in bot_data
    logger.debug("Kicking off bot:")
    application = Application.builder().token(get_token()).build()
    application.bot_data["db_manager"] = db_manager

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("order", order))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()
