from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class Subscriber(Base):
    __tablename__ = "subscribers"

    id: Mapped[int] = mapped_column(
        primary_key=True, unique=True, nullable=False, autoincrement=True
    )
    telegram_username: Mapped[str] = mapped_column(unique=True)
    telegram_id: Mapped[str] = mapped_column(unique=True)
