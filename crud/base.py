from sqlalchemy.orm import Session
import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import desc, update
from sqlalchemy.future import select
from db.base_class import Base
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBaseAsync(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        logging.info(f'Obtendo {self.model.__name__} de id={id}')
        stmt = select(self.model).where(
            self.model.id == id
            # Não vou filtrar aqui porque posso querer reativar os casos pelo ID
            # self.model.ativo == True,
            # self.model.exclude == False
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_first_by_filter(
        self, db: AsyncSession, *, order_by: str = "id", filterby: str = "enviado", filter: str
    ) -> Optional[ModelType]:
        logging.info(
            f'Obtendo primeiro {self.model.__name__} cujo {filterby}={filter}')
        stmt = (
            select(self.model)
           
            .order_by(getattr(self.model, order_by))
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, order_by: str = "id"
    ) -> List[ModelType]:
        logging.info(f'Obtendo lista de {self.model.__name__}')
        stmt = (
            select(self.model)
            .order_by(getattr(self.model, order_by))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_multi_filter(
        self, db: AsyncSession, *, order_by: str = "id", filterby: str = "enviado", filter: str
    ) -> List[ModelType]:
        logging.info(
            f'Obtendo lista de {self.model.__name__} cujo {filterby}={filter}')
        stmt = (
            select(self.model)
            .where(
                getattr(self.model, filterby) == filter,
                self.model.ativo == True,
                # self.model.exclude == False
            )
            .order_by(getattr(self.model, order_by))
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_multi_filters(
        self, db: AsyncSession, *, filters: List[Dict[str, Any]]
    ) -> List[ModelType]:
        logging.info(
            f'Obtendo lista de {self.model.__name__} de acordo com os filtros')
        # Iniciando com a base: registros ativos e não excluídos.
        stmt = select(self.model)
        # Definir um mapa de operadores
        operator_map = {
            '=': lambda field, value: field == value,
            '!=': lambda field, value: field != value,
            '<': lambda field, value: field < value,
            '<=': lambda field, value: field <= value,
            '>': lambda field, value: field > value,
            '>=': lambda field, value: field >= value,
            'like': lambda field, value: field.like(value),
            'ilike': lambda field, value: field.ilike(value),
            'in': lambda field, value: field.in_(value),
            'notin': lambda field, value: field.notin_(value),
        }
        for filter_item in filters:
            field_name = filter_item["field"]
            operator = filter_item.get("operator", "=")
            value = filter_item["value"]
            field = getattr(self.model, field_name)
            if operator in operator_map:
                stmt = stmt.filter(operator_map[operator](field, value))
            else:
                raise ValueError(f"Operador desconhecido: {operator}")
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_last_by_filters(
        self,
        db: AsyncSession,
        *,
        filters: Dict[str, Dict[str, Union[str, int]]],
    ) -> Optional[ModelType]:
        logging.info(
            f'Obtendo último registro de {self.model.__name__} de acordo com os filtros')

        stmt = select(self.model)

        for filter_name, filter_data in filters.items():
            operator = filter_data['operator']
            filter_value = filter_data['value']

            column = getattr(self.model, filter_name)

            if operator == '>':
                stmt = stmt.where(column > filter_value)
            elif operator == '<':
                stmt = stmt.where(column < filter_value)
            elif operator == '>=':
                stmt = stmt.where(column >= filter_value)
            elif operator == '<=':
                stmt = stmt.where(column <= filter_value)
            elif operator == '==':
                stmt = stmt.where(column == filter_value)
            elif operator == '!=':
                stmt = stmt.where(column != filter_value)
            elif operator == 'like':
                stmt = stmt.where(column.like(f"%{filter_value}%"))
            elif operator == 'is_null':
                stmt = stmt.where(column.is_(None))

        stmt = stmt.order_by(desc(self.model.id)).limit(1)

        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        logging.info(f'Criando objeto em {self.model.__name__}')
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    def create_multi_bulk(self, db: Session, *, obj_in: List[CreateSchemaType]) -> List[ModelType]:
        db_objs = [self.model(**jsonable_encoder(item)) for item in obj_in]
        db.bulk_save_objects(db_objs)
        db.commit()
        print('multiplos...')

        return {'msg': 'Chamados inseridos com sucesso'}

    async def create_multi(self, db: AsyncSession, *, obj_in: List[CreateSchemaType]) -> Any:
        logging.info(f'Criando lista de objetos {self.model.__name__}')
        db_objs = [self.model(**jsonable_encoder(item)) for item in obj_in]
        db.add_all(db_objs)
        db.commit()
        for obj in db_objs:
            db.refresh(obj)
        return {'msg': 'Chamados inseridos com sucesso'}

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        logging.info(f'Atualizando o objeto de {self.model.__name__}')
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_multi(
        self, db: AsyncSession, *, objs_in: List[Union[UpdateSchemaType, Dict[str, Any]]], filtro: str
    ) -> List[ModelType]:
        logging.info(f'Atualizando lista de objetos {self.model.__name__}')
        updated_objs = []
        for obj_in in objs_in:
            obj_data = jsonable_encoder(obj_in) if isinstance(
                obj_in, BaseModel) else obj_in
            filter_args = {filtro: obj_data[filtro]}
            # Selecionando apenas registros ativos e não excluídos
            stmt = select(self.model).filter_by(**filter_args).filter(
                self.model.ativo == True,
                # self.model.exclude == False
            )
            result = await db.execute(stmt)
            db_obj = result.scalars().first()
            if db_obj:
                await db.execute(
                    update(self.model)
                    .filter_by(**filter_args)
                    .filter(
                        self.model.ativo == True,
                        self.model.exclude == False
                    )
                    .values(**obj_data)
                )
                await db.commit()
                await db.refresh(db_obj)
                updated_objs.append(db_obj)
        return updated_objs

    async def update_many(
        self, db: AsyncSession, *, filter_args: Dict[str, Any], update_data: Dict[str, Any]
    ) -> int:
        """
        Atualiza em massa os registros do modelo que atendem aos filtros especificados.
        Retorna o número de registros atualizados.
        """
        logging.info(
            f'Atualizando vários objetos de {self.model.__name__} com filtro {filter_args}')
        stmt = update(self.model).filter_by(
            **filter_args).values(**update_data)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        logging.info(f'Removendo objeto {self.model.__name__} de id={id}')
        db_obj = await self.get(db=db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj
