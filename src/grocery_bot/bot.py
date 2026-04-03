"""Telegram bot core components."""

from ast import parse
from email import message
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from tomlkit import date
from zmq import Context

from grocery_bot.db.manager import DBManager
from grocery_bot.db.schema import Order, Admin
from grocery_bot.utils import *

logger = logging.getLogger(__name__)


# Define command handlers. Looks like these should always expect an Update and
# Context argument
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_txt = (
        "Right now, I know these commands:\n\n"
        + "`/help`     This displays the text you're reading now\n"
        + "`/order`    Use this command to request something\n"
        + "`/cancel`   Cancel a request that you placed"
    )
    await update.message.reply_text(help_txt, parse_mode="MarkdownV2")


async def order_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allow users to cancel requests if they are the request owner or an Admin"""

    # Fetch the db manager
    db_manager = context.bot_data["db_manager"]

    # Enforce a standard here -- people should /reply to their order confirmation
    # This should be easier for our users, and look cooler, honestly, from an
    # interface perspective
    reply = update.message.reply_to_message
    if not reply or not reply.from_user.id == context.bot.id:
        logger.debug("Command not valid:")
        logger.debug("is_reply: %s", bool(reply))
        logger.debug("from_user.id: %s", context.bot.id)
        await update.message.reply_text(
            "To cancel a request, please reply to your confirmation with the `/cancel` command",
            parse_mode="MarkdownV2",
        )
        return

    # If the message is a reply, we should attempt to get info out of it
    logger.debug("Message is valid reply")
    reply_txt = update.message.reply_to_message.text
    logger.debug("Reply text:\n%s", reply_txt)

    # Try to extract an orderID and execute the db update
    try:
        orderid = extract_orderid_from_text(reply_txt)
        userid = update.effective_user.id

        # Basically, only allow execution if the requester is an admin or the
        # request owner
        if is_admin(userid, db_manager) or is_request_owner(
            userid, orderid, db_manager
        ):
            logger.debug("Permissions OK")
            with db_manager.get_session() as session:
                _order: Order = session.get(Order, orderid)
                if _order:
                    logger.debug("Cancelling order")
                    _order.canceleddate = datetime.now().isoformat()
                    _order.canceledbyid = userid
                    _order.canceledbyname = update.effective_user.username
                    await update.message.reply_text("Successfully canceled")
                    return

                logger.warning("Order not found")
        else:
            logger.warning("Permissions NOT OK")
            await update.message.reply_text(
                "Sorry, you don't have the right permissions"
            )
            return
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Sorry, I wasn't able to cancel this request")
        return


def bot_setup(is_demo: bool = False) -> None:
    """Set up the bot core components."""
    # DB setup
    db_manager = DBManager(demo=is_demo)
    db_manager.connect()

    # Kick off the bot by fetching the token and caching the db_manager
    # in bot_data
    logger.debug("Kicking off bot:")
    application = Application.builder().token(get_token()).build()
    application.bot_data["db_manager"] = db_manager

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("order", order_new))
    application.add_handler(CommandHandler("cancel", cancel_order))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()
