# -*- coding: utf-8 -*-
"""Пересобирает все картинки сайта из исходников с повышенным качеством.

Раньше стояло webp 82 / jpg 84. Заказчик заметил падение качества, поэтому
поднимаем до webp 90 / jpg 92 и берём максимально доступный исходник, а не
уже сжатую копию: иначе потери накапливаются.
"""
from PIL import Image
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(ROOT, '_originals')
OFF = os.path.join(ORIG, 'official')
IMG = os.path.join(ROOT, 'assets/img')

WEBP_Q, JPG_Q = 90, 92

# имя на сайте -> файл исходника
MAP = {}
for f in os.listdir(ORIG):
    if f.lower().endswith(('.jpg', '.png')):
        MAP[os.path.splitext(f)[0]] = os.path.join(ORIG, f)

MAP.update({
    'work_reiki':    os.path.join(OFF, '52056733.jpg'),
    'work_marble':   os.path.join(OFF, '52056735.jpg'),
    'work_pendants': os.path.join(OFF, '52058161.jpg'),
    'work_montage':  os.path.join(OFF, '52058565.jpg'),
    # официальные версии кадров, которые есть в лучшем разрешении
    'files_17': os.path.join(OFF, '52056731.jpg'),
    'files_16': os.path.join(OFF, '52059189.jpg'),
    'files_11': os.path.join(OFF, '52059193.jpg'),
    'files_12': os.path.join(OFF, '52056729.jpg'),
    'files_14': os.path.join(OFF, '52059185.jpg'),
    'files_15': os.path.join(OFF, '52059187.jpg'),
    'files_13': os.path.join(OFF, '52059191.jpg'),
})

TEXTURE_MAP = {'rolls': os.path.join(ORIG, 'files_im4.jpg'),
               'fabric': os.path.join(ORIG, 'files_im5.jpg')}

REVIEW_MAP = {'irina': os.path.join(OFF, '52057767.png'),
              'dmitry': os.path.join(OFF, '52057813.png'),
              'anastasia': os.path.join(OFF, '52057859.png')}

WIDTHS = {'lg': 1600, 'sm': 800}
stats = {'ok': 0, 'skip': 0, 'before': 0, 'after': 0}


def rebuild(folder, name, src, sizes=WIDTHS, square=False):
    if not src or not os.path.exists(src):
        print('   нет исходника для', name)
        stats['skip'] += 1
        return
    im = Image.open(src).convert('RGB')
    if square:
        s = min(im.size)
        left = (im.width - s) // 2
        top = 0 if im.height <= im.width else int((im.height - s) * 0.18)
        im = im.crop((left, top, left + s, top + s))

    for tag, w in sizes.items():
        d = os.path.join(IMG, folder, tag)
        if not os.path.isdir(d):
            continue
        for ext in ('webp', 'jpg'):
            target = os.path.join(d, f'{name}.{ext}')
            if not os.path.exists(target):
                continue
            stats['before'] += os.path.getsize(target)
            c = im.copy()
            if c.width > w:
                c = c.resize((w, round(c.height * w / c.width)), Image.LANCZOS)
            if ext == 'webp':
                c.save(target, 'WEBP', quality=WEBP_Q, method=6)
            else:
                c.save(target, 'JPEG', quality=JPG_Q, optimize=True, progressive=True)
            stats['after'] += os.path.getsize(target)
            stats['ok'] += 1


names = set()
for tag in ('lg', 'sm'):
    d = os.path.join(IMG, 'portfolio', tag)
    if os.path.isdir(d):
        names |= {os.path.splitext(f)[0] for f in os.listdir(d)}

print('портфолио:')
for n in sorted(names):
    rebuild('portfolio', n, MAP.get(n))

print('фактуры:')
for n, src in TEXTURE_MAP.items():
    rebuild('textures', n, src)

print('портреты:')
for n, src in REVIEW_MAP.items():
    rebuild('reviews', n, src, sizes={'lg': 320, 'sm': 160}, square=True)

print()
print('перекодировано файлов: %d, пропущено: %d' % (stats['ok'], stats['skip']))
print('было %.2f MB -> стало %.2f MB' % (stats['before'] / 1048576, stats['after'] / 1048576))
