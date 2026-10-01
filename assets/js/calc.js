/* Калькулятор стоимости натяжного потолка.
   Ставки берутся из prices.js — здесь только арифметика и вывод. */

(() => {
  'use strict';

  const form = document.querySelector('#calc-form');
  const out = document.querySelector('#calc-result');
  if (!form || !out || !window.RKSPrices) return;

  const P = window.RKSPrices;

  const totalEl = out.querySelector('[data-total]');
  const rowsEl = out.querySelector('[data-rows]');
  const hiddenEl = document.querySelector('#calc-summary');

  const money = (n) => new Intl.NumberFormat('ru-RU').format(Math.round(n)) + ' ₽';
  const num = (name, fallback = 0) => {
    const v = Number(form.elements[name] ? form.elements[name].value : NaN);
    return Number.isFinite(v) && v >= 0 ? v : fallback;
  };

  let last = null;

  const compute = () => {
    const area = num('area');
    const corners = num('corners');
    const lights = num('lights');
    const pipes = num('pipes');
    const key = form.elements.texture ? form.elements.texture.value : 'matte';
    const texture = P.textures[key] || P.textures.matte;

    if (area <= 0) return null;

    const rows = [];

    const canvas = area * texture.pricePerM2;
    rows.push({
      label: `${texture.label}, ${area} м² × ${money(texture.pricePerM2)}`,
      value: canvas
    });

    const extraCorners = Math.max(0, corners - P.cornersFree);
    if (extraCorners > 0) {
      rows.push({
        label: `Углы свыше ${P.cornersFree}: ${extraCorners} × ${money(P.cornerPrice)}`,
        value: extraCorners * P.cornerPrice
      });
    }

    if (lights > 0) {
      rows.push({
        label: `Врезка светильников: ${lights} × ${money(P.lightPrice)}`,
        value: lights * P.lightPrice
      });
    }

    if (pipes > 0) {
      rows.push({
        label: `Обвод труб: ${pipes} × ${money(P.pipePrice)}`,
        value: pipes * P.pipePrice
      });
    }

    const subtotal = rows.reduce((s, r) => s + r.value, 0);

    const giftM2 = Math.floor(area / P.giftEveryM2);
    const gift = giftM2 * texture.pricePerM2;
    if (gift > 0) {
      rows.push({
        label: `Каждый 10-й м² в подарок: ${giftM2} м²`,
        value: -gift,
        discount: true
      });
    }

    const raw = subtotal - gift;
    const total = Math.max(raw, P.minOrder);

    return {
      rows,
      total,
      minApplied: raw < P.minOrder,
      params: {
        'Площадь': `${area} м²`,
        'Углов': String(corners),
        'Светильников': String(lights),
        'Труб': String(pipes),
        'Фактура': texture.label
      }
    };
  };

  const render = () => {
    const r = compute();
    last = r;

    if (!r) {
      totalEl.textContent = '0 ₽';
      totalEl.dataset.pending = 'true';
      rowsEl.innerHTML = '<li><span>Укажите площадь потолка</span><span></span></li>';
      if (hiddenEl) hiddenEl.value = '';
      return;
    }

    totalEl.dataset.pending = 'false';
    totalEl.textContent = money(r.total);

    rowsEl.innerHTML = r.rows.map((row) => (
      `<li${row.discount ? ' data-discount="true"' : ''}>` +
      `<span>${row.label}</span>` +
      `<span>${row.value < 0 ? '−' + money(-row.value) : money(row.value)}</span>` +
      '</li>'
    )).join('') + (r.minApplied
      ? `<li><span>Минимальная сумма заказа</span><span>${money(P.minOrder)}</span></li>`
      : '');

    if (hiddenEl) hiddenEl.value = summary();
  };

  const summary = () => {
    if (!last) return 'Расчёт не заполнен';
    const params = Object.entries(last.params).map(([k, v]) => `${k}: ${v}`).join('; ');
    const detail = last.rows
      .map((row) => `${row.label} = ${row.value < 0 ? '−' : ''}${Math.abs(Math.round(row.value))} руб.`)
      .join('\n');
    return `${params}\n\n${detail}\n\nИТОГО: ${Math.round(last.total)} руб.`;
  };

  window.RKSCalc = { summary, recompute: render };

  form.addEventListener('input', render);
  form.addEventListener('change', render);
  render();
})();
