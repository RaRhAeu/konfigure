from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings

engine = create_async_engine(
    settings.DB_URL, pool_size=settings.POOL_SIZE, echo=True, echo_pool=True
)


async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except:  # noqa
            await session.rollback()
            raise
