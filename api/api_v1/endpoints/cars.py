from typing import Any, List, Optional
import logging


from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from core.request import RequestClient
from api import deps
from crud.crud_cars import crud_car
from schemas.car_schema import Car, CarCreate, CarRequest, CarUpdate

router = APIRouter()
logger = logging.getLogger(__name__)




@router.post("/", response_model=Car)
async def create_car(
        *,
        db: AsyncSession = Depends(deps.get_db_psql),
        car_in: CarCreate,
) -> Any:
    """
    Create new car.
    """
    car = await crud_car.create(db=db, obj_in=car_in)
    return car

@router.put("/{id}", response_model=Car)
async def update_car(
        id: int,
        update_data: CarUpdate,
        db: AsyncSession = Depends(deps.get_db_psql),
        
) -> Any:
    """
    Update an existing car.
    """
    obj = await crud_car.get(db=db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="Car not found")
    
    
    car = await crud_car.update(db=db, db_obj=obj, obj_in=update_data)
    return car

@router.delete(path="/{id}", response_model=Car)
async def delete_car(
        *,
        db: AsyncSession = Depends(deps.get_db_psql),
        id: int,
) -> Any:
    """
    Delete an item.
    """
    car = crud_car.get(db=db, id=id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    car = await crud_car.remove(db=db, id=id)
    return car


@router.get(path="/{id}",response_model=CarRequest)
async def car_request( 
        id: int,
        db: AsyncSession = Depends(deps.get_db_psql),
       
) -> Any:
    """
    Retrieve cars.
    """
    logger.info(f"Consultando carro - filtro por id: {id}")
    return await crud_car.get(db=db, id=id)


@router.get("/", response_model=List[Car])
async def read_cars(
        db: AsyncSession = Depends(deps.get_db_psql),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    Retrieve cars.
    """
    logger.info("Consultando carros")
    return await crud_car.get_multi(db=db, skip=skip, limit=limit)
