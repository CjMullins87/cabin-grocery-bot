"""MYSQL db components."""

import os
from os.path import dirname
from pathlib import Path
from threading import RLock

DB_PATH = Path(os.path.abspath(dirname(__file__))) / "sqlite.db"


class DBManager:
    """Database manager for the bot."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        """Initialize the manager."""

        self.db_path = db_path
        self._lock = RLock()
