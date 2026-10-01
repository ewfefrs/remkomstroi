# -*- coding: utf-8 -*-
"""
Собирает таблицу цен для заказчика из assets/js/prices.js.
Запуск: python make_price_table.py
Результат: ПРАЙС-для-заказчика.md в корне проекта.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets/js/prices.js')
OUT = os.path.join(ROOT, 'ПРАЙС-для-заказчика.md')

src = open(SRC, encoding='utf-8').read()

block = re.search(r'textures:\s*\{(.*?)\n  \}', src, re.S).group(1)
textures = []
for m in re.finditer(r"(\w+):\s*\{\s*label:\s*'([^']+)',\s*pricePerM2:\s*(\d+)", block):
    textures.append((m.group(1), m.group(2), int(m.group(3))))

nums = {}
for key in ('cornerPrice', 'cornersFree', 'lightPrice', 'pipePrice', 'minOrder', 'giftEveryM2'):
    mm = re.search(key + r':\s*(\d+)', src)
    nums[key] = int(mm.group(1)) if mm else 0


def plural(n, one, few, many):
    """Русские склонения: 1 угол, 2 угла, 5 углов."""
    n = abs(n) % 100
    if 11 <= n <= 14:
        return many
    n %= 10
    if n == 1:
        return one
    if 2 <= n <= 4:
        return few
    return many


def money(n):
    return f'{round(n):,}'.replace(',', ' ') + ' ₽'


def total(area, corners, lights, pipes, price):
    """Та же формула, что в калькуляторе на сайте."""
    canvas = area * price
    extra_corners = max(0, corners - nums['cornersFree']) * nums['cornerPrice']
    lamps = lights * nums['lightPrice']
    tubes = pipes * nums['pipePrice']
    gift = (area // nums['giftEveryM2']) * price
    return max(canvas + extra_corners + lamps + tubes - gift, nums['minOrder'])


ROOMS = [
    ('Маленькая комната', 12, 4, 3, 0),
    ('Стандартная комната', 18, 4, 4, 0),
    ('Большая комната', 25, 4, 6, 1),
    ('Типовое решение с сайта', 33, 4, 6, 0),
]

L = []
L.append('# Прайс для заполнения: РемКомСтрой')
L.append('')
L.append('Таблица собрана из того, что сейчас стоит в калькуляторе на сайте.')
L.append('Заполните колонку «Ваша цена» и верните, я обновлю сайт.')
L.append('')
L.append('> **Важно.** На вашем сайте цена «от 190 ₽/м²» стоит со звёздочкой,')
L.append('> а внизу страницы написано «* цена для дилеров». Значит, 190 ₽ это не')
L.append('> розничная цена. Сейчас калькулятор считает именно от неё, поэтому итоговые')
L.append('> суммы ниже, скорее всего, занижены. Нужна ваша розничная ставка за м².')
L.append('')

L.append('## 1. Цена за квадратный метр по фактурам')
L.append('')
L.append('В цену входит полотно, профиль и монтаж.')
L.append('')
L.append('| Фактура | Сейчас в калькуляторе | Откуда взято | **Ваша цена, ₽/м²** |')
L.append('|---|---:|---|---:|')
for key, label, price in textures:
    origin = 'с вашего сайта (дилерская)' if price == 190 else 'моя оценка, нужно подтвердить'
    L.append(f'| {label} | {price} ₽ | {origin} | |')
L.append('')

L.append('## 2. Дополнительные работы')
L.append('')
L.append('| Позиция | Сейчас в калькуляторе | **Ваша цена** |')
L.append('|---|---:|---:|')
L.append(f'| Угол свыше {nums["cornersFree"]}-го (за штуку) | {nums["cornerPrice"]} ₽ | |')
L.append(f'| Врезка и подключение светильника | {nums["lightPrice"]} ₽ | |')
L.append(f'| Обвод трубы | {nums["pipePrice"]} ₽ | |')
L.append(f'| Минимальная сумма заказа | {money(nums["minOrder"])} | |')
L.append('')

L.append('## 3. Сколько получается всего')
L.append('')
L.append('Примеры полной стоимости по текущим ставкам. Учтена ваша акция')
L.append(f'«каждый {nums["giftEveryM2"]}-й метр в подарок».')
L.append('')

header = '| Фактура | ' + ' | '.join(f'{n}<br>{a} м²' for n, a, *_ in ROOMS) + ' |'
L.append(header)
L.append('|---' + '|---:' * len(ROOMS) + '|')
for key, label, price in textures:
    cells = [money(total(a, c, li, p, price)) for _, a, c, li, p in ROOMS]
    L.append(f'| {label} | ' + ' | '.join(cells) + ' |')
L.append('')
L.append('Состав комнат в примерах:')
L.append('')
for name, a, c, li, p in ROOMS:
    parts = [f'{a} м²',
             f'{c} ' + plural(c, 'угол', 'угла', 'углов'),
             f'{li} ' + plural(li, 'светильник', 'светильника', 'светильников')]
    if p:
        parts.append(f'{p} ' + plural(p, 'труба', 'трубы', 'труб'))
    L.append(f'- **{name}**: ' + ', '.join(parts))
L.append('')

L.append('## 4. Как считается итог')
L.append('')
L.append('```')
L.append('площадь × цена за м²')
L.append(f'+ (углы свыше {nums["cornersFree"]}) × {nums["cornerPrice"]} ₽')
L.append(f'+ светильники × {nums["lightPrice"]} ₽')
L.append(f'+ трубы × {nums["pipePrice"]} ₽')
L.append(f'− каждый {nums["giftEveryM2"]}-й м² в подарок')
L.append(f'= итог, но не меньше {money(nums["minOrder"])}')
L.append('```')
L.append('')
L.append('Если формула у вас другая (например, углы считаются иначе или есть цена')
L.append('за погонный метр профиля), напишите как правильно, я переделаю расчёт.')
L.append('')
L.append('---')
L.append('')
L.append('После заполнения цены проставляются в файле `assets/js/prices.js`,')
L.append('и калькулятор на сайте начинает считать по ним. Больше нигде цены не зашиты.')

open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print('готово:', OUT)
print('фактур:', len(textures), '| примеров комнат:', len(ROOMS))
