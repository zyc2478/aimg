from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash

def test_login(client: TestClient, db: Session):
    """测试用户登录"""
    # 创建测试用户
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass"),
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # 测试登录
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "test@example.com", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_register(client: TestClient, db: Session):
    """测试用户注册"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "newpass"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["username"] == "newuser"
    assert "id" in data
    
    # 验证用户已创建
    user = db.query(User).filter(User.email == "new@example.com").first()
    assert user is not None
    assert user.username == "newuser"

def test_register_existing_email(client: TestClient, db: Session):
    """测试注册已存在的邮箱"""
    # 创建测试用户
    user = User(
        email="existing@example.com",
        username="existinguser",
        hashed_password=get_password_hash("testpass"),
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # 测试注册相同邮箱
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "existing@example.com",
            "username": "newuser",
            "password": "newpass"
        }
    )
    assert response.status_code == 400
    assert "该邮箱已被注册" in response.json()["detail"] 