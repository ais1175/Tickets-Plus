"""The main bot file. Start the bot."""
import logging

from discord.ext import commands
from sqlalchemy.ext.asyncio import create_async_engine

from tickets_plus.bot import TicketsPlus
from tickets_plus.database.models import Base
from tickets_plus.database.statvars import MiniConfig, Secret, handler, intents


async def start_bot():
    """Sets up the bot and starts it"""
    stat_data = MiniConfig()

    # Set up logging
    dt_fmr = "%Y-%m-%d %H:%M:%S"
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s", dt_fmr)
    )

    # Set up discord.py logging
    dscrd_logger = logging.getLogger("discord")
    dscrd_logger.setLevel(logging.INFO)
    dscrd_logger.addHandler(handler)

    # Set up sqlalchemy logging
    sql_logger = logging.getLogger("sqlalchemy.engine")
    sql_logger.setLevel(logging.INFO)
    sql_logger.addHandler(handler)

    # Set up bot logging
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(handler)

    engine = create_async_engine(stat_data.get_url())
    bot = TicketsPlus(
        db_engine=engine, intents=intents, command_prefix=commands.when_mentioned
    )
    logging.info("Engine created. Ensuring tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Tables ensured. Starting bot...")
    try:
        await bot.start(Secret().token)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected. Shutting down...")
        # We print this because there was a keyboard interrupt.
        print("Keyboard interrupt detected. Shutting down...")
        await bot.close()
    except SystemExit as exc:
        logging.info("System exit code: %s detected. Closing bot...", exc.code)
        await bot.close()
    else:
        logging.info("Bot shutdown gracefully.")
    logging.info("Bot shutdown complete.")
