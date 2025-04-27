from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database.base import Base
from app.main import app
from app.core.deps import get_db

# 使用内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db() -> Generator:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def create_test_db() -> None:
    Base.metadata.create_all(bind=engine)

def drop_test_db() -> None:
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def db() -> Generator:
    create_test_db()
    yield TestingSessionLocal()
    drop_test_db()

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c 