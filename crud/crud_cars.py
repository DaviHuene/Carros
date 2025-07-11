from crud.base import CRUDBaseAsync
from models.car_model import Car
from schemas.car_schema import  CarCreate, CarUpdate


class CRUDItem(CRUDBaseAsync[ Car, CarCreate, CarUpdate]):
    pass


crud_car = CRUDItem(Car)
