# -*- coding: utf-8 -*-
"""
Собирает Excel-прайс по ценам материала из assets/js/prices.js.
Заказчик заполняет жёлтые ячейки, итоги пересчитываются формулами Excel.

Запуск: python make_price_xlsx.py
Результат: ПРАЙС-материала.xlsx в корне проекта.
"""
import os
import re

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets/js/prices.js')
OUT = os.path.join(ROOT, 'ПРАЙС-материала.xlsx')

# ------------------------------ данные ------------------------------

src = open(SRC, encoding='utf-8').read()
block = re.search(r'textures:\s*\{(.*?)\n  \}', src, re.S).group(1)

TEXTURES = [(m.group(1), int(m.group(2)))
            for m in re.finditer(r"\w+:\s*\{\s*label:\s*'([^']+)',\s*pricePerM2:\s*(\d+)", block)]

NUM = {}
for key in ('cornerPrice', 'cornersFree', 'lightPrice', 'pipePrice', 'minOrder', 'giftEveryM2'):
    NUM[key] = int(re.search(key + r':\s*(\d+)', src).group(1))

# Матовое и глянцевое взяты с сайта компании, остальное моя оценка
ORIGIN = {190: 'с сайта компании, помечена как «цена для дилеров»'}
DEFAULT_ORIGIN = 'оценка, требует подтверждения'

ROOMS = [('Маленькая комната', 12, 4, 3, 0),
         ('Стандартная комната', 18, 4, 4, 0),
         ('Большая комната', 25, 4, 6, 1),
         ('Типовое решение с сайта', 33, 4, 6, 0)]

# ------------------------------ оформление ------------------------------

FONT = 'Arial'
INK = '1A1A1A'
GREEN = '00803A'

f_title = Font(name=FONT, size=16, bold=True, color=INK)
f_sub = Font(name=FONT, size=10, color='595959')
f_section = Font(name=FONT, size=12, bold=True, color='FFFFFF')
f_head = Font(name=FONT, size=10, bold=True, color=INK)
f_body = Font(name=FONT, size=10, color=INK)
f_input = Font(name=FONT, size=10, bold=True, color='0000FF')   # синий: ячейки для заполнения
f_formula = Font(name=FONT, size=10, color=INK)                 # чёрный: формулы
f_link = Font(name=FONT, size=10, color='008000')               # зелёный: ссылка на другой лист
f_note = Font(name=FONT, size=9, italic=True, color='7F7F7F')
f_total = Font(name=FONT, size=10, bold=True, color=INK)

fill_section = PatternFill('solid', fgColor=GREEN)
fill_head = PatternFill('solid', fgColor='EDF1F5')
fill_input = PatternFill('solid', fgColor='FFFF00')             # жёлтый: заполнить
fill_accent = PatternFill('solid', fgColor='E8F3EC')

thin = Side(style='thin', color='C9D2DB')
box = Border(left=thin, right=thin, top=thin, bottom=thin)

RUB = '#,##0" ₽"'
RUB_M2 = '#,##0" ₽/м²"'

wrap_top = Alignment(vertical='top', wrap_text=True)
center = Alignment(horizontal='center', vertical='center')


def style_row(ws, row, cols, font=None, fill=None, fmt=None, align=None):
    for c in cols:
        cell = ws.cell(row=row, column=c)
        cell.border = box
        if font:
            cell.font = font
        if fill:
            cell.fill = fill
        if fmt:
            cell.number_format = fmt
        if align:
            cell.alignment = align


def section(ws, row, last_col, text):
    ws.cell(row=row, column=1, value=text).font = f_section
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    for c in range(1, last_col + 1):
        ws.cell(row=row, column=c).fill = fill_section
    ws.row_dimensions[row].height = 22


wb = Workbook()

# ==================================================================
# Лист 1: цены материала
# ==================================================================

ws = wb.active
ws.title = 'Материал'
ws.sheet_view.showGridLines = False

ws['A1'] = 'Прайс на материал: натяжные потолки'
ws['A1'].font = f_title
ws.merge_cells('A1:E1')

ws['A2'] = ('РемКомСтрой, Мурманск. Цены собраны из калькулятора на сайте. '
            'Заполните столбец «Ваша цена», итоги на листе «Расчёт» пересчитаются сами.')
ws['A2'].font = f_sub
ws.merge_cells('A2:E2')
ws.row_dimensions[2].height = 28
ws['A2'].alignment = wrap_top

ws['A4'] = 'ВАЖНО'
ws['A4'].font = Font(name=FONT, size=10, bold=True, color='C00000')
ws['B4'] = ('На вашем сайте цена «от 190 ₽/м²» стоит со звёздочкой, а внизу страницы написано '
            '«цена для дилеров». Значит, это не розничная цена, и расчёт сейчас занижен.')
ws['B4'].font = Font(name=FONT, size=10, color='C00000')
ws.merge_cells('B4:E4')
ws['B4'].alignment = wrap_top
ws.row_dimensions[4].height = 28

ws['A6'] = 'Как заполнять'
ws['A6'].font = f_head
ws['B6'] = 'Жёлтые ячейки — для вас. Впишите цену цифрами, без пробелов и знака рубля.'
ws['B6'].font = f_body
ws.merge_cells('B6:E6')

ws['A7'] = 'Пример'
ws['A7'].font = f_head
ws['B7'] = 'Матовое'
ws['B7'].font = f_body
ws['C7'] = 190
ws['C7'].font = f_body
ws['C7'].number_format = RUB_M2
ws['D7'] = 350
ws['D7'].font = f_input
ws['D7'].fill = fill_input
ws['D7'].number_format = RUB_M2
ws['E7'] = 'так выглядит заполненная строка'
ws['E7'].font = f_note

HEAD_ROW = 9
headers = ['Фактура полотна', 'Цена в калькуляторе', 'Ваша цена', 'В расчёте', 'Откуда взята текущая цена']
for i, h in enumerate(headers, start=1):
    c = ws.cell(row=HEAD_ROW, column=i, value=h)
    c.font = f_head
    c.fill = fill_head
    c.border = box
    c.alignment = Alignment(vertical='center', wrap_text=True)
ws.row_dimensions[HEAD_ROW].height = 30

FIRST = HEAD_ROW + 1
for i, (label, price) in enumerate(TEXTURES):
    r = FIRST + i
    ws.cell(row=r, column=1, value=label).font = f_body
    ws.cell(row=r, column=2, value=price).font = f_body
    ws.cell(row=r, column=2).number_format = RUB_M2
    ws.cell(row=r, column=3).font = f_input
    ws.cell(row=r, column=3).fill = fill_input
    ws.cell(row=r, column=3).number_format = RUB_M2
    # если своя цена не вписана, в расчёт идёт текущая
    ws.cell(row=r, column=4, value=f'=IF(C{r}="",B{r},C{r})').font = f_formula
    ws.cell(row=r, column=4).number_format = RUB_M2
    ws.cell(row=r, column=5, value=ORIGIN.get(price, DEFAULT_ORIGIN)).font = f_note
    ws.cell(row=r, column=5).alignment = wrap_top
    style_row(ws, r, range(1, 6))
    ws.row_dimensions[r].height = 20

LAST = FIRST + len(TEXTURES) - 1
ws.cell(row=LAST + 2, column=1,
        value='Цена включает полотно, профиль и монтаж.').font = f_note
ws.cell(row=LAST + 3, column=1,
        value='Столбец «В расчёте» подставляет вашу цену, а пока она пустая — текущую.').font = f_note

ws['C9'].comment = Comment(
    'Впишите свою розничную цену за квадратный метр. Пустая ячейка означает '
    '«оставить как есть», тогда в расчёт идёт цена из калькулятора.', 'РемКомСтрой')

widths = {'A': 26, 'B': 20, 'C': 16, 'D': 15, 'E': 44}
for col, w in widths.items():
    ws.column_dimensions[col].width = w

# ==================================================================
# Лист 2: работы и итоговая стоимость
# ==================================================================

ws2 = wb.create_sheet('Расчёт')
ws2.sheet_view.showGridLines = False

ws2['A1'] = 'Дополнительные работы и итоговая стоимость'
ws2['A1'].font = f_title
ws2.merge_cells('A1:F1')

ws2['A2'] = 'Жёлтые ячейки — для заполнения. Всё остальное считается формулами.'
ws2['A2'].font = f_sub
ws2.merge_cells('A2:F2')

section(ws2, 4, 4, '  1. Дополнительные работы')

W_HEAD = 5
for i, h in enumerate(['Позиция', 'Сейчас', 'Ваша цена', 'В расчёте'], start=1):
    c = ws2.cell(row=W_HEAD, column=i, value=h)
    c.font = f_head
    c.fill = fill_head
    c.border = box

WORKS = [
    (f'Угол свыше {NUM["cornersFree"]}-го, за штуку', NUM['cornerPrice'], RUB),
    ('Врезка и подключение светильника', NUM['lightPrice'], RUB),
    ('Обвод трубы', NUM['pipePrice'], RUB),
    ('Минимальная сумма заказа', NUM['minOrder'], RUB),
]
W_FIRST = W_HEAD + 1
for i, (label, val, fmt) in enumerate(WORKS):
    r = W_FIRST + i
    ws2.cell(row=r, column=1, value=label).font = f_body
    ws2.cell(row=r, column=2, value=val).font = f_body
    ws2.cell(row=r, column=2).number_format = fmt
    ws2.cell(row=r, column=3).font = f_input
    ws2.cell(row=r, column=3).fill = fill_input
    ws2.cell(row=r, column=3).number_format = fmt
    ws2.cell(row=r, column=4, value=f'=IF(C{r}="",B{r},C{r})').font = f_formula
    ws2.cell(row=r, column=4).number_format = fmt
    style_row(ws2, r, range(1, 5))

CORNER, LAMP, PIPE, MINORDER = (f'$D${W_FIRST + i}' for i in range(4))

r = W_FIRST + len(WORKS)
ws2.cell(row=r, column=1, value='Углов включено в базовую цену').font = f_body
ws2.cell(row=r, column=2, value=NUM['cornersFree']).font = f_body
ws2.cell(row=r, column=4, value=f'=B{r}').font = f_formula
style_row(ws2, r, range(1, 5))
FREE_CORNERS = f'$D${r}'

r += 1
ws2.cell(row=r, column=1, value='Акция: каждый N-й м² в подарок').font = f_body
ws2.cell(row=r, column=2, value=NUM['giftEveryM2']).font = f_body
ws2.cell(row=r, column=4, value=f'=B{r}').font = f_formula
style_row(ws2, r, range(1, 5))
GIFT = f'$D${r}'

for col, w in {'A': 34, 'B': 14, 'C': 14, 'D': 14, 'E': 14, 'F': 14}.items():
    ws2.column_dimensions[col].width = w

# ---- параметры комнат ----

R_SEC = r + 2
section(ws2, R_SEC, 5, '  2. Из чего состоят типовые комнаты')

R_HEAD = R_SEC + 1
for i, h in enumerate(['Комната', 'Площадь, м²', 'Углов', 'Светильников', 'Труб'], start=1):
    c = ws2.cell(row=R_HEAD, column=i, value=h)
    c.font = f_head
    c.fill = fill_head
    c.border = box

R_FIRST = R_HEAD + 1
for i, (name, area, corners, lamps, pipes) in enumerate(ROOMS):
    rr = R_FIRST + i
    for j, v in enumerate((name, area, corners, lamps, pipes), start=1):
        cell = ws2.cell(row=rr, column=j, value=v)
        cell.font = f_body if j == 1 else f_input
        if j > 1:
            cell.fill = fill_input
    style_row(ws2, rr, range(1, 6))

# ---- итоговая матрица ----

T_SEC = R_FIRST + len(ROOMS) + 1
section(ws2, T_SEC, 5, '  3. Сколько получается всего')

T_HEAD = T_SEC + 1
ws2.cell(row=T_HEAD, column=1, value='Фактура').font = f_head
ws2.cell(row=T_HEAD, column=1).fill = fill_head
ws2.cell(row=T_HEAD, column=1).border = box
for i, (name, area, *_rest) in enumerate(ROOMS):
    c = ws2.cell(row=T_HEAD, column=2 + i, value=f'{name}\n{area} м²')
    c.font = f_head
    c.fill = fill_head
    c.border = box
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
ws2.row_dimensions[T_HEAD].height = 34

T_FIRST = T_HEAD + 1
for i, (label, _price) in enumerate(TEXTURES):
    rr = T_FIRST + i
    ws2.cell(row=rr, column=1, value=f"=Материал!A{FIRST + i}").font = f_link
    for j in range(len(ROOMS)):
        room_row = R_FIRST + j
        price = f'Материал!$D${FIRST + i}'
        area = f'$B${room_row}'
        corners = f'$C${room_row}'
        lamps = f'$D${room_row}'
        pipes = f'$E${room_row}'
        formula = (
            f'=MAX({area}*{price}'
            f'+MAX(0,{corners}-{FREE_CORNERS})*{CORNER}'
            f'+{lamps}*{LAMP}'
            f'+{pipes}*{PIPE}'
            f'-INT({area}/{GIFT})*{price}'
            f',{MINORDER})'
        )
        c = ws2.cell(row=rr, column=2 + j, value=formula)
        c.font = f_total
        c.number_format = RUB
    style_row(ws2, rr, range(1, 2 + len(ROOMS)))

T_LAST = T_FIRST + len(TEXTURES) - 1

# ---- как считается ----

N = T_LAST + 2
ws2.cell(row=N, column=1, value='Как считается итог').font = f_head
lines = [
    'площадь × цена за м² по фактуре',
    f'+ углы свыше {NUM["cornersFree"]}-го × цена за угол',
    '+ светильники × врезка',
    '+ трубы × обвод',
    f'− каждый {NUM["giftEveryM2"]}-й м² в подарок (действующая акция)',
    'Итого: не меньше минимальной суммы заказа',
]
for i, line in enumerate(lines, start=1):
    # Текст, начинающийся с '=', Excel принимает за формулу и выдаёт #NAME?
    safe = "'" + line if line[:1] in '=+-@' else line
    ws2.cell(row=N + i, column=1, value=safe).font = f_note
    ws2.merge_cells(start_row=N + i, start_column=1, end_row=N + i, end_column=5)

N2 = N + len(lines) + 2
ws2.cell(row=N2, column=1,
         value='Если формула у вас другая, например есть цена за погонный метр профиля '
               'или углы считаются иначе, напишите как правильно.').font = f_note
ws2.merge_cells(start_row=N2, start_column=1, end_row=N2, end_column=5)

ws2.cell(row=N2 + 2, column=1,
         value='Источник текущих цен: assets/js/prices.js в проекте сайта. '
               'После согласования цены проставляются там, и калькулятор считает по ним.').font = f_note
ws2.merge_cells(start_row=N2 + 2, start_column=1, end_row=N2 + 2, end_column=5)

# ---- легенда цветов ----

L = N2 + 4
ws2.cell(row=L, column=1, value='Обозначения').font = f_head
legend = [
    (fill_input, f_input, 'жёлтая ячейка, синий шрифт', 'заполняете вы'),
    (None, f_formula, 'чёрный шрифт', 'считается формулой'),
    (None, f_link, 'зелёный шрифт', 'ссылка на лист «Материал»'),
]
for i, (fill, font, what, meaning) in enumerate(legend, start=1):
    c = ws2.cell(row=L + i, column=1, value=what)
    c.font = font
    if fill:
        c.fill = fill
    c.border = box
    ws2.cell(row=L + i, column=2, value=meaning).font = f_note
    ws2.merge_cells(start_row=L + i, start_column=2, end_row=L + i, end_column=5)

ws.sheet_view.selection[0].activeCell = 'C10'
ws.sheet_view.selection[0].sqref = 'C10'

wb.save(OUT)
print('записано:', OUT)
print('фактур:', len(TEXTURES), '| комнат:', len(ROOMS))


def recalc(path):
    """Excel сохраняет посчитанные значения формул, openpyxl этого не умеет.
    Без пересчёта формулы читаются как пустые где угодно, кроме самого Excel.
    Работаем через временную копию с латинским именем: COM спотыкается
    на кириллице в пути."""
    import shutil, subprocess, tempfile
    tmp = os.path.join(tempfile.gettempdir(), 'rks_price_recalc.xlsx')
    shutil.copy2(path, tmp)
    ps = (
        "$e = New-Object -ComObject Excel.Application; $e.Visible = $false; "
        "$e.DisplayAlerts = $false; "
        f"$w = $e.Workbooks.Open('{tmp}'); "
        "$e.Application.CalculateFullRebuild(); $w.Save(); $w.Close($true); $e.Quit(); "
        "[System.Runtime.InteropServices.Marshal]::ReleaseComObject($e) | Out-Null"
    )
    r = subprocess.run(['powershell', '-NoProfile', '-Command', ps],
                       capture_output=True, text=True)
    if r.returncode == 0 and os.path.getsize(tmp) > 0:
        shutil.copy2(tmp, path)
        os.remove(tmp)
        return True
    print('  пересчитать не удалось:', (r.stderr or r.stdout).strip()[:160])
    return False


if recalc(OUT):
    from openpyxl import load_workbook
    fw = load_workbook(OUT)
    vw = load_workbook(OUT, data_only=True)
    ERR = ('#REF!', '#NAME?', '#VALUE!', '#DIV/0!', '#N/A', '#NULL!', '#NUM!')
    total = ok = bad = 0
    problems = []
    for sh in fw.worksheets:
        for row in sh.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('='):
                    total += 1
                    got = vw[sh.title][c.coordinate].value
                    if isinstance(got, str) and got in ERR:
                        bad += 1
                        problems.append(f'{sh.title}!{c.coordinate} = {got}')
                    elif got is not None:
                        ok += 1
    print(f'формулы пересчитаны: {ok} из {total}, ошибок {bad}')
    for pr in problems[:10]:
        print('   ', pr)
else:
    print('ВНИМАНИЕ: формулы записаны, но без посчитанных значений. '
          'Откройте файл в Excel и сохраните, либо запустите скрипт на машине с Excel.')
