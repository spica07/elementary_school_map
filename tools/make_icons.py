# -*- coding: utf-8 -*-
"""소스 일러스트(SOURCE_IMG)에서 앱 아이콘(192/512/apple-180/maskable-512) 생성.
소스 배경의 검은 모서리를 흰색으로 채운 뒤 각 크기로 리사이즈한다."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")

TOOLS = Path(__file__).resolve().parent
ICONS = TOOLS.parent / "assets" / "icons"
SOURCE_IMG = TOOLS / "icon-source.png"

WHITE = (254, 254, 254)
MASKABLE_SAFE_ZONE = 0.92  # 중심 92%만 남기고 확대 (런처 마스크 크롭 대비)


def load_base():
    src = Image.open(SOURCE_IMG).convert("RGB")
    w, h = src.size
    img = src.copy()
    for corner in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(img, corner, WHITE, thresh=40)
    return img


def build(base, size, out_name, maskable=False):
    if maskable:
        w, h = base.size
        margin_w = int(w * (1 - MASKABLE_SAFE_ZONE) / 2)
        margin_h = int(h * (1 - MASKABLE_SAFE_ZONE) / 2)
        cropped = base.crop((margin_w, margin_h, w - margin_w, h - margin_h))
        img = cropped.resize((size, size), Image.LANCZOS)
    else:
        img = base.resize((size, size), Image.LANCZOS)
    img.save(ICONS / out_name)
    print("saved", out_name, img.size)


base = load_base()
build(base, 512, "app-icon-512.png")
build(base, 192, "app-icon-192.png")
build(base, 180, "app-icon-apple-180.png")
build(base, 512, "app-icon-maskable-512.png", maskable=True)
