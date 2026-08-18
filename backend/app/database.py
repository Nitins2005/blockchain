from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

try:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )
except Exception as e:
    logger.warning(f"Failed to create database engine for {settings.DATABASE_URL}: {e}")
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    try:
        from app.models import user, wallet, transaction, wallet_feature, prediction, investigation, blacklist, notification, blockchain_config
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified successfully.")
    except Exception as e:
        logger.warning(f"Skipping database table creation: {e}")
