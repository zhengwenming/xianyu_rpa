#!/usr/bin/env python3
"""
闲鱼自动化铺货系统 - 图标生成
参考闲鱼官方 App 图标：黄色背景 + 白色鱼形 + 大眼睛微笑
+ 右下角小齿轮暗示"自动化"

生成: icon_1024.png, icon.iconset/, icon.ico
"""
import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ICON_DIR = Path(__file__).parent
SIZE = 1024

# ─── 闲鱼官方色系 ───
YELLOW_BG = (255, 215, 0)          # 闲鱼主黄 #FFD700
YELLOW_LIGHT = (255, 232, 84)      # 顶部浅黄
YELLOW_DEEP = (255, 190, 0)        # 底部深黄
FISH_WHITE = (255, 255, 255)       # 鱼身白色
EYE_BLACK = (30, 30, 30)           # 眼睛深色
BLUSH_PINK = (255, 148, 148)       # 腮红
GEAR_ORANGE = (255, 128, 0)        # 齿轮橙色（自动化点缀）
GEAR_DARK = (200, 90, 0)


def rounded_rect_mask(size, radius):
    """圆角矩形 alpha 遮罩"""
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size, size], radius=radius, fill=255)
    return mask


def make_vertical_gradient(width, height, color_top, color_bottom):
    """垂直渐变"""
    grad = Image.new("RGB", (1, height), color_top)
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(color_top[0] * (1 - t) + color_bottom[0] * t)
        g = int(color_top[1] * (1 - t) + color_bottom[1] * t)
        b = int(color_top[2] * (1 - t) + color_bottom[2] * t)
        grad.putpixel((0, y), (r, g, b))
    return grad.resize((width, height))


def draw_icon(size=1024):
    """绘制闲鱼风格图标"""
    # ─── 1. 黄色圆角矩形背景 ───
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # 渐变黄色背景
    bg = make_vertical_gradient(size, size, YELLOW_LIGHT, YELLOW_DEEP).convert("RGBA")
    mask = rounded_rect_mask(size, radius=int(size * 0.225))
    bg.putalpha(mask)
    canvas.paste(bg, (0, 0), bg)

    draw = ImageDraw.Draw(canvas, "RGBA")

    # ─── 2. 鱼身（白色，卡通鱼头形状）───
    # 采用「圆脸 + 三角小尾巴」的简约风格
    # 中心稍偏左，鱼头朝右
    cx, cy = size // 2 - 30, size // 2 + 20

    # 鱼身主体：一个大椭圆
    body_w = int(size * 0.52)
    body_h = int(size * 0.52)
    body_left = cx - body_w // 2
    body_top = cy - body_h // 2
    body_right = cx + body_w // 2
    body_bottom = cy + body_h // 2

    # 白色鱼身
    draw.ellipse(
        [body_left, body_top, body_right, body_bottom],
        fill=FISH_WHITE,
    )

    # ─── 3. 鱼尾（左侧小三角，指向左边）───
    tail_size = int(size * 0.12)
    tail_x = body_left + 20  # 鱼尾根部
    tail_y = cy

    # 鱼尾用两个三角形组成的分叉尾巴
    tail_points_upper = [
        (tail_x, tail_y - 20),                          # 尾根上
        (tail_x - tail_size, tail_y - tail_size),       # 尾尖上
        (tail_x - tail_size + 20, tail_y),              # 尾中
    ]
    tail_points_lower = [
        (tail_x, tail_y + 20),                          # 尾根下
        (tail_x - tail_size, tail_y + tail_size),       # 尾尖下
        (tail_x - tail_size + 20, tail_y),              # 尾中
    ]
    draw.polygon(tail_points_upper, fill=FISH_WHITE)
    draw.polygon(tail_points_lower, fill=FISH_WHITE)

    # ─── 4. 眼睛（两个大眼睛，闲鱼灵魂）───
    # 左眼（大）
    eye_radius_1 = int(size * 0.062)
    eye1_x = cx + int(size * 0.02)
    eye1_y = cy - int(size * 0.05)
    draw.ellipse(
        [eye1_x - eye_radius_1, eye1_y - eye_radius_1,
         eye1_x + eye_radius_1, eye1_y + eye_radius_1],
        fill=EYE_BLACK,
    )
    # 左眼高光
    hl1_r = int(eye_radius_1 * 0.35)
    draw.ellipse(
        [eye1_x + eye_radius_1 // 3 - hl1_r, eye1_y - eye_radius_1 // 2 - hl1_r,
         eye1_x + eye_radius_1 // 3 + hl1_r, eye1_y - eye_radius_1 // 2 + hl1_r],
        fill=FISH_WHITE,
    )

    # 右眼（也大，稍偏右）
    eye_radius_2 = int(size * 0.062)
    eye2_x = cx + int(size * 0.19)
    eye2_y = cy - int(size * 0.05)
    draw.ellipse(
        [eye2_x - eye_radius_2, eye2_y - eye_radius_2,
         eye2_x + eye_radius_2, eye2_y + eye_radius_2],
        fill=EYE_BLACK,
    )
    # 右眼高光
    hl2_r = int(eye_radius_2 * 0.35)
    draw.ellipse(
        [eye2_x + eye_radius_2 // 3 - hl2_r, eye2_y - eye_radius_2 // 2 - hl2_r,
         eye2_x + eye_radius_2 // 3 + hl2_r, eye2_y - eye_radius_2 // 2 + hl2_r],
        fill=FISH_WHITE,
    )

    # ─── 5. 微笑嘴巴（一个小弧线）───
    mouth_cx = cx + int(size * 0.10)
    mouth_cy = cy + int(size * 0.08)
    mouth_w = int(size * 0.09)
    mouth_h = int(size * 0.05)
    # 用 arc 画笑脸
    draw.arc(
        [mouth_cx - mouth_w, mouth_cy - mouth_h,
         mouth_cx + mouth_w, mouth_cy + mouth_h],
        start=20, end=160,
        fill=EYE_BLACK,
        width=int(size * 0.012),
    )

    # ─── 6. 腮红（可爱感）───
    blush_r = int(size * 0.028)
    # 左腮红
    draw.ellipse(
        [cx - int(size * 0.03) - blush_r, cy + int(size * 0.05) - blush_r,
         cx - int(size * 0.03) + blush_r, cy + int(size * 0.05) + blush_r],
        fill=BLUSH_PINK + (0,) if isinstance(BLUSH_PINK, tuple) and len(BLUSH_PINK) == 4 else (*BLUSH_PINK, 180),
    )
    # 右腮红
    draw.ellipse(
        [cx + int(size * 0.23) - blush_r, cy + int(size * 0.05) - blush_r,
         cx + int(size * 0.23) + blush_r, cy + int(size * 0.05) + blush_r],
        fill=(*BLUSH_PINK, 180),
    )

    # ─── 7. 右下角小齿轮（暗示"自动化"，不破坏主视觉）───
    gear_cx = int(size * 0.79)
    gear_cy = int(size * 0.79)
    gear_outer_r = int(size * 0.10)
    gear_inner_r = int(size * 0.055)
    gear_hole_r = int(size * 0.028)
    teeth_count = 8

    # 齿轮外圈（8 个梯形齿）
    gear_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(gear_layer)

    for i in range(teeth_count):
        ang = 360 / teeth_count * i
        # 齿的四个顶点
        half_angle = 360 / teeth_count / 4
        a1 = math.radians(ang - half_angle * 1.3)
        a2 = math.radians(ang + half_angle * 1.3)
        a3 = math.radians(ang + half_angle * 0.8)
        a4 = math.radians(ang - half_angle * 0.8)
        r_out = gear_outer_r * 1.22
        r_in = gear_outer_r
        pts = [
            (gear_cx + r_in * math.cos(a1), gear_cy + r_in * math.sin(a1)),
            (gear_cx + r_out * math.cos(a4), gear_cy + r_out * math.sin(a4)),
            (gear_cx + r_out * math.cos(a3), gear_cy + r_out * math.sin(a3)),
            (gear_cx + r_in * math.cos(a2), gear_cy + r_in * math.sin(a2)),
        ]
        gdraw.polygon(pts, fill=GEAR_ORANGE)

    # 齿轮主圆
    gdraw.ellipse(
        [gear_cx - gear_outer_r, gear_cy - gear_outer_r,
         gear_cx + gear_outer_r, gear_cy + gear_outer_r],
        fill=GEAR_ORANGE,
        outline=GEAR_DARK,
        width=3,
    )
    # 内圆（露出下面的黄底）
    gdraw.ellipse(
        [gear_cx - gear_inner_r, gear_cy - gear_inner_r,
         gear_cx + gear_inner_r, gear_cy + gear_inner_r],
        fill=(255, 210, 0, 255),
        outline=GEAR_DARK,
        width=3,
    )
    # 中心黑孔（更聚焦）
    gdraw.ellipse(
        [gear_cx - gear_hole_r, gear_cy - gear_hole_r,
         gear_cx + gear_hole_r, gear_cy + gear_hole_r],
        fill=GEAR_DARK,
    )

    canvas.alpha_composite(gear_layer)

    # ─── 8. 顶部反光（macOS 图标质感）───
    highlight = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(highlight)
    # 顶部半月形高光
    hdraw.ellipse(
        [80, -size // 2, size - 80, size // 3],
        fill=(255, 255, 255, 45),
    )
    highlight = highlight.filter(ImageFilter.GaussianBlur(radius=4))
    # 用圆角矩形 mask 裁剪
    highlight.putalpha(mask)
    canvas.alpha_composite(highlight)

    return canvas


def main():
    print("🎨 生成闲鱼风格图标...")

    icon = draw_icon(SIZE)

    # 保存主图
    main_png = ICON_DIR / "icon_1024.png"
    icon.save(main_png, "PNG")
    print(f"✅ 主图: {main_png}")

    # macOS iconset
    iconset_dir = ICON_DIR / "icon.iconset"
    iconset_dir.mkdir(exist_ok=True)
    apple_sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]
    for s, name in apple_sizes:
        resized = icon.resize((s, s), Image.LANCZOS)
        resized.save(iconset_dir / name, "PNG")
    print(f"✅ macOS iconset: {iconset_dir}")

    # Windows .ico
    ico_path = ICON_DIR / "icon.ico"
    icon.save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(f"✅ Windows ICO: {ico_path}")

    print("\n下一步: iconutil -c icns", str(iconset_dir))


if __name__ == "__main__":
    main()
