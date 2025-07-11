from typing import Optional
from pydantic import BaseModel, Field


class CarBase(BaseModel):
    modelo : str
    nome : str
    cor : str
    marca: str
    versao: str
    ano: int 


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    nome: Optional[str] = None
    modelo: Optional[str] = None
    cor: Optional[str] = None


class CarInDbBase(CarBase):
    id: int
    
class Config:
        orm_mode = True

class Car(CarInDbBase):
    pass

class CarRequest(CarBase):
     pass