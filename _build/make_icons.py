# -*- coding: utf-8 -*-
"""
Собирает иконки сайта из настоящего логотипа компании.
Исходник: _originals/official/logo.png (прозрачный PNG).
Запуск: python make_icons.py
"""
from PIL import Image
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_originals/official/logo.png')

src = Image.open(SRC).convert('RGBA')

# У логотипа по краям прозрачные поля. Если их не убрать, в размере вкладки
# знак получается слишком мелким и превращается в пятно.
bbox = src.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
logo = src.crop(bbox)

pad = round(max(logo.size) * 0.04)
canvas = Image.new('RGBA', (logo.width + pad * 2, logo.height + pad * 2), (0, 0, 0, 0))
canvas.paste(logo, (pad, pad), logo)

side = max(canvas.size)
square = Image.new('RGBA', (side, side), (0, 0, 0, 0))
square.paste(canvas, ((side - canvas.width) // 2, (side - canvas.height) // 2), canvas)


def at(size):
    return square.resize((size, size), Image.LANCZOS)


ico = os.path.join(ROOT, 'favicon.ico')
if os.path.exists(ico):
    os.remove(ico)
at(64).save(ico, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

brand = os.path.join(ROOT, 'assets/img/brand')
os.makedirs(brand, exist_ok=True)
at(192).save(os.path.join(brand, 'icon-192.png'), 'PNG', optimize=True)
at(96).save(os.path.join(brand, 'logo-96.png'), 'PNG', optimize=True)
at(512).save(os.path.join(brand, 'logo-512.png'), 'PNG', optimize=True)

# iOS плохо работает с прозрачностью, поэтому кладём знак на белое поле
apple = Image.new('RGB', (180, 180), (255, 255, 255))
mark = at(148)
apple.paste(mark, (16, 16), mark)
apple.save(os.path.join(ROOT, 'apple-touch-icon.png'), 'PNG', optimize=True)

for f in ('favicon.ico', 'apple-touch-icon.png',
          'assets/img/brand/icon-192.png', 'assets/img/brand/logo-96.png'):
    path = os.path.join(ROOT, f)
    print('%-38s %d байт' % (f, os.path.getsize(path)))
