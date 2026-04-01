"""DB manager"""

import logging
from contextlib import contextmanager
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from grocery_bot.config import DB_PATH
from grocery_bot.db.schema import Base

logger = logging.getLogger(__name__)


class DBManager:
    """Manages the SQLite database"""

    def __init__(self, connect_args: dict = None, demo: bool = False):

        # Engine lives on instance, but we'll connect behind an explicit call
        self.engine: Engine = None
        self.demo: bool = demo

        # If no connect_args are specified, we'll default to a 15s timeout
        # Otherwise, whatever is given should be accepted
        if not connect_args:
            logger.debug("Default connect args")
            self.connect_args = {"timeout": 15}
        else:
            logger.debug("Other connect args: %s", connect_args)
            self.connect_args = connect_args

    @contextmanager
    def get_session(self) -> None:
        """Retrieve a session object and define behaviors for the transaction"""

        # Use sessionmaker to make sure we're always calling directly to
        # a new session
        SessionFactory = sessionmaker(bind=self.engine)
        session = SessionFactory()

        # Generally, we want the session to pop out and execute, then commit
        try:
            yield session
            session.commit()

        # If something goes wrong, raise and rollback
        except Exception:
            session.rollback()
            raise

        # Finally close
        finally:
            session.close()

    def connect(self) -> None:
        """Connects to our DB"""
        # NOTE if the DB does not exist, this connect method will create it

        try:
            logger.debug("Connecting DB")
            if self.demo:
                # If we're running a demo, we'll load the database in RAM only
                logger.debug("Demo mode, DB in RAM only")
                self.engine = create_engine(
                    "sqlite+pysqlite:///:memory:",
                    connect_args=self.connect_args,
                    echo=True,
                )
            else:
                # Otherwise, we'll want to load the db from the configured path
                self.engine = create_engine(
                    f"sqlite+pysqlite:///{DB_PATH}",
                    connect_args=self.connect_args,
                    echo=True,
                )

            # We'll also want to use our Metadata to populate the tables
            # if they don't already exist
            Base.metadata.create_all(self.engine)

        except Exception as e:
            # No idea what we'll encounter, so, just raise it
            raise e
