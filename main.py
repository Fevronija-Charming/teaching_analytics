from pydantic import BaseModel, Field, ValidationError
import asyncio
import os
from colorama import *
from dotenv import find_dotenv, load_dotenv
from faststream.rabbit.fastapi import RabbitBroker, RabbitRouter
#выключаем зайца
#router=RabbitRouter(host="localhost", port=5672)
from fastapi import FastAPI
from fastapi import HTTPException
app = FastAPI()
import uvicorn
load_dotenv(find_dotenv())
from typing import Annotated
from fastapi import Depends
#работа с базой данных
from sqlalchemy import  DateTime, String, Float, Column, Integer, func, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
engine = create_async_engine(os.getenv("DBURL"),echo=True,max_overflow=5,pool_size=5)
session_factory = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)
class Base(DeclarativeBase):
    pass
class Ученики(Base):
    __tablename__="Ученики"
    id: Mapped[int]=mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Фамилия: Mapped[str]=mapped_column(String(128), nullable=False)
    Имя: Mapped[str]=mapped_column(String(128), nullable=False)
class Предметы(Base):
    __tablename__="Предметы"
    id: Mapped[int]=mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Название_Предмета: Mapped[str]=mapped_column(String(32), nullable=False)
class Даты(Base):
    __tablename__="Даты"
    id: Mapped[int]=mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Дата: Mapped[str]=mapped_column(String(128), nullable=False)
class Ступени_Обучения(Base):
    __tablename__ = "Ступени_Обучения"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Ступень_Обучения: Mapped[str] = mapped_column(String(128), nullable=False)
class Уроки(Base):
    __tablename__ = "Уроки"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Имя_Преподавателя: Mapped[str] = mapped_column(String(128), nullable=False)
    Фамилия_Преподавателя: Mapped[str] = mapped_column(String(128), nullable=False)
    Предмет_Обучения: Mapped[str] = mapped_column(String(128), nullable=False)
    Имя_Ученика: Mapped[str] = mapped_column(String(128), nullable=False)
    Фамилия_Ученика: Mapped[str] = mapped_column(String(128), nullable=False)
    Ступень_Обучения: Mapped[str] = mapped_column(String(128), nullable=False)
    Дата_Проведения: Mapped[str] = mapped_column(String(128), nullable=False)
    Время_Начала: Mapped[str] = mapped_column(String(128), nullable=False)
    Длительность_Занятия_Мин: Mapped[int]
    Стоимость_Занятия_Центов: Mapped[int]
    Что_Делали_На_Уроке: Mapped[str] = mapped_column(Text, nullable=False)
    Задание_На_Дом: Mapped[str] = mapped_column(String(128), nullable=False)
    Примечание: Mapped[str] = mapped_column(Text, nullable=False)
class Urok_Schema(BaseModel):
    Имя_Преподавателя: str = Field(min_length=5, max_length=25)
    Фамилия_Преподавателя: str = Field(min_length=5, max_length=25)
    Предмет_Обучения: str = Field(min_length=5, max_length=25)
    Имя_Ученика: str= Field(min_length=5, max_length=25)
    Фамилия_Ученика: str= Field(min_length=5, max_length=25)
    Ступень_Обучения: str= Field(min_length=5, max_length=25)
    Дата_Проведения: str= Field(min_length=5, max_length=25)
    Время_Начала: str= Field(min_length=5, max_length=25)
    Длительность_Занятия_Мин: int
    Стоимость_Занятия_Центов: int
    Что_Делали_На_Уроке: str= Field(min_length=5, max_length=2000)
    Задание_На_Дом: str= Field(min_length=5, max_length=128)
    Примечание: str= Field(min_length=5, max_length=2000)
@app.post("/urok", summary="Зарегестрировать урок",tags=["УРОКИ"])
async def create_urok(urok: Annotated[Urok_Schema, Depends()]):
    try:
        urok_eksemp = Уроки(Имя_Преподавателя=urok.Имя_Преподавателя,Фамилия_Преподавателя=urok.Фамилия_Преподавателя,
                            Предмет_Обучения=urok.Предмет_Обучения,Имя_Ученика=urok.Имя_Ученика,
                            Фамилия_Ученика=urok.Фамилия_Ученика,Ступень_Обучения=urok.Ступень_Обучения,
                            Дата_Проведения=urok.Дата_Проведения, Время_Начала=urok.Время_Начала,
                            Длительность_Занятия_Мин=urok.Длительность_Занятия_Мин,
                            Стоимость_Занятия_Центов=urok.Стоимость_Занятия_Центов,
                            Что_Делали_На_Уроке=urok.Что_Делали_На_Уроке,Задание_На_Дом=urok.Задание_На_Дом,
                            Примечание=urok.Примечание)
        session = session_factory()
        session.add(urok_eksemp)
        await session.commit()
        await session.close()
        try:
            #выключаем зайца
            #router.broker.publish(message="Добавлен новый урок", queue="UROKI")
            #await router.broker.publish(message=f"{urok}", queue="UROKI")
            return urok_eksemp
        except:
            raise HTTPException(status_code=500, detail="Проблема с брокером")
    except:
        raise HTTPException(status_code=500, detail="Проблема с базой данных")
@app.get("/zapr", summary="Посчитать зарплату",tags=["ЗАРПЛАТА"])
async def get_zapr():
    summa=0
    query = select(Уроки.Стоимость_Занятия_Центов)
    session = session_factory()
    result = await session.execute(query)
    zapka = result.scalars().all()
    for zapka in zapka:
        summa = summa + zapka
    return summa/100
@app.get("/chasy", summary="Посчитать часы",tags=["ЧАСЫ"])
async def get_chasy():
    chasy=0
    query = select(Уроки.Длительность_Занятия_Мин)
    session = session_factory()
    result = await session.execute(query)
    dlitelnost = result.scalars().all()
    for element in dlitelnost:
        chasy = chasy + element
    return chasy/60
# пока выключил, Хероку сам создаст базу
async def kostily_BD():
    # создать ДБ
    import psycopg2 as ps
    from psycopg2.errors import DuplicateDatabase as Oshibka
    from psycopg2 import sql
    connection = None
    try:
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(Back.GREEN + Fore.BLACK + Style.BRIGHT + 'Создать базу Данных')
        databasename = os.getenv('DATABASENAME')
        connection = ps.connect(host="localhost", database="postgres", user="postgres", password=os.getenv("DBPASSWORD"),
                                port="5432")
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(databasename)))
        cursor.close()
        print(Back.LIGHTGREEN_EX + Fore.BLACK + Style.BRIGHT + 'БД успешно создана, моя Госпожа')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    except Oshibka:
        print('Такая БД уже есть, моя Госпожа!!!')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    finally:
        if connection:
            connection.close()
        if cursor:
            cursor.close()
async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
# пока выключил этот функционал не нужен
async def create_predmety():
    predmet_eksempjar1=Предметы(Название_Предмета="Математика")
    session=session_factory()
    session.add(predmet_eksempjar1)
    await session.commit()
    await session.close()
    predmet_eksempjar2 = Предметы(Название_Предмета="Физика")
    session = session_factory()
    session.add(predmet_eksempjar2)
    await session.commit()
    await session.close()
    predmet_eksempjar3 = Предметы(Название_Предмета="Биология")
    session = session_factory()
    session.add(predmet_eksempjar3)
    await session.commit()
    await session.close()
    predmet_eksempjar4 = Предметы(Название_Предмета="Химия")
    session = session_factory()
    session.add(predmet_eksempjar4)
    await session.commit()
    await session.close()
    predmet_eksempjar5=Предметы(Название_Предмета="Английский")
    session = session_factory()
    session.add(predmet_eksempjar5)
    await session.commit()
    await session.close()
async def create_stupeni():
    stupen_eksemprjar1=Ступени_Обучения(Ступень_Обучения="7-8-9 классы")
    session = session_factory()
    session.add(stupen_eksemprjar1)
    await session.commit()
    await session.close()
    stupen_eksemprjar2 = Ступени_Обучения(Ступень_Обучения="5-6-7 классы")
    session = session_factory()
    session.add(stupen_eksemprjar2)
    await session.commit()
    await session.close()
    stupen_eksemprjar3 = Ступени_Обучения(Ступень_Обучения="Гимназия-Техникум")
    session = session_factory()
    session.add(stupen_eksemprjar3)
    await session.commit()
    await session.close()
    stupen_eksemprjar4 = Ступени_Обучения(Ступень_Обучения="Студенты_Абитурьенты")
    session = session_factory()
    session.add(stupen_eksemprjar4)
    await session.commit()
    await session.close()
    stupen_eksemprjar5 = Ступени_Обучения(Ступень_Обучения="1-2-3-4 классы")
    session = session_factory()
    session.add(stupen_eksemprjar5)
    await session.commit()
    await session.close()

async def main():
    init(autoreset=True)
    #await kostily_BD()
    await create_tables()
    uvicorn.run("main:app", reload=True, port=8000)
    #создать предметы
    #await create_predmety()
    #await create_stupeni()
app.include_router(router)
if __name__ == "__main__":
    asyncio.run(main())
