from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import JSON

from database import Base


class Odontograma(Base):

    __tablename__ = "odontogramas"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    cliente_id = Column(
        Integer,
        unique=True,
        nullable=False
    )

    odontograma = Column(
        JSON,
        nullable=False
    )