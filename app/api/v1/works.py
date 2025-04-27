from typing import Any, List, Optional
from datetime import datetime, timedelta
import random
import string
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.core.deps import get_current_active_user, get_db
from app.models.user import User
from app.models.work import Work
from app.models.tag import Tag
from app.schemas.work import (
    WorkCreate, WorkUpdate, WorkResponse, WorkList,
    WorkShare, SharedWorkResponse
)

router = APIRouter()

def generate_share_code(length: int = 8) -> str:
    """生成分享码"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@router.post("/", response_model=WorkResponse)
def create_work(
    *,
    work_in: WorkCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """创建作品"""
    work = Work(
        title=work_in.title,
        description=work_in.description,
        image_path=work_in.image_path,
        prompt=work_in.prompt,
        negative_prompt=work_in.negative_prompt,
        parameters=work_in.parameters,
        ai_engine=work_in.ai_engine,
        owner_id=current_user.id
    )
    db.add(work)
    db.commit()
    db.refresh(work)
    return work

@router.get("/", response_model=WorkList)
def get_works(
    *,
    skip: int = 0,
    limit: int = 10,
    tag: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取作品列表"""
    query = db.query(Work).filter(Work.owner_id == current_user.id)
    
    if tag:
        query = query.join(Work.tags).filter(Tag.name == tag)
    
    total = query.count()
    works = query.order_by(desc(Work.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": works
    }

@router.get("/{work_id}", response_model=WorkResponse)
def get_work(
    *,
    work_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取作品详情"""
    work = db.query(Work).filter(
        Work.id == work_id,
        Work.owner_id == current_user.id
    ).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    return work

@router.put("/{work_id}", response_model=WorkResponse)
def update_work(
    *,
    work_id: int,
    work_in: WorkUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """更新作品"""
    work = db.query(Work).filter(
        Work.id == work_id,
        Work.owner_id == current_user.id
    ).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # 更新基本信息
    if work_in.title is not None:
        work.title = work_in.title
    if work_in.description is not None:
        work.description = work_in.description
    if work_in.is_public is not None:
        work.is_public = work_in.is_public
    
    # 更新标签
    if work_in.tags is not None:
        # 清除现有标签
        work.tags = []
        # 添加新标签
        for tag_name in work_in.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            work.tags.append(tag)
    
    db.add(work)
    db.commit()
    db.refresh(work)
    return work

@router.delete("/{work_id}")
def delete_work(
    *,
    work_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """删除作品"""
    work = db.query(Work).filter(
        Work.id == work_id,
        Work.owner_id == current_user.id
    ).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    db.delete(work)
    db.commit()
    return {"status": "success"}

@router.post("/{work_id}/share", response_model=WorkResponse)
def share_work(
    *,
    work_id: int,
    share_in: WorkShare,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """分享作品"""
    work = db.query(Work).filter(
        Work.id == work_id,
        Work.owner_id == current_user.id
    ).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # 更新分享状态
    work.is_public = share_in.is_public
    if share_in.is_public:
        work.share_code = generate_share_code()
        if share_in.expires_in_hours:
            work.share_expires_at = datetime.utcnow() + timedelta(hours=share_in.expires_in_hours)
        else:
            work.share_expires_at = None
    else:
        work.share_code = None
        work.share_expires_at = None
    
    db.add(work)
    db.commit()
    db.refresh(work)
    return work

@router.get("/shared/{share_code}", response_model=SharedWorkResponse)
def get_shared_work(
    *,
    share_code: str,
    db: Session = Depends(get_db)
) -> Any:
    """获取分享的作品"""
    work = db.query(Work).filter(
        Work.share_code == share_code,
        Work.is_public == True
    ).first()
    if not work:
        raise HTTPException(status_code=404, detail="分享的作品不存在")
    
    # 检查是否过期
    if work.share_expires_at and work.share_expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="分享链接已过期")
    
    # 获取作品所有者信息
    owner = db.query(User).filter(User.id == work.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="作品所有者不存在")
    
    # 转换为响应模型
    response = SharedWorkResponse.from_orm(work)
    response.owner_name = owner.username
    return response

@router.get("/public/", response_model=WorkList)
def get_public_works(
    *,
    skip: int = 0,
    limit: int = 10,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Any:
    """获取公开作品列表"""
    query = db.query(Work).filter(
        Work.is_public == True,
        or_(
            Work.share_expires_at == None,
            Work.share_expires_at > datetime.utcnow()
        )
    )
    
    if tag:
        query = query.join(Work.tags).filter(Tag.name == tag)
    
    total = query.count()
    works = query.order_by(desc(Work.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": works
    } 