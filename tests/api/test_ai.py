from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash

def test_text_to_image(
    client: TestClient,
    db: Session,
    test_user: User
):
    """测试文生图"""
    # 登录获取token
    login_data = {
        "username": test_user.email,
        "password": "testpass"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 测试文生图
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "prompt": "a beautiful landscape",
        "negative_prompt": "ugly, blurry",
        "engine": "stable_diffusion",
        "parameters": {
            "steps": 20,
            "width": 512,
            "height": 512
        }
    }
    response = client.post(
        f"{settings.API_V1_STR}/ai/text-to-image",
        json=data,
        headers=headers
    )
    assert response.status_code == 200
    result = response.json()
    assert "image_path" in result
    assert Path(result["image_path"]).exists()

def test_image_to_image(
    client: TestClient,
    db: Session,
    test_user: User
):
    """测试图生图"""
    # 登录获取token
    login_data = {
        "username": test_user.email,
        "password": "testpass"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 创建测试图片
    test_image = Path("test_image.png")
    test_image.write_bytes(b"fake image data")
    
    # 测试图生图
    headers = {"Authorization": f"Bearer {token}"}
    files = {"image": ("test_image.png", open(test_image, "rb"))}
    data = {
        "prompt": "make it more beautiful",
        "negative_prompt": "ugly, blurry",
        "engine": "stable_diffusion",
        "parameters": {
            "steps": 20,
            "denoising_strength": 0.75
        }
    }
    response = client.post(
        f"{settings.API_V1_STR}/ai/image-to-image",
        files=files,
        data=data,
        headers=headers
    )
    assert response.status_code == 200
    result = response.json()
    assert "image_path" in result
    assert Path(result["image_path"]).exists()
    
    # 清理测试文件
    test_image.unlink()

def test_get_models(
    client: TestClient,
    db: Session,
    test_user: User
):
    """测试获取模型列表"""
    # 登录获取token
    login_data = {
        "username": test_user.email,
        "password": "testpass"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 测试获取模型列表
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        f"{settings.API_V1_STR}/ai/models/stable_diffusion",
        headers=headers
    )
    assert response.status_code == 200
    result = response.json()
    assert "models" in result 