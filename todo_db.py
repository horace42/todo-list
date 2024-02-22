"""
Database classes and functions
"""
from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, Integer, Boolean
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class List(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    tasks: Mapped["Task"] = relationship(back_populates="list")


class Task(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    list_id = mapped_column(ForeignKey("list.id"), nullable=False)

    list: Mapped["List"] = relationship(back_populates="tasks")


def add_list(form_data):
    """
    Insert new list in the db
    :param form_data: Dictionary from web form
    :return: None
    """
    stmt = db.select(List).where(List.name == form_data["name"])
    result = db.session.execute(stmt).first()
    if result:
        print(f"{form_data["name"]} already exists")
    else:
        new_list = List(name=form_data["name"])
        db.session.add(new_list)
        db.session.commit()


def add_task(form_data):
    """
    Insert new task in the db
    :param form_data: Dictionary from web form
    :return:
    """
    new_task = Task(name=form_data["name"],
                    deadline=form_data["deadline"],
                    completed=False,
                    list_id=form_data["list_id"])
    db.session.add(new_task)
    db.session.commit()
