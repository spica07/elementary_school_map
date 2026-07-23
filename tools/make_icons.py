# -*- coding: utf-8 -*-
"""소스 일러스트(SOURCE_IMG)에서 앱 아이콘(192/512/apple-180/maskable-512) 생성.
소스 배경의 검은 모서리를 흰색으로 채운 뒤, 상하좌우에 여백을 두고 각 크기로 리사이즈한다.
(휴대폰 런처가 아이콘에 자체 마스크를 씌우면서 가장자리 텍스트가 잘리는 문제 방지)"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")

TOOLS = Path(__file__).resolve().parent
ICONS = TOOLS.parent / "assets" / "icons"
SOURCE_IMG = TOOLS / "icon-source.png"

WHITE = (254, 254, 254)
CONTENT_RATIO = 0.82        # 일반 아이콘: 콘텐츠를 82%로 축소, 상하좌우 9% 여백
MASKABLE_CONTENT_RATIO = 0.66  # 마스커블 아이콘: 안드로이드 세이프존(중심 66%) 기준


def load_base():
    src = Image.open(SOURCE_IMG).convert("RGB")
    w, h = src.size
    img = src.copy()
    for corner in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(img, corner, WHITE, thresh=40)
    return img


def pad(base, content_ratio):
    w, h = base.size
    content_w = int(w * content_ratio)
    content_h = int(h * content_ratio)
    shrunk = base.resize((content_w, content_h), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), WHITE)
    canvas.paste(shrunk, ((w - content_w) // 2, (h - content_h) // 2))
    return canvas


def build(img, size, out_name):
    resized = img.resize((size, size), Image.LANCZOS)
    resized.save(ICONS / out_name)
    print("saved", out_name, resized.size)


base = load_base()
padded = pad(base, CONTENT_RATIO)
build(padded, 512, "app-icon-512.png")
build(padded, 192, "app-icon-192.png")
build(padded, 180, "app-icon-apple-180.png")

padded_maskable = pad(base, MASKABLE_CONTENT_RATIO)
build(padded_maskable, 512, "app-icon-maskable-512.png")
