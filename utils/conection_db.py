import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import declarative_base
Base = declarative_base()


load_dotenv()

DB_USER = os.getenv("CLEVER_USER")
DB_PASSWORD = os.getenv("CLEVER_PASSWORD")
DB_HOST = os.getenv("CLEVER_HOST")
DB_PORT = os.getenv("CLEVER_PORT")
DB_NAME = os.getenv("CLEVER_DATABASE")

CLEVER_DB = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine: AsyncEngine = create_async_engine(CLEVER_DB, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async with async_session() as session:
        yield session

