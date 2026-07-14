"""自动回复 API 路由"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.conversation import Conversation
from app.services.reply.engine import reply_engine
from app.services.reply.context import context_manager
from app.services.reply.prompts import prompt_manager
from app.services.xianyu_ws.connection_manager import connection_manager

router = APIRouter(prefix="/api/reply", tags=["自动回复"])


class ExpertPrompt(BaseModel):
    expert_name: str
    prompt: str


@router.get("/status")
async def get_reply_status():
    status = connection_manager.get_all_status()
    return {"code": 0, "data": status, "message": "ok"}


@router.post("/{shop_id}/start")
async def start_reply(shop_id: str):
    success = await connection_manager.start_shop(shop_id)
    return {"code": 0 if success else 1, "data": None, "message": "已启动" if success else "启动失败"}


@router.post("/{shop_id}/stop")
async def stop_reply(shop_id: str):
    await connection_manager.stop_shop(shop_id)
    return {"code": 0, "data": None, "message": "已停止"}


@router.get("/{shop_id}/conversations")
async def list_conversations(shop_id: str):
    sessions = context_manager.get_all_sessions(shop_id)
    return {"code": 0, "data": sessions, "message": "ok"}


@router.get("/{shop_id}/conversations/{user_id}")
async def get_conversation(shop_id: str, user_id: str):
    ctx = context_manager.get(shop_id, user_id)
    if not ctx:
        return {"code": 0, "data": None, "message": "无对话记录"}
    return {"code": 0, "data": ctx.to_dict(), "message": "ok"}


@router.post("/{shop_id}/conversations/{user_id}/takeover")
async def toggle_takeover(shop_id: str, user_id: str):
    ctx = context_manager.get_or_create(shop_id, user_id)
    ctx.human_takeover = not ctx.human_takeover
    return {"code": 0, "data": {"human_takeover": ctx.human_takeover}, "message": "已切换接管模式"}


@router.post("/{shop_id}/send")
async def send_message(shop_id: str, user_id: str, text: str):
    try:
        await connection_manager.send_message(shop_id, user_id, text)
        return {"code": 0, "data": None, "message": "消息已发送"}
    except Exception as e:
        return {"code": 1, "data": None, "message": str(e)}


@router.get("/experts/prompts")
async def get_expert_prompts():
    prompts = prompt_manager.get_all_prompts()
    return {"code": 0, "data": prompts, "message": "ok"}


@router.put("/experts/prompts")
async def update_expert_prompt(data: ExpertPrompt):
    success = prompt_manager.update_prompt(data.expert_name, data.prompt)
    return {"code": 0 if success else 1, "data": None, "message": "更新成功" if success else "专家不存在"}


_keyword_rules: list[dict] = []


@router.get("/rules")
async def list_rules():
    return {"code": 0, "data": _keyword_rules, "message": "ok"}


@router.post("/rules")
async def create_rule(keyword: str, reply: str):
    rule = {"id": str(len(_keyword_rules) + 1), "keyword": keyword, "reply": reply}
    _keyword_rules.append(rule)
    from app.services.reply.experts import expert_router
    expert_router.set_keyword_rules(_keyword_rules)
    return {"code": 0, "data": rule, "message": "创建成功"}


@router.put("/rules/{rule_id}")
async def update_rule(rule_id: str, keyword: str = "", reply: str = ""):
    for rule in _keyword_rules:
        if rule["id"] == rule_id:
            if keyword:
                rule["keyword"] = keyword
            if reply:
                rule["reply"] = reply
            return {"code": 0, "data": rule, "message": "更新成功"}
    return {"code": 1, "data": None, "message": "规则不存在"}


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    global _keyword_rules
    _keyword_rules = [r for r in _keyword_rules if r["id"] != rule_id]
    from app.services.reply.experts import expert_router
    expert_router.set_keyword_rules(_keyword_rules)
    return {"code": 0, "data": None, "message": "已删除"}