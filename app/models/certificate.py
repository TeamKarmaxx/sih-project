from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.connection import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("training_modules.id"), nullable=False)

    certificate_number = Column(String, unique=True, nullable=False)