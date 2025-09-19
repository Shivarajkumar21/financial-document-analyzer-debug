from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Text, JSON

# Use aiosqlite for async support
DATABASE_URL = "sqlite+aiosqlite:///analysis.db"

# Create async engine and session
async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine, 
    class_=AsyncSession
)

Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, index=True)
    query = Column(String)
    file_path = Column(String)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)

async def init_db():
    """Initialize the database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
