import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.core.config import settings

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_generate_image(client):
    response = client.post(
        "/api/v1/images/generate",
        json={
            "prompt": "a beautiful sunset",
            "negative_prompt": "ugly, blurry",
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "width": 512,
            "height": 512
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "filename" in data
    assert data["prompt"] == "a beautiful sunset"

def test_get_image(client, db):
    # 先创建一个图片
    create_response = client.post(
        "/api/v1/images/generate",
        json={
            "prompt": "test image",
            "num_inference_steps": 20
        }
    )
    image_id = create_response.json()["id"]

    # 获取创建的图片
    response = client.get(f"/api/v1/images/{image_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == image_id
    assert data["prompt"] == "test image"

def test_list_images(client, db):
    # 创建多个图片
    for i in range(3):
        client.post(
            "/api/v1/images/generate",
            json={
                "prompt": f"test image {i}",
                "num_inference_steps": 20
            }
        )

    # 获取图片列表
    response = client.get("/api/v1/images/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all("id" in item for item in data)
    assert all("prompt" in item for item in data) 