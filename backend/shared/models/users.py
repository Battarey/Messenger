import uuid
from datetime import datetime
from typing import ClassVar

from sqlalchemy import Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base


class Account(Base):
    """Модель системных данных учетных записей пользователей."""

    __tablename__: ClassVar[str] = "accounts"
    __table_args__: ClassVar[dict] = {"schema": "users"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Уникальный идентификатор аккаунта",
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Основной email пользователя",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Статус активности аккаунта",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', NOW())"),
        nullable=False,
        comment="Дата и время регистрации",
    )

    # Отношения
    profile: Mapped["Profile"] = relationship(
        "Profile",
        back_populates="account",
        uselist=False,
        cascade="all, delete-orphan",
    )
    ui_settings: Mapped["UISettings"] = relationship(
        "UISettings",
        back_populates="account",
        uselist=False,
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="account",
        cascade="all, delete-orphan",
    )


class Profile(Base):
    """Модель публичного профиля пользователя."""

    __tablename__: ClassVar[str] = "profiles"
    __table_args__: ClassVar[dict] = {"schema": "users"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.accounts.id", ondelete="CASCADE"),
        primary_key=True,
        comment="ID профиля, совпадает с ID аккаунта",
    )
    username: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Уникальный логин пользователя",
    )
    display_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment="Отображаемое имя (публичное)",
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment="Ссылка на аватар",
    )
    bio: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Описание профиля (до 200 символов)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', NOW())"),
        onupdate=text("TIMEZONE('utc', NOW())"),
        nullable=False,
        comment="Дата и время последнего обновления профиля",
    )

    # Отношения
    account: Mapped["Account"] = relationship("Account", back_populates="profile")


class UISettings(Base):
    """Модель настроек интерфейса пользователя."""

    __tablename__: ClassVar[str] = "ui_settings"
    __table_args__: ClassVar[dict] = {"schema": "users"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.accounts.id", ondelete="CASCADE"),
        primary_key=True,
        comment="ID пользователя, владельца настроек",
    )
    theme: Mapped[str] = mapped_column(
        String,
        default="dark",
        server_default="dark",
        nullable=False,
        comment="Выбранная тема оформления (dark/light)",
    )
    language: Mapped[str] = mapped_column(
        String,
        default="ru",
        server_default="ru",
        nullable=False,
        comment="Язык интерфейса (ru/en)",
    )

    # Отношения
    account: Mapped["Account"] = relationship("Account", back_populates="ui_settings")


class Session(Base):
    """Модель активных сессий устройств пользователя."""

    __tablename__: ClassVar[str] = "sessions"
    __table_args__: ClassVar[dict] = {"schema": "users"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Уникальный ID сессии",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.accounts.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID владельца сессии",
    )
    refresh_token_hash: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Хэш Refresh-токена",
    )
    device_info: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment="Информация об устройстве",
    )
    ip_address: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment="IP-адрес сессии",
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', NOW())"),
        nullable=False,
        comment="Время последней активности",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', NOW())"),
        nullable=False,
        comment="Дата создания сессии",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Дата истечения сессии",
    )

    # Отношения
    account: Mapped["Account"] = relationship("Account", back_populates="sessions")
