"""LLM 内容生成服务"""
from typing import Optional
from app.services.llm.factory import get_llm
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Prompt 模板
LISTING_TITLE_PROMPT = """你是一个闲鱼商品文案专家。请根据以下商品信息，生成一个吸引人的闲鱼商品标题。

原始商品信息：
- 标题：{original_title}
- 价格：{price}
- 规格：{specs}

要求：
1. 标题不超过 30 个字
2. 突出核心卖点和性价比
3. 符合闲鱼平台的文案风格（口语化、有吸引力）
4. 不要使用违禁词或夸大宣传

请直接输出标题，不要加其他内容。"""

LISTING_DESC_PROMPT = """你是一个闲鱼商品文案专家。请根据以下信息，生成一段闲鱼商品描述。

商品信息：
- 标题：{title}
- 原始描述：{original_desc}
- 价格：{price}
- 规格：{specs}
- 发货地：{ship_from}

要求：
1. 描述分为几个部分：商品介绍、规格参数、发货说明、售后说明
2. 语气真诚、口语化，像个人卖家
3. 突出商品成色和性价比
4. 适当使用 emoji 增加亲和力
5. 总字数控制在 200-400 字

请直接输出商品描述。"""

SHORT_TITLE_PROMPT = """你是一个闲鱼商品文案专家。请根据以下商品信息，生成一个8-12字的导购短标题。

原始商品标题：{original_title}

要求：
1. 8-12个字
2. 突出核心卖点
3. 简洁有力，吸引点击

请直接输出短标题，不要加其他内容。"""


class ContentGenerator:
    """内容生成器"""

    async def generate_title(self, product: dict) -> str:
        """生成闲鱼商品标题"""
        try:
            llm = get_llm()
            prompt = LISTING_TITLE_PROMPT.format(
                original_title=product.get("title", ""),
                price=product.get("price", 0),
                specs=product.get("specs", "无"),
            )
            title = await llm.chat([
                {"role": "system", "content": "你是一个闲鱼商品文案专家。"},
                {"role": "user", "content": prompt},
            ], temperature=0.7, max_tokens=100)
            title = title.strip().strip('"').strip("'")
            logger.info(f"生成标题成功: {title[:30]}")
            return title[:50]  # 限制长度
        except Exception as e:
            logger.warning(f"LLM 生成标题失败，使用原始标题: {e}")
            return product.get("title", "闲置商品")[:50]

    async def generate_description(self, product: dict, price: float) -> str:
        """生成闲鱼商品描述"""
        try:
            llm = get_llm()
            prompt = LISTING_DESC_PROMPT.format(
                title=product.get("title", ""),
                original_desc=product.get("specs", ""),
                price=price,
                specs=product.get("specs", "无"),
                ship_from=product.get("ship_from", "全国"),
            )
            desc = await llm.chat([
                {"role": "system", "content": "你是一个闲鱼商品文案专家。"},
                {"role": "user", "content": prompt},
            ], temperature=0.7, max_tokens=500)
            logger.info(f"生成描述成功: {len(desc)} 字")
            return desc
        except Exception as e:
            logger.warning(f"LLM 生成描述失败，使用默认描述: {e}")
            return f"全新闲置，低价转让。\n\n商品：{product.get('title', '')}\n价格：{price}元\n\n全新未使用，包装完好，放心购买。\n\n拍下后48小时内发货，全国包邮。\n\n有问题随时联系，诚信交易。"

    async def generate_short_title(self, product: dict) -> str:
        """生成导购短标题"""
        try:
            llm = get_llm()
            prompt = SHORT_TITLE_PROMPT.format(
                original_title=product.get("title", ""),
            )
            short_title = await llm.chat([
                {"role": "system", "content": "你是一个闲鱼商品文案专家。"},
                {"role": "user", "content": prompt},
            ], temperature=0.5, max_tokens=50)
            short_title = short_title.strip().strip('"').strip("'")
            logger.info(f"生成短标题成功: {short_title}")
            return short_title[:20]
        except Exception as e:
            logger.warning(f"生成短标题失败: {e}")
            return ""

    async def crop_images(self, image_urls: list[str]) -> list[str]:
        """智能裁剪图片为3:4比例"""
        from PIL import Image
        import requests
        from io import BytesIO
        import os
        from app.config import settings

        cropped = []
        for url in image_urls[:9]:
            try:
                # 下载图片
                resp = requests.get(url, timeout=10)
                img = Image.open(BytesIO(resp.content))

                # 裁剪为3:4
                width, height = img.size
                target_ratio = 3 / 4
                current_ratio = width / height

                if current_ratio > target_ratio:
                    # 太宽，裁剪宽度
                    new_width = int(height * target_ratio)
                    offset = (width - new_width) // 2
                    img = img.crop((offset, 0, offset + new_width, height))
                elif current_ratio < target_ratio:
                    # 太高，裁剪高度
                    new_height = int(width / target_ratio)
                    offset = (height - new_height) // 2
                    img = img.crop((0, offset, width, offset + new_height))

                # 保存裁剪后的图片
                cache_dir = os.path.join(settings.SESSION_DIR, "_cache")
                os.makedirs(cache_dir, exist_ok=True)
                filename = f"crop_{hash(url)}_{os.path.basename(url)}"
                filepath = os.path.join(cache_dir, filename)
                img.save(filepath, quality=95)
                cropped.append(filepath)

            except Exception as e:
                logger.warning(f"图片裁剪失败: {e}")
                cropped.append(url)  # 使用原图

        return cropped


# 全局实例
content_generator = ContentGenerator()