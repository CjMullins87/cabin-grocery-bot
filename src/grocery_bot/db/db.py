"""MYSQL db components."""

import os
from os.path import dirname
from pathlib import Path
import sqlite3

DB_PATH = Path(os.path.abspath(dirname(__file__))) / "sqlite.db"
