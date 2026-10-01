/* Портфолио: фильтры по типу потолка и просмотр фото во весь экран. */

(() => {
  'use strict';

  const grid = document.querySelector('#gallery');
  if (!grid) return;

  const shots = Array.from(grid.querySelectorAll('.shot'));
  const chips = Array.from(document.querySelectorAll('.filters .chip'));
  const empty = document.querySelector('#gallery-empty');
  const counter = document.querySelector('[data-shown]');

  /* ---------- фильтры ---------- */

  const apply = (filter) => {
    let shown = 0;

    shots.forEach((shot) => {
      const match = filter === 'all' || shot.dataset.cat === filter;
      shot.hidden = !match;
      if (match) shown += 1;
    });

    chips.forEach((chip) => {
      chip.setAttribute('aria-pressed', String(chip.dataset.filter === filter));
    });

    if (counter) counter.textContent = String(shown);
    if (empty) empty.hidden = shown > 0;
  };

  chips.forEach((chip) => {
    chip.addEventListener('click', () => apply(chip.dataset.filter));
  });

  apply('all');

  /* ---------- лайтбокс ---------- */

  const box = document.querySelector('#lightbox');
  if (!box) return;

  const boxImg = box.querySelector('[data-lb-img]');
  const boxCap = box.querySelector('[data-lb-cap]');
  const boxPos = box.querySelector('[data-lb-pos]');

  let visible = [];
  let index = 0;

  const show = (i) => {
    if (!visible.length) return;
    index = (i + visible.length) % visible.length;

    const shot = visible[index];
    const img = shot.querySelector('img');
    const full = shot.dataset.full || img.src;

    boxImg.src = full;
    boxImg.alt = img.alt;
    boxCap.textContent = img.alt;
    boxPos.textContent = `${index + 1} из ${visible.length}`;
  };

  const open = (shot) => {
    visible = shots.filter((s) => !s.hidden);
    const start = visible.indexOf(shot);
    show(start < 0 ? 0 : start);

    if (typeof box.showModal === 'function') {
      box.showModal();
    } else {
      box.setAttribute('open', '');
    }
  };

  shots.forEach((shot) => {
    shot.addEventListener('click', (e) => {
      e.preventDefault();
      open(shot);
    });
  });

  box.querySelector('[data-lb-prev]').addEventListener('click', () => show(index - 1));
  box.querySelector('[data-lb-next]').addEventListener('click', () => show(index + 1));
  box.querySelector('[data-lb-close]').addEventListener('click', () => box.close());

  box.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') { e.preventDefault(); show(index - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); show(index + 1); }
  });

  // клик по затемнённому фону закрывает
  box.addEventListener('click', (e) => {
    if (e.target === box) box.close();
  });
})();
