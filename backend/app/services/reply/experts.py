"""多专家路由 - 各专家回复生成"""
import re
from app.services.llm.factory import get_llm
from app.services.reply.prompts import prompt_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ExpertRouter:
    """专家路由 - 意图到专家名称映射"""

    EXPERTS = {
        "BARGAIN": "price_expert",      # 议价专家
        "TECHNICAL": "tech_expert",     # 技术专家
        "LOGISTICS": "logistics_expert", # 物流专家
        "AFTER_SALE": "service_expert",  # 售后专家
        "GENERAL": "default_expert",     # 默认客服
    }

    # 关键词回复规则（LLM 降级方案）
    _keyword_reply_rules: list[dict] = []

    @classmethod
    def set_keyword_rules(cls, rules: list[dict]):
        """设置关键词回复规则"""
        cls._keyword_rules = rules

    @classmethod
    async def generate_reply(cls, expert_name: str, context, user_message: str) -> str:
        """生成专家回复"""
        # 先尝试关键词匹配
        reply = cls._keyword_match(user_message)
        if reply:
            return reply

        # 尝试 LLM 生成
        try:
            llm = get_llm()
            prompt_template = prompt_manager.get_prompt(expert_name)

            # 构建上下文
            product_info = context.product_info or {}
            prompt = prompt_template.format(
                title=product_info.get("title", "商品"),
                price=product_info.get("price", "面议"),
                min_price=product_info.get("min_price", product_info.get("price", 0)),
                description=product_info.get("description", ""),
                specs=product_info.get("specs", "标准规格"),
                ship_from=product_info.get("ship_from", "全国"),
                history=context.get_recent_history(6),
                user_message=user_message,
            )

            reply = await llm.chat([
                {"role": "system", "content": f"你是一个闲鱼{expert_name}，生成回复要口语化、像真实卖家。"},
                {"role": "user", "content": prompt},
            ], temperature=0.7, max_tokens=200)

            return reply.strip()

        except Exception as e:
            logger.warning(f"LLM 回复生成失败，使用默认回复: {e}")
            return cls._default_reply(expert_name, user_message)

    @classmethod
    def _keyword_match(cls, message: str) -> str:
        """关键词规则匹配"""
        for rule in getattr(cls, '_keyword_rules', []):
            pattern = rule.get("keyword", "")
            if pattern and pattern.lower() in message.lower():
                return rule.get("reply", "")
        return ""

    @classmethod
    def _default_reply(cls, expert_name: str, user_message: str) -> str:
        """默认回复（LLM 完全不可用时的最底方案）"""
        if "价格" in user_message or "便宜" in user_message:
            return "亲，这个价格已经很实惠了，质量保证，放心购买哦~"
        if "参数" in user_message or "尺寸" in user_message:
            return "亲，商品详情页有详细参数，您可以看一下，有什么不明白的随时问哦~"
        if "发货" in user_message or "物流" in user_message:
            return "亲，下单后48小时内发货，一般2-3天到货，请放心~"
        if "退货" in user_message:
            return "亲，支持7天无理由退货，有任何问题联系我处理~"
        return "亲，您好！有什么可以帮您的吗？"


# 全局实例
expert_router = ExpertRouter()