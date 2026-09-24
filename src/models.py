from __future__ import annotations #Se usa en versiones anteriores a la 3.14 para utilizar clasess que se definen mas abajo en el archivo. Por ej el User no podria tener list[Posts] porque POSTS no esta definido a esa altura del codigo

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
#SIEMPRE DEFINIR DE MANERA CORRECTA LAS RELACIONES EN LA DB DE ENTRADA Y NO ESPERAR A QUE SE PRESENTEN. En este caso la relacion 1:N entre usuarios y posts

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,
    )

    posts: Mapped[list[Post]] = relationship(back_populates="author", cascade="all, delete-orphan") #This creates 1:N relationship

    #Python code
    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC), #Utiliza el datetime.now al momento de crear el post. Sin el lambda utilizaria el tiempo al levantar el servidor.
    )

    author: Mapped[User] = relationship(back_populates="posts")