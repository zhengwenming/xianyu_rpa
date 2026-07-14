"""意图分类器 - LLM 驱动"""
from app.services.llm.factory import get_llm
from app.utils.logger import get_logger

logger = get_logger(__name__)

CLASSIFY_PROMPT = """你是一个闲鱼客服意图分类器。根据用户消息判断意图类型。

用户消息：{user_message}

商品信息：{product_info}

对话历史（最近3轮）：
{recent_history}

请只输出以下分类之一，不要输出其他内容：
- BARGAIN: 用户在讨价还价、询问能否便宜、要求降价
- TECHNICAL: 用户询问商品参数、功能、规格、兼容性、使用方法
- LOGISTICS: 用户询问发货、物流、快递、到货时间
- AFTER_SALE: 用户询问售后、退换货、质量问题
- GENERAL: 通用咨询、闲聊、其他

只输出分类标签，如：BARGAIN"""


class IntentClassifier:
    """LLM 驱动的意图分类器"""

    def __init__(self):
        self._fallback_rules = {
            # 关键词匹配规则（LLM 降级方案）
            "价格|便宜|降价|优惠|折扣|几折|能不能少|便宜点|太贵|贵了|最低|预算": "BARGAIN",
            "参数|规格|尺寸|重量|材质|颜色|版本|型号|兼容|能?用|怎么用|功能|支持|接口|系统": "TECHNICAL",
            "发货|物流|快递|邮费|运费|包邮|多久到|什么时候发|顺丰|中通": "LOGISTICS",
            "退货|换货|退款|售后|维修|坏了|问题|质量|破损|瑕疵|不满意|投诉": "AFTER_SALE",
        }

    async def classify(self, context, user_message: str) -> str:
        """分类用户意图"""
        # 先尝试 LLM 分类
        try:
            llm = get_llm()
            prompt = CLASSIFY_PROMPT.format(
                user_message=user_message,
                product_info=context.product_info or "无",
                recent_history=context.get_recent_history(6),
            )
            result = await llm.chat([
                {"role": "system", "content": "你是一个意图分类器，只输出分类标签。"},
                {"role": "user", "content": prompt},
            ], temperature=0.1, max_tokens=20)
            intent = result.strip().upper()
            if intent in ["BARGAIN", "TECHNICAL", "LOGISTICS", "AFTER_SALE", "GENERAL"]:
                return intent
        except Exception as e:
            logger.warning(f"LLM 分类失败，使用关键词降级: {e}")

        # LLM 不可用时，用关键词匹配
        return self._keyword_classify(user_message)

    def _keyword_classify(self, message: str) -> str:
        """关键词匹配分类（降级方案）"""
        import re
        for pattern, intent in self._fallback_rules.items():
            if re.search(pattern, message):
                return intent
        return "GENERAL"


# 全局实例
intent_classifier = IntentClassifier()