from database.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP
from uuid import UUID, uuid4
from datetime import datetime
from auth.models import User


class Game(Base):
    __tablename__ = 'games'

    id: UUID = Column(UUID, primary_key=True, default=uuid4)
    name: str = Column(String, nullable=False)
    create_at: datetime = Column(TIMESTAMP, default=datetime)
    first_palyer_id: UUID = Column(UUID, ForeignKey('users.id'))
    second_plater_id: UUID = Column(UUID, ForeignKey('users.id'))
    winner_id: UUID = Column(UUID, ForeignKey('users.id'))