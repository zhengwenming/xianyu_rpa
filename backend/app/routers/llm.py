"""LLM 配置 API 路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.llm_config import LLMConfig
from app.services.llm.factory import LLMFactory, set_llm

router = APIRouter(prefix="/api/llm", tags=["LLM配置"])


class LLMConfigCreate(BaseModel):
    name: str
    provider_type: str
    api_key: str = ""
    api_base: str = ""
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    image_model: Optional[str] = None


class LLMConfigUpdate(BaseModel):
    name: Optional[str] = None
    provider_type: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    image_model: Optional[str] = None


@router.get("/configs")
async def list_configs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LLMConfig).order_by(LLMConfig.created_at.desc()))
    configs = result.scalars().all()
    return {"code": 0, "data": [c.to_dict() for c in configs], "message": "ok"}


@router.post("/configs")
async def create_config(data: LLMConfigCreate, db: AsyncSession = Depends(get_db)):
    config = LLMConfig(**data.dict())
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return {"code": 0, "data": config.to_dict(), "message": "配置创建成功"}


@router.put("/configs/{config_id}")
async def update_config(config_id: str, data: LLMConfigUpdate, db: AsyncSession = Depends(get_db)):
    config = await db.get(LLMConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(config, key, value)
    await db.commit()
    await db.refresh(config)
    return {"code": 0, "data": config.to_dict(), "message": "更新成功"}


@router.delete("/configs/{config_id}")
async def delete_config(config_id: str, db: AsyncSession = Depends(get_db)):
    config = await db.get(LLMConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    await db.delete(config)
    await db.commit()
    return {"code": 0, "data": None, "message": "已删除"}


@router.post("/configs/{config_id}/test")
async def test_config(config_id: str, db: AsyncSession = Depends(get_db)):
    config = await db.get(LLMConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    try:
        provider = LLMFactory.create(config)
        success = await provider.test_connection()
        return {"code": 0 if success else 1, "data": {"success": success}, "message": "连接成功" if success else "连接失败"}
    except Exception as e:
        return {"code": 1, "data": {"success": False}, "message": str(e)}


@router.post("/configs/{config_id}/activate")
async def activate_config(config_id: str, db: AsyncSession = Depends(get_db)):
    config = await db.get(LLMConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    result = await db.execute(select(LLMConfig).where(LLMConfig.is_active == True))
    for c in result.scalars().all():
        c.is_active = False
    config.is_active = True
    await db.commit()
    set_llm(config)
    return {"code": 0, "data": config.to_dict(), "message": "已激活"}


@router.post("/generate")
async def generate_text(prompt: str):
    try:
        from app.services.llm.factory import get_llm
        llm = get_llm()
        result = await llm.chat([{"role": "user", "content": prompt}])
        return {"code": 0, "data": {"result": result}, "message": "ok"}
    except Exception as e:
        return {"code": 1, "data": None, "message": str(e)}