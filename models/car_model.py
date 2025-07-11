from sqlalchemy import Column, Integer, String
from db.base_class import Base


class Car(Base):
    __tablename__ = 'Carrinhos'
    
    id = Column(Integer, primary_key=True, index=True)
    modelo = Column(String(255), index=True)
    nome = Column(String(255), nullable=False)
    cor  = Column(String(255), nullable=False)
    marca = Column(String(255), nullable=False)
    versao = Column(String(255), nullable=False)
    ano = Column(Integer, nullable=False)
