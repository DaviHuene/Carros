from logging import config
import os
import logging
import traceback
from typing import Any, List, Optional
from tempfile import NamedTemporaryFile

import pandas as pd
import pdfkit
from jinja2 import Template
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps
from crud.crud_cars import crud_car
from schemas.car_schema import Car, CarCreate, CarRequest, CarUpdate
from sqlalchemy import select


router = APIRouter()
logger = logging.getLogger(__name__)

path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)



@router.post("/create", response_model=Car)
async def create_car(
        car_in: CarCreate,
        db: AsyncSession = Depends(deps.get_db_psql),
        
) -> Any:
    """
    Create new car.
    """
    car = await crud_car.create(db=db, obj_in=car_in)
    return car




@router.post("/create-mult", response_model=dict)
async def create_multi_car(
    car_in: list[CarCreate],
    db: AsyncSession = Depends(deps.get_db_psql),
) -> dict:
    result = await crud_car.create_multi(db=db, obj_in=car_in)
    return result



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

@router.delete("/del{id}", response_model=Car)
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


@router.get("/{id}",response_model=CarRequest)
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




@router.post("/import-excel", response_model=dict)
async def import_excel(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(deps.get_db_psql)
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser .xlsx")

    try:
        df = pd.read_excel(file.file)
        print("Preview do DF:")
        print(df.head())
        print("Colunas:", df.columns)
                # Valida se colunas necessárias existem
        required_columns = {"modelo", "nome", "cor", "marca", "versao", "ano"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail=f"Colunas esperadas: {required_columns}")
     
        cars_data: List[CarCreate] = [
            CarCreate(**row.to_dict()) for _, row in df.iterrows()
        ]
        
        result = await crud_car.create_multi(db=db, obj_in=cars_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o Excel: {str(e)}")
    
  
@router.get("/export-excel", response_class=FileResponse)
async def export_excel(db: AsyncSession = Depends(deps.get_db_psql)):
    cars = await crud_car.get_all(db)
    if not cars:
        raise HTTPException(status_code=404, detail="Nenhum carro encontrado.")

    df = pd.DataFrame([car.__dict__ for car in cars])
    df = df.drop(columns=['_sa_instance_state'], errors='ignore')

    with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        df.to_excel(tmp.name, index=False)
        return FileResponse(tmp.name, filename="carros.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.get("/export-pdf", response_class=FileResponse)
async def export_pdf(db: AsyncSession = Depends(deps.get_db_psql)):
    cars = await crud_car.get_all(db)
    if not cars:
        raise HTTPException(status_code=404, detail="Nenhum carro encontrado.")

    html = """
    <html>
    <head><style>table, th, td { border: 1px solid black; border-collapse: collapse; padding: 4px; }</style></head>
    <body>
        <h2>Relatório de Carros</h2>
        <table>
            <tr><th>Modelo</th><th>Nome</th><th>Cor</th><th>Marca</th><th>Versão</th><th>Ano</th></tr>
            %s
        </table>
    </body>
    </html>
    """ % "".join([
        f"<tr><td>{c.modelo}</td><td>{c.nome}</td><td>{c.cor}</td><td>{c.marca}</td><td>{c.versao}</td><td>{c.ano}</td></tr>"
        for c in cars
    ])

    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdfkit.from_string(html, tmp.name, configuration=config)
        return FileResponse(tmp.name, filename="carros.pdf", media_type="application/pdf")