"""Main program loop."""

import logging
from grocery_bot.bot import bot_setup


def main() -> None:
    """Core loop."""

    # Enable debug logging w/ basic config
    logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        level=logging.DEBUG,
    )

    # Per docs, recommend setting higher level warnings to avoid
    # floods of Requests
    logging.getLogger("httpx").setLevel(logging.WARNING)

    bot_setup(is_demo=True)
    return


if __name__ == "__main__":
    main()
