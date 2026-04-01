"""MYSQL db components."""

# NOTE sqlite3 doesn't support datetime objects but it will take
# ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS")

from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import String


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM"""


class Order(Base):
    """Order table"""

    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    createddate: Mapped[str] = mapped_column(String(26))
    username: Mapped[str]
    userid: Mapped[int]
    txt: Mapped[str] = mapped_column(String(85))  # Arbitrary n characters
    claimed_by: Mapped[Optional[str]]
    claimeddate: Mapped[Optional[str]] = mapped_column(String(26))

    def __repr__(self) -> str:
        return (
            f"Order(id={self.id!r}"
            f", createddate={self.createddate!r}"
            f", username={self.username!r}"
            f", userid={self.userid!r}"
            f", claimed_by={self.claimed_by!r}"
            f", claimeddate={self.claimeddate!r})"
        )


class Admin(Base):
    """Admin table"""

    __tablename__ = "admin"

    userid: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self) -> str:
        return f"Admin(userid={self.userid!r})"
