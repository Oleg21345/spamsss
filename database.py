from BaseModel import Base
from sqlalchemy.orm import mapped_column, Mapped
import datetime


class TelegramList(Base):
    __tablename__ = "list"

    id: Mapped[int] = mapped_column(primary_key=True)
    number_phone: Mapped[str]

    def __str__(self):
        return f"{self.number_phone}"


class ChackedTelegramList(Base):
    __tablename__ = "chacked_list"

    id: Mapped[int] = mapped_column(primary_key=True)
    number_phone: Mapped[str]
    sent_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CheckedTelegramList(number_phone={self.number_phone}, sent_at={self.sent_at})>"

