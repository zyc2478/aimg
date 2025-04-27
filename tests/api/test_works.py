from pathlib import Path
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.work import Work
from app.models.tag import Tag

def test_create_work(
    client: TestClient,
    db: Session,
    test_user: User
):
    """测试创建作品"""
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
    
    # 创建作品
    headers = {"Authorization": f"Bearer {token}"}
    work_data = {
        "title": "测试作品",
        "description": "这是一个测试作品",
        "image_path": "test_image.png",
        "prompt": "a beautiful landscape",
        "negative_prompt": "ugly, blurry",
        "parameters": {
            "steps": 20,
            "width": 512,
            "height": 512
        },
        "ai_engine": "stable_diffusion"
    }
    response = client.post(
        f"{settings.API_V1_STR}/works/",
        json=work_data,
        headers=headers
    )
    assert response.status_code == 200
    result = response.json()
    assert result["title"] == work_data["title"]
    assert result["owner_id"] == test_user.id

def test_get_works(
    client: TestClient,
    db: Session,
    test_user: User
):
    """测试获取作品列表"""
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
    
    # 创建测试标签
    tag = Tag(name="landscape")
    db.add(tag)
    db.commit()
    
    # 创建测试作品
    work = Work(
        title="测试作品",
        description="这是一个测试作品",
        image_path="test_image.png",
        prompt="a beautiful landscape",
        negative_prompt="ugly, blurry",
        parameters={"steps": 20},
        ai_engine="stable_diffusion",
        owner_id=test_user.id,
        tags=[tag]
    )
    db.add(work)
    db.commit()
    
    # 获取作品列表
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        f"{settings.API_V1_STR}/works/",
        headers=headers
    )
    assert response.status_code == 200
    result = response.json()
    assert result["total"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["title"] == work.title
    
    # 按标签筛选
    response = client.get(
        f"{settings.API_V1_STR}/works/?tag=landscape",
        headers=headers
    )
    assert response.status_code == 200
    result = response.json()
    assert result["total"] == 1

def test_update_work(
    client: TestClient,
    db: Session,
    test_user: User
):
    """测试更新作品"""
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
    
    # 创建测试作品
    work = Work(
        title="测试作品",
        description="这是一个测试作品",
        image_path="test_image.png",
        prompt="a beautiful landscape",
        negative_prompt="ugly, blurry",
        parameters={"steps": 20},
        ai_engine="stable_diffusion",
        owner_id=test_user.id
    )
    db.add(work)
    db.commit()
    
    # 更新作品
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "title": "更新后的作品",
        "description": "这是更新后的描述",
        "tags": ["landscape", "nature"]
    }
    response = client.put(
        f"{settings.API_V1_STR}/works/{work.id}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    result = response.json()
    assert result["title"] == update_data["title"]
    assert result["description"] == update_data["description"]
    assert len(result["tags"]) == 2

def test_delete_work(
    client: TestClient,
    db: Session,
    test_user: User
):
    """测试删除作品"""
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
    
    # 创建测试作品
    work = Work(
        title="测试作品",
        description="这是一个测试作品",
        image_path="test_image.png",
        prompt="a beautiful landscape",
        negative_prompt="ugly, blurry",
        parameters={"steps": 20},
        ai_engine="stable_diffusion",
        owner_id=test_user.id
    )
    db.add(work)
    db.commit()
    
    # 删除作品
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(
        f"{settings.API_V1_STR}/works/{work.id}",
        headers=headers
    )
    assert response.status_code == 200
    
    # 验证作品已删除
    deleted_work = db.query(Work).filter(Work.id == work.id).first()
    assert deleted_work is None

def test_share_work(
    client: TestClient,
    db: Session,
    test_user: User
):
    """测试分享作品"""
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
    
    # 创建测试作品
    work = Work(
        title="测试作品",
        description="这是一个测试作品",
        image_path="test_image.png",
        prompt="a beautiful landscape",
        negative_prompt="ugly, blurry",
        parameters={"steps": 20},
        ai_engine="stable_diffusion",
        owner_id=test_user.id
    )
    db.add(work)
    db.commit()
    
    # 分享作品
    headers = {"Authorization": f"Bearer {token}"}
    share_data = {
        "is_public": True,
        "expires_in_hours": 24
    }
    response = client.post(
        f"{settings.API_V1_STR}/works/{work.id}/share",
        json=share_data,
        headers=headers
    )
    assert response.status_code == 200
    result = response.json()
    assert result["is_public"] == True
    assert result["share_code"] is not None
    assert result["share_expires_at"] is not None
    
    # 获取分享的作品
    response = client.get(
        f"{settings.API_V1_STR}/works/shared/{result['share_code']}"
    )
    assert response.status_code == 200
    shared_result = response.json()
    assert shared_result["title"] == work.title
    assert shared_result["owner_name"] == test_user.username

def test_public_works(
    client: TestClient,
    db: Session,
    test_user: User
):
    """测试获取公开作品列表"""
    # 创建测试标签
    tag = Tag(name="landscape")
    db.add(tag)
    db.commit()
    
    # 创建公开作品
    work = Work(
        title="公开作品",
        description="这是一个公开作品",
        image_path="test_image.png",
        prompt="a beautiful landscape",
        negative_prompt="ugly, blurry",
        parameters={"steps": 20},
        ai_engine="stable_diffusion",
        owner_id=test_user.id,
        is_public=True,
        tags=[tag]
    )
    db.add(work)
    db.commit()
    
    # 获取公开作品列表
    response = client.get(f"{settings.API_V1_STR}/works/public/")
    assert response.status_code == 200
    result = response.json()
    assert result["total"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["title"] == work.title
    
    # 按标签筛选
    response = client.get(f"{settings.API_V1_STR}/works/public/?tag=landscape")
    assert response.status_code == 200
    result = response.json()
    assert result["total"] == 1 