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
    nome : str
    modelo : str
    cor : str


class CarInDbBase(CarBase):
    id: int


class Car(CarInDbBase):
    pass

class CarRequest(CarBase):
     modelo:str