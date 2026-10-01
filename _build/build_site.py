# -*- coding: utf-8 -*-
"""
Генератор всех страниц сайта РемКомСтрой.
Единый источник данных: всё, что ниже, снято с официального сайта remkomstroi.ru
(проверено 30.07.2026) и из группы vk.com/remkomstroy.
Запуск: python build_site.py
"""
import os
import re

# папка сайта: на уровень выше этого скрипта
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================ ДАННЫЕ КОМПАНИИ ============================
# Источник: remkomstroi.ru (официальный сайт, платформа Flexbe)

PHONE = '8 (815) 299-41-99'
TEL = '+78152994199'
EMAIL = 'RemKomStroy51@yandex.ru'
ADDRESS = 'г. Мурманск, ул. Полярные Зори, 11'
HOURS = 'Пн-Сб с 9:00 до 20:00'
LEGAL = 'ИП Ничипоренко Евгений Евгеньевич'
INN = '519098049800'
VK = 'https://vk.com/remkomstroy'

# Координаты офиса. Получены геокодированием адреса через OpenStreetMap Nominatim.
LAT, LON = '68.953565', '33.088229'
MAP_EMBED = f'https://yandex.ru/map-widget/v1/?ll={LON}%2C{LAT}&z=17&pt={LON}%2C{LAT}%2Cpm2rdm'
MAP_ROUTE = f'https://yandex.ru/maps/?rtext=~{LAT}%2C{LON}&rtt=auto'

NAV = [
    ('potolki.html', 'Потолки', 'potolki'),
    ('index.html#calc', 'Калькулятор', 'calc'),
    ('raboty.html', 'Работы', 'raboty'),
    ('otzyvy.html', 'Отзывы', 'otzyvy'),
    ('kontakty.html', 'Контакты', 'kontakty'),
]

# Преимущества, дословно с официального сайта
ADVANTAGES = [
    ('medal', 'Более 15 лет опыта',
     'Работаем в Мурманске с 2008 года. За это время через нас прошли сотни квартир, домов и офисов.'),
    ('shield-check', 'Гарантия 10 лет',
     'Десять лет на полотно и год на монтажные работы. Если что-то пойдёт не так, устраним бесплатно.'),
    ('ruler', 'Бесплатный замер',
     'Замерщик приезжает бесплатно и привозит образцы. Расчёт получите в тот же день.'),
    ('wallet', 'Рассрочка без переплат',
     'Условия подбираем индивидуально. Оставьте заявку, предложим удобный вариант оплаты.'),
    ('clock', 'Работы точно в срок',
     'Сроки фиксируем в договоре. В большинстве случаев потолок готов уже в день монтажа.'),
    ('tag', 'Фиксированная стоимость',
     'Цену закрепляем после замера, и в процессе она не меняется. Скрытых доплат нет.'),
]

# Этапы работы, дословно с официального сайта (там их пять)
STEPS = [
    ('Заявка', 'Вы оставляете заявку на сайте или звоните нам сами.'),
    ('Консультация', 'Проводим консультацию и подбираем подходящую вам акцию.'),
    ('Замер', 'Приезжаем на бесплатный замер с образцами полотен.'),
    ('Договор', 'Согласовываем стоимость и фиксируем её в договоре.'),
    ('Монтаж', 'Устанавливаем потолок. Обычно это занимает от 2 до 6 часов на комнату.'),
]

PROMOS = [
    ('sparkle', 'Третий потолок в подарок', 'При заказе двух потолков третий устанавливаем бесплатно.'),
    ('tag', 'Скидка 5% в день замера', 'Если заключаете договор сразу после замера.'),
    ('wallet', 'Найдёте дешевле, сделаем скидку', 'Покажите предложение конкурента, пересчитаем цену.'),
    ('medal', 'Каждый 10-й метр в подарок', 'Чем больше площадь, тем заметнее экономия.'),
]

# Отзывы с официального сайта, вместе с портретами
REVIEWS_MAIN = [
    ('irina', 'Ирина', '35 лет',
     'Сделали потолок в зале и кухне, всё прошло быстрее, чем ожидали. Приехали вовремя, за несколько '
     'часов всё установили. Самое главное чисто, без пыли и мусора. Цена осталась такой же, как озвучили '
     'после замера. Очень довольны результатом.'),
    ('dmitry', 'Дмитрий', '55 лет',
     'Долго выбирали компанию, боялись, что будет как у знакомых: затянут сроки или поднимут цену. '
     'В итоге всё прошло отлично, приехали на следующий день после замера, сделали аккуратно, помогли '
     'с выбором потолка. Уже полгода прошло и всё идеально.'),
    ('anastasia', 'Анастасия', '44 года',
     'Обратились по рекомендации. Нужно было срочно сделать потолок перед заездом. Ребята вошли '
     'в положение и сделали буквально за день. Выглядит очень красиво, спасибо!'),
]

# Короткие версии тех же отзывов для главной, чтобы карточка была в 3 строки
REVIEWS_SHORT = [
    ('irina', 'Ирина', '35 лет',
     'Приехали вовремя, за несколько часов всё установили. Чисто, без пыли и мусора. '
     'Цена осталась такой же, как озвучили после замера.'),
    ('dmitry', 'Дмитрий', '55 лет',
     'Боялись, что затянут сроки или поднимут цену. Приехали на следующий день после замера, '
     'сделали аккуратно. Полгода прошло и всё идеально.'),
    ('anastasia', 'Анастасия', '44 года',
     'Нужно было срочно сделать потолок перед заездом. Ребята вошли в положение '
     'и сделали буквально за день. Очень красиво.'),
]

# Отзывы со второго сайта компании, натяжныепотолкимурманск.рф
REVIEWS_EXTRA = [
    ('Анна', 'по рекомендации знакомых',
     'Ребята молодцы! Порекомендовали фирму через знакомых, не пожалела. Сделали всё качественно '
     'и аккуратно. Плюс порадовали приятные цены. Ещё раз спасибо, успехов!'),
    ('Роман', 'потолки в двух комнатах',
     'Установили нам натяжные потолки в двух комнатах. Хорошо, ровно, относительно быстро. Приехали '
     'в тот день, в который сказали. Взяли предоплату, остаток внесли уже после установки.'),
    ('Дарья', 'потолок в новом офисе',
     'Заказали натяжной потолок в новый офис, хотелось удивить клиентов. Удивились сами: нам сделали '
     'шикарный потолок. Три яруса, точечные светильники, и главное без гипсокартона.'),
    ('Наталья', 'по рекомендации друзей',
     'Мы обратились в компанию по рекомендации друзей. Встретили отличных специалистов, которые не '
     'только профессионалы в своём деле, но и творческие ребята со смелыми идеями.'),
]

# FAQ, дословно с официального сайта
FAQ = [
    ('Сколько длится монтаж?',
     '<p>В большинстве случаев установка занимает от 2 до 6 часов на одну комнату. Если объект большой '
     'или сложный (несколько уровней, подсветка), работы могут занять до одного дня.</p>'
     '<p style="margin-top:.6rem">В 90% случаев вы получаете готовый потолок уже в день монтажа.</p>'),
    ('Есть ли гарантия?',
     '<p>Да, мы даём:</p><ul><li>10 лет гарантии на полотно;</li>'
     '<li>1 год гарантии на монтажные работы.</li></ul>'
     '<p style="margin-top:.6rem">Если в течение этого времени возникнут проблемы, устраним их бесплатно.</p>'),
    ('Можно ли в рассрочку?',
     '<p>Да, у нас есть рассрочка без переплат. Условия подбираем индивидуально: оставьте заявку, '
     'и мы предложим удобный вариант оплаты.</p>'),
    ('Есть ли скрытые доплаты?',
     '<p>Нет. Мы фиксируем стоимость после замера, и она не меняется в процессе работы. '
     'Вы заранее знаете точную цену и платите именно её.</p>'),
    ('Нужно ли выносить мебель?',
     '<p>Полностью выносить мебель не требуется. Достаточно освободить доступ к стенам, то есть '
     'отодвинуть мебель на 50-70 см, и убрать хрупкие вещи. Всё остальное мы аккуратно закроем '
     'и защитим во время монтажа.</p>'),
    ('Что выбрать для кухни, ванной или спальни?',
     '<p>Мы подберём вариант под каждое помещение:</p>'
     '<ul><li>кухня: матовый или сатиновый, практично и легко мыть;</li>'
     '<li>ванная: влагостойкие потолки, не боятся пара и воды;</li>'
     '<li>спальня: матовый или сатиновый, спокойный мягкий свет.</li></ul>'
     '<p style="margin-top:.6rem">Если сомневаетесь, замерщик покажет образцы и поможет выбрать на месте.</p>'),
    ('Можно ли сделать срочно?',
     '<p>Да, можем выполнить заказ в кратчайшие сроки, иногда уже на следующий день. Всё зависит '
     'от загрузки и объёма работ: уточним при звонке и предложим ближайшую дату.</p>'),
]

# Фактуры. Матовый, глянцевый и сатиновый подтверждены официальным сайтом,
# остальные взяты со второго сайта компании и из свежих постов ВКонтакте.
TEXTURES = [
    ('matte', 'Матовые', 'portfolio', 'files_im3', 800, 600, 'lg',
     'Бликов нет совсем, ближе всего к идеально окрашенному потолку. На официальном сайте компании '
     'рекомендуют для спальни и кухни.'),
    ('gloss', 'Глянцевые', 'portfolio', 'files_1.4', 1600, 1600, 'lg',
     'Зеркальная поверхность отражает свет и визуально поднимает потолок. Хорошо работает '
     'в гостиной и санузле.'),
    ('satin', 'Сатиновые', 'portfolio', 'files_17', 1600, 1200, 'lg',
     'Структура поверхности напоминает сатин, отблеск мягкий и перламутровый. Универсальный '
     'вариант и для спальни, и для гостиной.'),
    ('bath', 'Влагостойкие', 'portfolio', 'bath_led', 800, 600, 'lg',
     'Для ванной и санузла. Не боятся пара и воды, при протечке сверху полотно удерживает воду '
     'и его можно слить.'),
    ('fabric', 'Тканевые бесшовные', 'textures', 'fabric', 600, 450, 'lg',
     'Полотно шириной до 5 метров, поэтому шва нет вообще. Дышит, не боится минусовых '
     'температур, монтируется без нагрева.'),
    ('print', 'С фотопечатью', 'portfolio', 'files_1.5', 1600, 1600, 'lg',
     'Любое изображение или фотография. Печать экологичными УФ-чернилами, бесшовно до 5 метров '
     'в ширину.'),
    ('stars', 'Звёздное небо', 'portfolio', 'files_1.6', 1600, 1600, 'lg',
     'Оптоволокно и игра света дают объёмную картину неба. Эффектнее всего в спальне и детской.'),
]

# Портфолио: файл, ширина_sm, высота_sm, категория, подпись
SHOTS = [
    ('files_1.4', 800, 800, 'gloss', 'Глянцевый потолок в светлой комнате'),
    ('bath_led', 800, 600, 'gloss', 'Влагостойкий потолок в ванной с контурной подсветкой'),
    ('files_1.3', 800, 800, 'matte', 'Матовое полотно в просторной комнате'),
    ('files_13', 800, 600, 'matte', 'Люстра и точечные светильники на матовом потолке'),
    ('files_im1', 800, 600, 'matte', 'Дизайнерская люстра в виде облака'),
    ('files_im2', 800, 600, 'matte', 'Светлая комната с люстрой и матовым потолком'),
    ('files_im3', 800, 600, 'matte', 'Матовый потолок с потолочным плафоном'),
    ('hex_lamps', 800, 600, 'matte', 'Матовый потолок с дизайнерскими светильниками'),
    ('files_17', 800, 600, 'satin', 'Подвесные светильники на сатиновом полотне'),
    ('files_12', 800, 600, 'lines', 'Световые линии крестом на потолке'),
    ('files_14', 800, 1067, 'lines', 'Световая линия по всей длине коридора'),
    ('files_16', 800, 600, 'lines', 'Кухня с линейной подсветкой на потолке'),
    ('files_11', 800, 600, 'lines', 'Белое полотно с трековыми светильниками'),
    ('files_10', 800, 1000, 'lines', 'Парящий потолок с контурной подсветкой'),
    ('work_reiki', 800, 600, 'lines', 'Коридор с рейками и трековыми светильниками'),
    ('work_marble', 800, 600, 'lines', 'Контурная подсветка потолка на фоне мрамора'),
    ('lines_triangle', 800, 600, 'lines', 'Световые линии и трековые светильники на потолке'),
    ('files_1.2', 800, 800, 'multi', 'Гостиная с подсветкой по периметру потолка'),
    ('files_15', 800, 600, 'multi', 'Световая рамка с точечными светильниками'),
    ('room_rings', 800, 600, 'multi', 'Комната с панорамными окнами и подсветкой по периметру'),
    ('curved_level', 800, 450, 'multi', 'Двухуровневый потолок с волнообразной границей'),
    ('files_1.5', 800, 800, 'print', 'Фотопечать с крупными цветами на потолке'),
    ('files_im6', 800, 600, 'print', 'Фотопечать с ромашками на глянцевом полотне'),
    ('print_butterfly', 800, 600, 'print', 'Фотопечать с бабочкой на глянцевом полотне'),
    ('files_1.6', 800, 800, 'stars', 'Потолок звёздное небо в гостиной'),
]

CATS = [
    ('all', 'Все работы'), ('gloss', 'Глянцевые'), ('matte', 'Матовые'), ('satin', 'Сатиновые'),
    ('lines', 'Со световыми линиями'), ('multi', 'Многоуровневые'),
    ('print', 'С фотопечатью'), ('stars', 'Звёздное небо'),
]


# Выполняется до отрисовки: ставит класс .js и, если посетитель выбрал полную
# версию, подменяет viewport ещё до первого кадра, чтобы не было перерисовки.
VIEWPORT_SCRIPT = """<script>
(function () {
  var d = document.documentElement;
  d.classList.add('js');
  try {
    if (localStorage.getItem('rks-desktop') === '1') {
      d.setAttribute('data-force-desktop', '1');
      var m = document.querySelector('meta[name="viewport"]');
      if (m) m.setAttribute('content', 'width=1280');
    }
  } catch (e) {}
})();
</script>"""


def read_prices():
    """Достаём ставки из assets/js/prices.js, чтобы цены жили в одном файле."""
    src = open(os.path.join(ROOT, 'assets/js/prices.js'), encoding='utf-8').read()
    block = re.search(r'textures:\s*\{(.*?)\n  \}', src, re.S).group(1)
    out = {}
    for m in re.finditer(r"(\w+):\s*\{\s*label:\s*'([^']+)',\s*pricePerM2:\s*(\d+)", block):
        out[m.group(1)] = {'label': m.group(2), 'price': int(m.group(3))}
    extra = {}
    for key in ('cornerPrice', 'cornersFree', 'lightPrice', 'pipePrice', 'minOrder', 'giftEveryM2'):
        mm = re.search(key + r':\s*(\d+)', src)
        if mm:
            extra[key] = int(mm.group(1))
    return out, extra


def asset_version():
    """Короткий хэш от css и js. Подставляется в ссылки как ?v=,
    чтобы браузер не показывал старую версию после обновления сайта."""
    import hashlib
    h = hashlib.sha1()
    for rel in ('assets/css/style.css', 'assets/js/app.js', 'assets/js/calc.js',
                'assets/js/gallery.js', 'assets/js/prices.js'):
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            h.update(open(p, 'rb').read())
    return h.hexdigest()[:8]


VER = asset_version()

PRICES, PRICE_EXTRA = read_prices()

# Ключи фактур на страницах и в prices.js совпадают не везде.
# Влагостойкие это обычная ПВХ-плёнка, поэтому цена как у глянца.
PRICE_ALIAS = {'stars': 'starrySky', 'bath': 'gloss'}


def price_of(key):
    """Цена за м² для фактуры страницы, с учётом различий в именовании."""
    entry = PRICES.get(PRICE_ALIAS.get(key, key))
    return entry['price'] if entry else None


# ============================ ШАБЛОНЫ ============================

def icon(name, size=None, cls='btn-icon', style=''):
    dim = f' width="{size}" height="{size}"' if size else ''
    c = f' class="{cls}"' if cls else ''
    s = f' style="{style}"' if style else ''
    return f'<svg{c}{dim}{s} aria-hidden="true"><use href="#i-{name}"></use></svg>'


def nav_items(current):
    out = []
    for href, label, key in NAV:
        cur = ' aria-current="page"' if key == current else ''
        out.append(f'        <li><a href="{href}"{cur}>{label}</a></li>')
    return '\n'.join(out)


def head(title, desc, current, canonical=''):
    canon = f'\n<link rel="canonical" href="https://remkomstroi.ru/{canonical}">' if canonical != '' else ''
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">{canon}
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="assets/img/portfolio/lg/work_marble.jpg">
<meta name="theme-color" content="#f4f6f8" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0e1116" media="(prefers-color-scheme: dark)">
{VIEWPORT_SCRIPT}
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="192x192" href="assets/img/brand/icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preload" href="assets/fonts/unbounded-cyrillic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/manrope-cyrillic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/style.css?v={VER}">
</head>
<body>
<!--SPRITE-->
<a class="skip-link" href="#main">Перейти к содержанию</a>
<div id="top-sentinel" aria-hidden="true"></div>

<header class="header">
  <div class="wrap header__inner">
    <a class="logo" href="index.html">
      <img class="logo__mark" src="assets/img/brand/logo-96.png" width="46" height="46" alt="">
      <span class="logo__text">РемКом<span>Строй</span></span>
    </a>
    <nav class="nav" aria-label="Основная навигация">
      <ul class="nav__list">
{nav_items(current)}
      </ul>
    </nav>
    <a class="header__phone" href="tel:{TEL}">
      <b>{PHONE}</b>
      <small>{HOURS}</small>
    </a>
    <button class="burger" type="button" aria-expanded="false" aria-label="Меню">
      <i aria-hidden="true"></i>
    </button>
  </div>
</header>

<main id="main">
"""


FOOTER = f"""
</main>

<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div>
        <a class="logo" href="index.html" style="margin-bottom:1rem">
          <img class="logo__mark" src="assets/img/brand/logo-96.png" width="58" height="58" alt="">
          <span class="logo__text">РемКом<span>Строй</span></span>
        </a>
        <p style="color:var(--ink-2); font-size:.92rem; max-width:32ch">
          Натяжные потолки в Мурманске с 2008 года. Бесплатный замер, установка за один день,
          гарантия 10 лет на полотно.
        </p>
      </div>
      <div>
        <h4>Услуги</h4>
        <ul>
          <li><a href="potolki.html#matte">Матовые потолки</a></li>
          <li><a href="potolki.html#gloss">Глянцевые потолки</a></li>
          <li><a href="potolki.html#bath">Потолки для ванной</a></li>
          <li><a href="potolki.html#print">Фотопечать</a></li>
        </ul>
      </div>
      <div>
        <h4>Разделы</h4>
        <ul>
          <li><a href="index.html#calc">Калькулятор</a></li>
          <li><a href="raboty.html">Наши работы</a></li>
          <li><a href="otzyvy.html">Отзывы</a></li>
          <li><a href="index.html#faq">Вопросы и ответы</a></li>
          <li><a href="politika.html">Политика конфиденциальности</a></li>
        </ul>
      </div>
      <div>
        <h4>Контакты</h4>
        <ul>
          <li><a class="footer__phone" href="tel:{TEL}">{PHONE}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li style="color:var(--ink-2)">{ADDRESS}</li>
          <li style="color:var(--ink-2)">{HOURS}</li>
          <li><a href="{VK}" rel="noopener">Мы во ВКонтакте</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>&copy; <span data-year>2026</span> {LEGAL}, ИНН {INN}</span>
      <button class="viewport-switch" type="button" data-viewport-switch>
        <svg aria-hidden="true"><use href="#i-desktop"></use></svg>
        <span data-viewport-label>Полная версия</span>
      </button>
      <span>Цены на сайте не являются публичной офертой</span>
    </div>
  </div>
</footer>

<div class="grain" aria-hidden="true"></div>
<script src="assets/js/app.js?v={VER}" defer></script>
"""


def crumbs(label):
    return (f'<nav class="crumbs" aria-label="Хлебные крошки">'
            f'<a href="index.html">Главная</a>{icon("caret-right", 12, cls="")}'
            f'<span>{label}</span></nav>')


def zamer_form(form_id, page, prefix, heading='Записаться на замер'):
    return f"""        <form class="panel" action="api/send.php" method="post" data-ajax>
          <input type="hidden" name="form_id" value="{form_id}">
          <input type="hidden" name="page_url" value="{page}">
          <div class="honeypot" aria-hidden="true">
            <label for="{prefix}-website">Не заполняйте</label>
            <input type="text" id="{prefix}-website" name="website" tabindex="-1" autocomplete="off">
          </div>
          <h3 class="h3" style="margin-bottom:1.25rem">{heading}</h3>
          <div class="stack-sm">
            <div class="field">
              <label for="{prefix}-name">Ваше имя</label>
              <input type="text" id="{prefix}-name" name="name" autocomplete="name" data-validate="name" placeholder="Как к вам обращаться">
              <span class="field__error"></span>
            </div>
            <div class="field">
              <label for="{prefix}-phone">Телефон</label>
              <input type="tel" id="{prefix}-phone" name="phone" autocomplete="tel" data-validate="phone" placeholder="+7 (___) ___-__-__">
              <span class="field__error"></span>
            </div>
            <div class="field">
              <label for="{prefix}-address">Адрес замера</label>
              <input type="text" id="{prefix}-address" name="address" autocomplete="street-address" data-validate="text" placeholder="Улица, дом, квартира">
              <span class="field__error"></span>
            </div>
            <div class="field">
              <label for="{prefix}-comment">Удобное время</label>
              <input type="text" id="{prefix}-comment" name="comment" placeholder="Например: в субботу после 14:00">
              <span class="field__help">Не обязательно</span>
            </div>
            <label class="consent">
              <input type="checkbox" name="consent" value="1">
              <span>Я согласен(-на) на обработку персональных данных, <a href="politika.html">политика конфиденциальности</a></span>
            </label>
            <button class="btn btn--primary btn--block" type="submit">Записаться на замер</button>
          </div>
          <p class="form-status" role="status" aria-live="polite"></p>
        </form>"""


def cta_band(page, prefix):
    return f"""  <section class="section" id="zamer">
    <div class="wrap">
      <div class="cta-band reveal">
        <picture>
          <source type="image/webp" srcset="assets/img/portfolio/lg/work_montage.webp">
          <img class="cta-band__bg" src="assets/img/portfolio/lg/work_montage.jpg" width="1600" height="1600" loading="lazy" alt="">
        </picture>
        <div>
          <h2 class="h2">Замер бесплатный и ни к чему не обязывает</h2>
          <p>
            Замерщик приедет с образцами полотен, посчитает точную смету на месте и подберёт акцию.
            При заключении договора в день замера скидка ещё 5%.
          </p>
          <p style="margin-top:1.5rem">
            <a class="btn" href="tel:{TEL}" style="--btn-bg:transparent; --btn-fg:#fff; border-color:rgba(255,255,255,.45)">
              {icon('phone')}{PHONE}
            </a>
          </p>
        </div>
{zamer_form('Заявка на замер', page, prefix)}
      </div>
    </div>
  </section>
"""


def map_section(surface=True, lead='Офис в центре Мурманска. Заходите посмотреть образцы полотен вживую.'):
    """Блок с картой проезда. Используется и на главной, и на странице контактов."""
    cls = 'section--tight section--surface' if surface else 'section--tight'
    return f"""  <section class="{cls}" id="map">
    <div class="wrap">
      <div class="section-head reveal">
        <h2 class="h2">Как нас найти</h2>
        <p>{lead}</p>
      </div>

      <div class="map reveal-media">
        <iframe src="{MAP_EMBED}"
                title="Карта проезда: {ADDRESS}"
                loading="lazy"
                referrerpolicy="no-referrer-when-downgrade"
                allowfullscreen></iframe>
        <div class="map__bar">
          <p><b>АДРЕС ОФИСА</b>{ADDRESS}</p>
          <p><b>ЧАСЫ РАБОТЫ</b>{HOURS}</p>
          <a class="btn" href="{MAP_ROUTE}" target="_blank" rel="noopener">
            {icon('map-pin')}Построить маршрут
          </a>
        </div>
      </div>
    </div>
  </section>
"""


def quote_card(key, name, meta, text):
    return f"""        <figure class="quote">
          <span class="quote__mark" aria-hidden="true">&laquo;</span>
          <blockquote>{text}</blockquote>
          <figcaption class="quote__person">
            <img src="assets/img/reviews/sm/{key}.jpg" width="48" height="48" loading="lazy" alt="">
            <span><b>{name}</b><span>{meta}</span></span>
          </figcaption>
        </figure>"""


def faq_block():
    items = []
    for q, a in FAQ:
        items.append(f"""        <details class="faq__item">
          <summary>{q}{icon('caret-down', cls='')}</summary>
          <div class="faq__body">{a}</div>
        </details>""")
    return '\n'.join(items)


# ============================ СТРАНИЦЫ ============================

def hero_slider():
    """Карточки фактур в hero: листаются сами раз в несколько секунд и вручную."""
    slides = []
    for key, title, sub, img, w, h, size, text in TEXTURES:
        price = price_of(key)
        tag = (f'<p class="slide__price"><b>от {price} ₽</b><span>за м²</span></p>'
               if price else '')
        short = text.split('.')[0] + '.'
        slides.append(f"""          <a class="slide" href="potolki.html#{key}">
            <div class="ratio ratio--3x2">
              <picture>
                <source type="image/webp" srcset="assets/img/{sub}/sm/{img}.webp">
                <img src="assets/img/{sub}/sm/{img}.jpg" width="{w}" height="{h}" loading="lazy"
                     alt="{title} натяжные потолки">
              </picture>
            </div>
            <div class="slide__body">
              <h3>{title}</h3>
              <p>{short}</p>
              {tag}
            </div>
          </a>""")

    return f"""      <div class="hero__slider reveal" data-slider style="--d:260ms">
        <div class="slider__head">
          <h2>Фактуры и цены</h2>
          <div class="slider__nav">
            <div class="slider__dots" data-slider-dots aria-label="Позиция ленты"></div>
            <button type="button" data-slider-prev aria-label="Предыдущая фактура">{icon('caret-left', cls='')}</button>
            <button type="button" data-slider-next aria-label="Следующая фактура">{icon('caret-right', cls='')}</button>
          </div>
        </div>
        <div class="slider__track" data-slider-track>
{chr(10).join(slides)}
        </div>
      </div>"""


def page_index():
    adv = '\n'.join(f"""        <div class="adv__item">
          <span class="adv__icon">{icon(ic, 26, cls='')}</span>
          <div>
            <h3 class="h4">{title}</h3>
            <p>{text}</p>
          </div>
        </div>""" for ic, title, text in ADVANTAGES)

    steps = '\n'.join(f"""        <li class="steps__item">
          <span class="steps__badge" aria-hidden="true"></span>
          <h3>{title}</h3>
          <p>{text}</p>
        </li>""" for title, text in STEPS)

    promos = '\n'.join(f"""        <div class="promo">
          {icon(ic, 24, cls='')}
          <div><b>{title}</b><p>{text}</p></div>
        </div>""" for ic, title, text in PROMOS)

    reviews = '\n'.join(quote_card(*r) for r in REVIEWS_SHORT)

    bento_layout = ['bento__cell bento__cell--lg', 'bento__cell', 'bento__cell',
                    'bento__cell', 'bento__cell', 'bento__cell bento__cell--full']
    # на главной показываем шесть фактур, полный список на странице potolki.html
    bento_pick = [t for t in TEXTURES if t[0] != 'fabric']
    bento = []
    for (key, title, sub, img, w, h, size, text), cls in zip(bento_pick, bento_layout):
        use = 'sm' if 'full' not in cls and '--lg' not in cls else size
        price = price_of(key)
        tag = f'<span class="bento__price">от {price} ₽/м²</span>' if price else ''
        bento.append(f"""        <a class="{cls}" href="potolki.html#{key}">
          <picture>
            <source type="image/webp" srcset="assets/img/{sub}/{use}/{img}.webp">
            <img src="assets/img/{sub}/{use}/{img}.jpg" width="{w}" height="{h}" loading="lazy" alt="{title} натяжные потолки">
          </picture>
          <div class="bento__head"><h3 class="h3">{title}</h3>{tag}</div>
          <p>{text.split('.')[0]}.</p>
        </a>""")

    gallery = '\n'.join(f"""        <a class="shot" href="raboty.html">
          <picture><source type="image/webp" srcset="assets/img/portfolio/sm/{f}.webp">
          <img src="assets/img/portfolio/sm/{f}.jpg" width="{w}" height="{h}" loading="lazy" alt="{alt}"></picture>
        </a>""" for f, w, h, cat, alt in
        [s for s in SHOTS if s[0] in ('work_marble', 'work_reiki', 'files_12',
                                       'lines_triangle', 'files_16', 'files_11')])

    return head(
        f'Натяжные потолки в Мурманске от 190 ₽/м² | РемКомСтрой',
        'Натяжные потолки в Мурманске с 2008 года. Бесплатный замер, установка за один день, '
        f'гарантия 10 лет, фиксированная стоимость. Телефон {PHONE}.',
        '', canonical=''
    ) + f"""
  <section class="hero">
    <div class="aurora" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
    <div class="wrap hero__grid">
      <div>
        <h1 class="h1 reveal">Натяжные потолки в Мурманске</h1>
        <p class="lead reveal" style="--d:90ms; margin-top:1.5rem">
          Бесплатный замер и установка за один день. Гарантия 10 лет
          на полотно, стоимость фиксируем в договоре.
        </p>
        <div class="hero__cta reveal" style="--d:180ms">
          <a class="btn btn--primary btn--lg" href="#zamer">{icon('ruler')}Вызвать замерщика</a>
          <a class="btn btn--lg" href="#calc">{icon('calculator')}Рассчитать стоимость</a>
        </div>
      </div>

      <div class="hero__media reveal-media" style="--d:120ms">
        <picture>
          <source type="image/webp"
                  srcset="assets/img/portfolio/sm/work_marble.webp 800w, assets/img/portfolio/lg/work_marble.webp 1600w"
                  sizes="(max-width: 900px) 100vw, 45vw">
          <img src="assets/img/portfolio/lg/work_marble.jpg" width="1600" height="1200" fetchpriority="high"
               alt="Натяжной потолок с контурной подсветкой в комнате с мраморной отделкой">
        </picture>
        <div class="hero__badge">
          <strong>от 190 ₽</strong>
          <span>за м² полотна.<br>Точную цену назовёт замерщик</span>
        </div>
      </div>
    </div>

    <div class="wrap">
{hero_slider()}
    </div>
  </section>

  <section class="section--tight">
    <div class="wrap">
      <div class="stats reveal" data-stagger="80">
        <div class="stats__item"><strong><span data-count="2008">2008</span></strong><span>работаем с этого года</span></div>
        <div class="stats__item"><strong><span data-count="10">10</span> лет</strong><span>гарантия на полотно</span></div>
        <div class="stats__item"><strong><span data-count="1">1</span> день</strong><span>обычно занимает монтаж</span></div>
        <div class="stats__item"><strong><span data-count="0">0</span> ₽</strong><span>замер и расчёт сметы</span></div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head reveal">
        <h2 class="h2">Почему выбирают нас</h2>
        <p>Шесть причин, по которым в Мурманске обращаются именно к нам.</p>
      </div>
      <div class="adv reveal" data-stagger="60">
{adv}
      </div>
    </div>
  </section>

  <section class="section section--surface" id="calc">
    <div class="wrap">
      <div class="section-head reveal">
        <span class="eyebrow">Расчёт стоимости</span>
        <h2 class="h2">Посчитайте свой потолок сами</h2>
        <p>
          Укажите параметры комнаты, сумма пересчитается сразу. Расчёт предварительный:
          точную стоимость назовёт замерщик, выезд бесплатный.
        </p>
      </div>

      <div class="calc">
        <form class="panel reveal" id="calc-form" novalidate>
          <div class="calc__fields">
            <div class="field">
              <label for="area">Площадь потолка, м²</label>
              <input type="number" id="area" name="area" min="1" max="500" step="0.5" value="18" inputmode="decimal">
              <span class="field__help">Длина × ширина комнаты</span>
            </div>
            <div class="field">
              <label for="corners">Количество углов</label>
              <input type="number" id="corners" name="corners" min="0" max="40" step="1" value="4" inputmode="numeric">
              <span class="field__help">В обычной комнате их 4</span>
            </div>
            <div class="field">
              <label for="lights">Светильников</label>
              <input type="number" id="lights" name="lights" min="0" max="60" step="1" value="4" inputmode="numeric">
              <span class="field__help">Считаем врезку и подключение</span>
            </div>
            <div class="field">
              <label for="pipes">Труб для обвода</label>
              <input type="number" id="pipes" name="pipes" min="0" max="30" step="1" value="0" inputmode="numeric">
              <span class="field__help">Стояки отопления, вентиляция</span>
            </div>
            <div class="field field--wide">
              <label for="texture">Фактура полотна</label>
              <select id="texture" name="texture">
                <option value="matte" selected>Матовое</option>
                <option value="gloss">Глянцевое</option>
                <option value="satin">Сатиновое</option>
                <option value="fabric">Тканевое бесшовное</option>
                <option value="print">С фотопечатью</option>
                <option value="starrySky">Звёздное небо</option>
              </select>
            </div>
          </div>
        </form>

        <div class="calc__result">
          <div class="panel reveal" id="calc-result" style="--d:100ms">
            <span class="eyebrow" style="margin-bottom:.5rem">Предварительно</span>
            <p class="result__total num" data-total data-pending="true">0 ₽</p>
            <ul class="result__rows" data-rows></ul>

            <form action="api/send.php" method="post" data-ajax data-attach-calc="1" style="margin-top:1.75rem">
              <input type="hidden" name="form_id" value="Заявка из калькулятора">
              <input type="hidden" name="page_url" value="index.html#calc">
              <input type="hidden" name="calc_summary" id="calc-summary">
              <div class="honeypot" aria-hidden="true">
                <label for="website-calc">Не заполняйте</label>
                <input type="text" id="website-calc" name="website" tabindex="-1" autocomplete="off">
              </div>

              <div class="stack-sm">
                <div class="field">
                  <label for="calc-name">Ваше имя</label>
                  <input type="text" id="calc-name" name="name" autocomplete="name" data-validate="name" placeholder="Как к вам обращаться">
                  <span class="field__error"></span>
                </div>
                <div class="field">
                  <label for="calc-phone">Телефон</label>
                  <input type="tel" id="calc-phone" name="phone" autocomplete="tel" data-validate="phone" placeholder="+7 (___) ___-__-__">
                  <span class="field__error"></span>
                </div>
                <label class="consent">
                  <input type="checkbox" name="consent" value="1">
                  <span>Я согласен(-на) на обработку персональных данных, <a href="politika.html">политика конфиденциальности</a></span>
                </label>
                <button class="btn btn--primary btn--block" type="submit">Отправить расчёт и подобрать акцию</button>
              </div>
              <p class="form-status" role="status" aria-live="polite"></p>
            </form>

            <p class="note">
              Расчёт ориентировочный и не является офертой. Стоимость фиксируется после замера
              и в процессе работы не меняется.
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head reveal">
        <h2 class="h2">Фактуры и цены за метр</h2>
        <p>
          Цены стартовые, за м² полотна вместе с профилем и монтажом. Замерщик привозит
          образцы, чтобы вы посмотрели фактуру вживую до заказа.
        </p>
      </div>
      <div class="bento reveal" data-stagger="70">
{chr(10).join(bento)}
      </div>
    </div>
  </section>

  <section class="section section--surface">
    <div class="wrap">
      <div class="section-head reveal">
        <h2 class="h2">Как проходит работа</h2>
        <p>Пять шагов от заявки до готового потолка.</p>
      </div>
      <ol class="steps">
{steps}
      </ol>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head reveal">
        <span class="eyebrow">Специальные предложения</span>
        <h2 class="h2">Действующие акции</h2>
      </div>
      <div class="promos reveal" data-stagger="70">
{promos}
      </div>
      <p class="note">Акции не суммируются. Менеджер подберёт самую выгодную для вашего заказа.</p>
    </div>
  </section>

  <section class="section section--surface">
    <div class="wrap">
      <div class="section-head reveal">
        <h2 class="h2">Отзывы наших клиентов</h2>
      </div>
    </div>
    <div class="wrap">
      <div class="rail reveal">
{reviews}
      </div>
      <p style="margin-top:1.5rem"><a class="btn" href="otzyvy.html">Все отзывы{icon('arrow-right')}</a></p>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head reveal">
        <h2 class="h2">Наши работы в Мурманске</h2>
        <p>Световые линии, парящие и многоуровневые потолки, фотопечать.</p>
      </div>
      <div class="gallery reveal" data-stagger="60">
{gallery}
      </div>
      <p style="margin-top:1.75rem"><a class="btn" href="raboty.html">Смотреть все работы{icon('arrow-right')}</a></p>
    </div>
  </section>

  <section class="section section--surface" id="faq">
    <div class="wrap">
      <div class="section-head reveal">
        <h2 class="h2">Часто задаваемые вопросы</h2>
        <p>Если нужного вопроса тут нет, позвоните нам, ответим по телефону.</p>
      </div>
      <div class="faq reveal" data-stagger="45">
{faq_block()}
      </div>
    </div>
  </section>

{cta_band('index.html#zamer', 'z')}
{map_section(surface=True, lead='Офис в центре Мурманска, на улице Полярные Зори. Можно заехать и посмотреть образцы полотен вживую.')}
""" + FOOTER + f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "HomeAndConstructionBusiness",
  "name": "РемКомСтрой",
  "description": "Натяжные потолки в Мурманске с 2008 года. Бесплатный замер, гарантия 10 лет.",
  "telephone": "{PHONE}",
  "email": "{EMAIL}",
  "url": "https://remkomstroi.ru/",
  "image": "https://remkomstroi.ru/assets/img/portfolio/lg/work_marble.jpg",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "ул. Полярные Зори, 11",
    "addressLocality": "Мурманск",
    "addressCountry": "RU"
  }},
  "openingHoursSpecification": {{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
    "opens": "09:00",
    "closes": "20:00"
  }},
  "sameAs": ["{VK}"]
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
""" + ',\n'.join(
        '    {"@type": "Question", "name": "%s", "acceptedAnswer": {"@type": "Answer", "text": "%s"}}'
        % (q, __import__('re').sub(r'<[^>]+>', ' ', a).replace('"', "'").strip())
        for q, a in FAQ) + """
  ]
}
</script>
<script src="assets/js/prices.js?v={VER}" defer></script>
<script src="assets/js/calc.js?v={VER}" defer></script>
</body>
</html>
"""


def page_potolki():
    cards = []
    for key, title, sub, img, w, h, size, text in TEXTURES:
        price = price_of(key)
        cost = (f'<p class="price-card__price"><b>от {price} ₽</b><span>за м²</span></p>'
                if price else '')
        cards.append(f"""        <article class="tile tile--media" id="{key}">
          <div class="ratio ratio--4x3">
            <picture>
              <source type="image/webp" srcset="assets/img/{sub}/sm/{img}.webp">
              <img src="assets/img/{sub}/sm/{img}.jpg" width="{w}" height="{h}" loading="lazy"
                   alt="{title} натяжные потолки">
            </picture>
          </div>
          <div class="tile__body">
            <h3 class="h3">{title}</h3>
            <p style="color:var(--ink-2); font-size:.92rem">{text}</p>
            {cost}
          </div>
        </article>""")

    return head(
        'Натяжные потолки в Мурманске: виды, фактуры, цены | РемКомСтрой',
        'Матовые, глянцевые, сатиновые и влагостойкие натяжные потолки, фотопечать и звёздное небо '
        'в Мурманске. Гарантия 10 лет, бесплатный замер, цена от 190 ₽ за м².',
        'potolki', canonical='potolki.html'
    ) + f"""
  <section class="wrap page-head">
    {crumbs('Натяжные потолки')}
    <h1 class="h1 reveal">Натяжные потолки: фактуры и решения</h1>
    <p class="lead reveal" style="--d:80ms; margin-top:1.25rem">
      Подберём полотно под конкретную комнату. Замерщик привезёт образцы, чтобы вы
      увидели фактуру вживую до заказа.
    </p>
  </section>

  <section class="section--tight">
    <div class="wrap">
      <div class="tiles reveal" data-stagger="70">
{chr(10).join(cards)}
      </div>
    </div>
  </section>

  <section class="section section--surface">
    <div class="wrap">
      <div class="section-head reveal">
        <span class="eyebrow">Цены и условия</span>
        <h2 class="h2">Что входит в стоимость</h2>
        <p>
          В цену входит полотно, профиль и монтаж. Точную смету считает замерщик на месте,
          после чего стоимость фиксируется в договоре и больше не меняется.
        </p>
      </div>
      <div class="tiles reveal" data-stagger="70">
        <div class="tile tile--accent">
          <strong>от 190 ₽</strong>
          <b>за м² полотна</b>
          <p>Стартовая цена, указанная на сайте компании.</p>
        </div>
        <div class="tile">
          <strong>0 ₽</strong>
          <b>замер и смета</b>
          <p>Замерщик приезжает бесплатно и привозит образцы.</p>
        </div>
        <div class="tile">
          <strong>10 лет</strong>
          <b>гарантия на полотно</b>
          <p>Плюс год гарантии на монтажные работы.</p>
        </div>
        <div class="tile">
          <strong>2-6 ч</strong>
          <b>монтаж одной комнаты</b>
          <p>Сложные объекты с подсветкой занимают до дня.</p>
        </div>
      </div>
      <p style="margin-top:1.75rem; text-align:center">
        <a class="btn btn--primary btn--lg" href="index.html#calc">{icon('calculator')}Рассчитать свой потолок</a>
      </p>
    </div>
  </section>

{cta_band('potolki.html', 'pt')}
""" + FOOTER + '</body>\n</html>\n'


def page_raboty():
    chips = '\n'.join(
        f'        <button class="chip" type="button" data-filter="{k}"'
        f' aria-pressed="{"true" if k == "all" else "false"}">{lbl}</button>'
        for k, lbl in CATS)
    shots = '\n'.join(f"""        <button class="shot" type="button" data-cat="{cat}" data-full="assets/img/portfolio/lg/{f}.jpg">
          <picture>
            <source type="image/webp" srcset="assets/img/portfolio/sm/{f}.webp">
            <img src="assets/img/portfolio/sm/{f}.jpg" width="{w}" height="{h}" loading="lazy" alt="{alt}">
          </picture>
          <span class="shot__tag">{alt}</span>
        </button>""" for f, w, h, cat, alt in SHOTS)

    return head(
        'Наши работы: натяжные потолки в Мурманске | РемКомСтрой',
        'Фотографии выполненных натяжных потолков в Мурманске: световые линии, парящие '
        'и многоуровневые потолки, фотопечать, звёздное небо.',
        'raboty', canonical='raboty.html'
    ) + f"""
  <section class="wrap page-head">
    {crumbs('Наши работы')}
    <h1 class="h1 reveal">Наши работы в Мурманске</h1>
    <p class="lead reveal" style="--d:80ms; margin-top:1.25rem">
      Показано <span data-shown class="num">{len(SHOTS)}</span> объектов.
      Нажмите на фото, чтобы открыть его целиком.
    </p>
  </section>

  <section class="section--tight">
    <div class="wrap">
      <div class="filters reveal">
{chips}
      </div>
      <div class="gallery reveal" id="gallery" data-stagger="45">
{shots}
      </div>
      <p id="gallery-empty" class="note" hidden>В этой категории пока нет фотографий.</p>
    </div>
  </section>

  <dialog class="lightbox" id="lightbox" aria-label="Просмотр фотографии">
    <button class="lightbox__close" type="button" data-lb-close aria-label="Закрыть">{icon('x', 20, cls='')}</button>
    <div>
      <div class="lightbox__stage"><img data-lb-img src="" alt=""></div>
      <div class="lightbox__bar">
        <p data-lb-cap></p>
        <div class="lightbox__nav">
          <span class="num" data-lb-pos style="align-self:center; margin-right:.5rem"></span>
          <button type="button" data-lb-prev aria-label="Предыдущее фото">{icon('caret-left', 20, cls='')}</button>
          <button type="button" data-lb-next aria-label="Следующее фото">{icon('caret-right', 20, cls='')}</button>
        </div>
      </div>
    </div>
  </dialog>

{cta_band('raboty.html', 'rb')}
""" + FOOTER + '<script src="assets/js/gallery.js?v={VER}" defer></script>\n</body>\n</html>\n'


def page_otzyvy():
    main = '\n'.join(quote_card(*r) for r in REVIEWS_MAIN)
    extra = '\n'.join(f"""        <figure class="quote">
          <span class="quote__mark" aria-hidden="true">&laquo;</span>
          <blockquote>{text}</blockquote>
          <figcaption><b>{name}</b>{meta}</figcaption>
        </figure>""" for name, meta, text in REVIEWS_EXTRA)

    return head(
        'Отзывы о компании РемКомСтрой, Мурманск',
        'Отзывы заказчиков о натяжных потолках от компании РемКомСтрой в Мурманске.',
        'otzyvy', canonical='otzyvy.html'
    ) + f"""
  <section class="wrap page-head">
    {crumbs('Отзывы')}
    <h1 class="h1 reveal">Отзывы наших клиентов</h1>
    <p class="lead reveal" style="--d:80ms; margin-top:1.25rem">
      Публикуем отзывы как есть, без правок.
    </p>
  </section>

  <section class="section--tight">
    <div class="wrap">
      <div class="gallery reveal" data-stagger="70" style="align-items:start">
{main}
      </div>
    </div>
  </section>

  <section class="section--tight">
    <div class="wrap">
      <h2 class="h3 reveal" style="margin-bottom:1.5rem">Ещё отзывы о наших потолках</h2>
      <div class="gallery reveal" data-stagger="70" style="align-items:start">
{extra}
      </div>
      <p class="note" style="max-width:62ch">
        Свежие фото объектов и новые отзывы выкладываем в группе
        <a href="{VK}" rel="noopener" class="text-accent">ВКонтакте</a>,
        там же можно задать вопрос в сообщения.
      </p>
    </div>
  </section>

{cta_band('otzyvy.html', 'ot')}
""" + FOOTER + '</body>\n</html>\n'


def page_kontakty():
    return head(
        f'Контакты РемКомСтрой: {ADDRESS}',
        f'Телефон, адрес и часы работы компании РемКомСтрой в Мурманске. '
        f'Запись на бесплатный замер натяжных потолков.',
        'kontakty', canonical='kontakty.html'
    ) + f"""
  <section class="wrap page-head">
    {crumbs('Контакты')}
    <h1 class="h1 reveal">Контакты</h1>
    <p class="lead reveal" style="--d:80ms; margin-top:1.25rem">
      Звоните {HOURS.lower()}. Консультация и выезд замерщика бесплатные.
    </p>
  </section>

  <section class="section--tight">
    <div class="wrap">
      <div class="tiles reveal" data-stagger="70">
        <div class="tile tile--accent">
          {icon('phone', 24, cls='', style='color:var(--accent-text)')}
          <b>Телефон</b>
          <p style="font-size:1.15rem; font-weight:700; color:var(--ink)">
            <a href="tel:{TEL}" style="text-decoration:none">{PHONE}</a>
          </p>
          <p>Замеры, расчёты, любые вопросы по потолкам.</p>
        </div>
        <div class="tile">
          {icon('envelope-simple', 24, cls='', style='color:var(--accent-text)')}
          <b>Почта</b>
          <p style="font-weight:700; color:var(--ink)">
            <a href="mailto:{EMAIL}" style="text-decoration:none">{EMAIL}</a>
          </p>
          <p>Сюда приходят заявки с сайта.</p>
        </div>
        <div class="tile">
          {icon('map-pin', 24, cls='', style='color:var(--accent-text)')}
          <b>Адрес</b>
          <p>{ADDRESS}</p>
          <p>Здесь же можно посмотреть образцы полотен.</p>
        </div>
        <div class="tile">
          {icon('clock', 24, cls='', style='color:var(--accent-text)')}
          <b>Часы работы</b>
          <p>{HOURS}</p>
          <p>В воскресенье не работаем.</p>
        </div>
      </div>

      <p class="note" style="max-width:62ch">
        {LEGAL}, ИНН {INN}.
        Мы во ВКонтакте: <a href="{VK}" rel="noopener" class="text-accent">vk.com/remkomstroy</a>
      </p>
    </div>
  </section>

{map_section(surface=False)}

{cta_band('kontakty.html', 'kt')}
""" + FOOTER + '</body>\n</html>\n'


def page_politika():
    return head(
        'Политика конфиденциальности | РемКомСтрой',
        'Политика обработки персональных данных на сайте компании РемКомСтрой.',
        '', canonical='politika.html'
    ) + f"""
  <section class="wrap page-head">
    {crumbs('Политика конфиденциальности')}
    <h1 class="h1 reveal">Политика конфиденциальности</h1>
  </section>

  <section class="section--tight">
    <div class="wrap prose reveal">
      <p>
        Настоящая политика описывает, как {LEGAL} (ИНН {INN}, {ADDRESS})
        обрабатывает персональные данные посетителей сайта. Отправляя любую форму
        на сайте, вы подтверждаете согласие с этой политикой.
      </p>

      <h2>Какие данные мы собираем</h2>
      <ul>
        <li>имя, которое вы указали в форме;</li>
        <li>номер телефона;</li>
        <li>адрес объекта, если вы записываетесь на замер;</li>
        <li>комментарий и параметры расчёта, если вы заполняли калькулятор;</li>
        <li>технические данные: IP-адрес и страница, с которой отправлена заявка.</li>
      </ul>

      <h2>Зачем они нужны</h2>
      <p>
        Данные используются только чтобы связаться с вами по вашей заявке: перезвонить,
        согласовать время замера, посчитать смету. Мы не передаём их третьим лицам,
        не продаём и не используем для рассылок, на которые вы не подписывались.
      </p>

      <h2>Сколько мы их храним</h2>
      <p>
        Заявки хранятся, пока это нужно для работы по вашему заказу и выполнения гарантийных
        обязательств. Вы можете в любой момент попросить удалить свои данные, позвонив
        по телефону <a href="tel:{TEL}">{PHONE}</a> или написав на
        <a href="mailto:{EMAIL}">{EMAIL}</a>.
      </p>

      <h2>Как мы их защищаем</h2>
      <p>
        Доступ к заявкам есть только у сотрудников, которые обрабатывают заказы.
        Данные передаются с сайта на почту компании и не публикуются.
      </p>

      <h2>Файлы cookie</h2>
      <p>
        Сайт не использует рекламные и аналитические cookie. Технические файлы, необходимые
        для работы страниц, можно запретить в настройках браузера.
      </p>

      <h2>Ваши права</h2>
      <p>
        Вы вправе запросить, какие ваши данные у нас есть, потребовать их уточнить или удалить,
        а также отозвать согласие на обработку. Для этого достаточно позвонить или написать
        по контактам выше.
      </p>
    </div>
  </section>
""" + FOOTER + '</body>\n</html>\n'


def page_spasibo():
    return head(
        'Заявка отправлена | РемКомСтрой',
        'Заявка принята. Мы свяжемся с вами в ближайшее время.',
        ''
    ) + f"""
  <section class="wrap page-head" style="min-height:52vh; display:grid; align-content:center">
    <div class="reveal" style="max-width:52ch">
      {icon('seal-check', 52, cls='', style='color:var(--accent-text)')}
      <h1 class="h1" style="margin-top:1.25rem">Заявка принята</h1>
      <p class="lead" style="margin-top:1.25rem">
        Спасибо. Мы свяжемся с вами в ближайшее время, {HOURS.lower()}.
        Если нужно срочно, позвоните сами: <a href="tel:{TEL}" class="text-accent">{PHONE}</a>.
      </p>
      <p style="margin-top:2rem; display:flex; gap:.85rem; flex-wrap:wrap">
        <a class="btn btn--primary" href="index.html">На главную</a>
        <a class="btn" href="raboty.html">Посмотреть работы</a>
      </p>
    </div>
  </section>
""" + FOOTER + '</body>\n</html>\n'


PAGES = {
    'index.html': page_index,
    'potolki.html': page_potolki,
    'raboty.html': page_raboty,
    'otzyvy.html': page_otzyvy,
    'kontakty.html': page_kontakty,
    'politika.html': page_politika,
    'spasibo.html': page_spasibo,
}

sprite = open(os.path.join(ROOT, 'assets/img/icons.svg'), encoding='utf-8').read().strip()

for filename, builder in PAGES.items():
    html = builder().replace('<!--SPRITE-->', sprite).replace('{VER}', VER)
    for bad in ('\u2014', '\u2013'):
        assert bad not in html, f'{filename}: найдено тире {bad!r}'
    with open(os.path.join(ROOT, filename), 'w', encoding='utf-8') as fh:
        fh.write(html)
    print('готово', filename, len(html), 'байт')
