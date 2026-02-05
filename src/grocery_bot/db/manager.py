"""DB manager"""

import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from threading import Lock


from grocery_bot.config import DB_PATH

logger = logging.getLogger(__name__)


class DBManager:
    """Manages the SQLite database"""

    def __init__(self):

        # Create the engine
        # NOTE we'll use the built-in timeout to handle queueing
        self.engine = create_engine(
            f"sqlite+pysqlite:///{DB_PATH}", connect_args={"timeout": 15}
        )

        # Set up a session factory that binds the engine
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def _get_session(self):
        """Retrieve a session object and define behaviors for the transaction"""

        session = self.Session()

        # Generally, we want the session to pop out and execute, then commit
        try:
            yield session
            session.commit()

        # If something goes wrong, raise
        except Exception:
            session.rollback()
            raise

        # Finally close
        finally:
            session.close()
