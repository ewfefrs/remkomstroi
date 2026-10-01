/* РемКомСтрой — общие скрипты: навигация, появление блоков, счётчики, формы.
   Скролл-слушателей нет: всё на IntersectionObserver. */

(() => {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- мобильное меню ---------- */

  const burger = document.querySelector('.burger');
  const nav = document.querySelector('.nav');

  if (burger && nav) {
    const setOpen = (open) => {
      burger.setAttribute('aria-expanded', String(open));
      nav.dataset.open = String(open);
    };

    burger.addEventListener('click', () => {
      setOpen(burger.getAttribute('aria-expanded') !== 'true');
    });

    nav.addEventListener('click', (e) => {
      if (e.target.closest('a')) setOpen(false);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') setOpen(false);
    });

    // при возврате на десктоп меню не должно остаться «открытым»
    window.matchMedia('(min-width: 1001px)').addEventListener('change', (e) => {
      if (e.matches) setOpen(false);
    });
  }

  /* ---------- рамка у залипшей шапки ---------- */

  const header = document.querySelector('.header');
  const sentinel = document.querySelector('#top-sentinel');

  if (header && sentinel && 'IntersectionObserver' in window) {
    new IntersectionObserver(
      ([entry]) => { header.dataset.stuck = String(!entry.isIntersecting); },
      { threshold: 0 }
    ).observe(sentinel);
  }

  /* ---------- появление блоков ---------- */

  const revealables = document.querySelectorAll('.reveal, .reveal-media, .steps__item');

  if (!('IntersectionObserver' in window) || reduceMotion) {
    revealables.forEach((el) => el.classList.add('is-visible'));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    revealables.forEach((el) => io.observe(el));

    /* Предохранитель: если через 1.2 с ни один блок так и не открылся, значит
       IntersectionObserver в этом окружении не сработал. Показываем всё,
       чтобы пользователь ни при каких условиях не увидел пустую страницу. */
    setTimeout(() => {
      if (!document.querySelector('.is-visible')) {
        revealables.forEach((el) => el.classList.add('is-visible'));
      }
    }, 1200);

    // стаггер внутри групп
    document.querySelectorAll('[data-stagger]').forEach((group) => {
      const step = Number(group.dataset.stagger) || 70;
      Array.from(group.children).forEach((child, i) => {
        child.style.setProperty('--d', `${i * step}ms`);
      });
    });
  }

  /* ---------- счётчики ---------- */

  const counters = document.querySelectorAll('[data-count]');

  if (counters.length) {
    const run = (el) => {
      const target = Number(el.dataset.count);
      if (!Number.isFinite(target)) return;

      if (reduceMotion) { el.textContent = String(target); return; }

      const duration = 1100;
      const start = performance.now();

      const frame = (now) => {
        const p = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = String(Math.round(target * eased));
        if (p < 1) requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    };

    if (!('IntersectionObserver' in window)) {
      counters.forEach((el) => { el.textContent = el.dataset.count; });
    } else {
      const co = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          run(entry.target);
          co.unobserve(entry.target);
        });
      }, { threshold: 0.5 });
      counters.forEach((el) => co.observe(el));
    }
  }

  /* ---------- телефонная маска ---------- */

  document.querySelectorAll('input[type="tel"]').forEach((input) => {
    const format = (raw) => {
      let d = raw.replace(/\D/g, '');
      if (d.startsWith('8')) d = '7' + d.slice(1);
      if (!d.startsWith('7')) d = '7' + d;
      d = d.slice(0, 11);

      let out = '+7';
      if (d.length > 1) out += ' (' + d.slice(1, 4);
      if (d.length >= 5) out += ') ' + d.slice(4, 7);
      if (d.length >= 8) out += '-' + d.slice(7, 9);
      if (d.length >= 10) out += '-' + d.slice(9, 11);
      return out;
    };

    input.addEventListener('input', () => {
      const atEnd = input.selectionStart === input.value.length;
      input.value = format(input.value);
      if (atEnd) input.setSelectionRange(input.value.length, input.value.length);
    });

    input.addEventListener('focus', () => {
      if (!input.value) input.value = '+7 (';
    });

    input.addEventListener('blur', () => {
      if (input.value.replace(/\D/g, '').length <= 1) input.value = '';
    });
  });

  /* ---------- отправка форм ---------- */

  const digits = (v) => (v || '').replace(/\D/g, '');

  const validate = (form) => {
    let ok = true;

    form.querySelectorAll('[data-validate]').forEach((input) => {
      const field = input.closest('.field');
      const box = field ? field.querySelector('.field__error') : null;
      const kind = input.dataset.validate;
      const value = input.value.trim();
      let msg = '';

      if (!value) {
        msg = 'Заполните поле';
      } else if (kind === 'phone' && digits(value).length !== 11) {
        msg = 'Введите телефон полностью';
      } else if (kind === 'name' && value.length < 2) {
        msg = 'Слишком короткое имя';
      }

      if (field) field.dataset.invalid = String(Boolean(msg));
      if (box) box.textContent = msg;
      if (msg) ok = false;
    });

    const consent = form.querySelector('input[name="consent"]');
    const status = form.querySelector('.form-status');

    if (consent && !consent.checked) {
      if (status) {
        status.dataset.state = 'error';
        status.textContent = 'Нужно согласие на обработку персональных данных.';
      }
      ok = false;
    }

    return ok;
  };

  document.querySelectorAll('form[data-ajax]').forEach((form) => {
    const status = form.querySelector('.form-status');
    const button = form.querySelector('button[type="submit"]');
    const label = button ? button.innerHTML : '';

    form.querySelectorAll('[data-validate]').forEach((input) => {
      input.addEventListener('input', () => {
        const field = input.closest('.field');
        if (field && field.dataset.invalid === 'true') {
          field.dataset.invalid = 'false';
          const box = field.querySelector('.field__error');
          if (box) box.textContent = '';
        }
      });
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (status) { status.dataset.state = ''; status.textContent = ''; }
      if (!validate(form)) return;

      if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner" aria-hidden="true"></span> Отправляем';
      }

      const data = new FormData(form);

      // расчёт калькулятора уезжает вместе с заявкой
      if (form.dataset.attachCalc && window.RKSCalc) {
        data.set('calc_summary', window.RKSCalc.summary());
      }

      try {
        const res = await fetch(form.action, {
          method: 'POST',
          body: data,
          headers: { 'Accept': 'application/json' }
        });

        let payload = null;
        try { payload = await res.json(); } catch (_) { /* сервер вернул не JSON */ }

        if (res.ok && payload && payload.ok) {
          form.reset();
          form.querySelectorAll('.field').forEach((f) => { f.dataset.invalid = 'false'; });
          if (status) {
            status.dataset.state = 'ok';
            status.textContent = payload.message ||
              'Заявка отправлена. Перезвоним в рабочее время: ежедневно с 9:00 до 20:00.';
          }
        } else {
          throw new Error((payload && payload.message) || 'Сервер не принял заявку');
        }
      } catch (err) {
        if (status) {
          status.dataset.state = 'error';
          status.textContent = 'Не удалось отправить. Позвоните нам: +7 (909) 559-41-50.';
        }
      } finally {
        if (button) { button.disabled = false; button.innerHTML = label; }
      }
    });
  });

  /* ---------- слайдер фактур в hero ---------- */

  document.querySelectorAll('[data-slider]').forEach((slider) => {
    const track = slider.querySelector('[data-slider-track]');
    const slides = Array.from(track.querySelectorAll('.slide'));
    const dotsBox = slider.querySelector('[data-slider-dots]');
    const prev = slider.querySelector('[data-slider-prev]');
    const next = slider.querySelector('[data-slider-next]');
    if (!slides.length) return;

    const DELAY = 5000;
    let index = 0;
    let timer = null;
    let paused = false;
    let offscreen = false;
    let stops = [0];
    let dots = [];

    /* Позиции остановки, а не «по карточке на точку». Последняя позиция это
       конец ленты: если листать дальше по карточке, справа появлялась бы
       пустота, а точки продолжали бы переключаться вхолостую. */
    const measure = () => {
      const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      const step = slides[0].getBoundingClientRect().width + gap;
      const max = Math.max(0, track.scrollWidth - track.clientWidth);
      const out = [];
      for (let x = 0; x < max - 2 && step > 0; x += step) out.push(Math.round(x));
      out.push(Math.round(max));
      stops = out.length ? out : [0];
      if (index >= stops.length) index = stops.length - 1;
    };

    const buildDots = () => {
      if (!dotsBox) return;
      dotsBox.innerHTML = '';
      dots = stops.map((_, i) => {
        const b = document.createElement('button');
        b.type = 'button';
        b.setAttribute('aria-label', `Показать карточки, позиция ${i + 1} из ${stops.length}`);
        b.setAttribute('aria-current', String(i === index));
        b.addEventListener('click', () => { goTo(i); start(); });
        dotsBox.appendChild(b);
        return b;
      });
    };

    const paint = () => dots.forEach((d, i) => d.setAttribute('aria-current', String(i === index)));

    const goTo = (i, smooth = true) => {
      index = (i + stops.length) % stops.length;
      track.scrollTo({
        left: stops[index],
        behavior: smooth && !reduceMotion ? 'smooth' : 'auto'
      });
      paint();
    };

    // пользователь мог листнуть пальцем: подтягиваем ближайшую позицию
    const syncFromScroll = () => {
      let nearest = 0;
      let best = Infinity;
      stops.forEach((x, i) => {
        const d = Math.abs(x - track.scrollLeft);
        if (d < best) { best = d; nearest = i; }
      });
      if (nearest !== index) { index = nearest; paint(); }
    };

    const stop = () => { if (timer) { clearInterval(timer); timer = null; } };
    const start = () => {
      stop();
      if (reduceMotion || paused || offscreen || document.hidden) return;
      timer = setInterval(() => goTo(index + 1), DELAY);
    };

    const relayout = () => {
      const prevCount = stops.length;
      measure();
      if (stops.length !== prevCount) buildDots(); else paint();
    };

    if (prev) prev.addEventListener('click', () => { goTo(index - 1); start(); });
    if (next) next.addEventListener('click', () => { goTo(index + 1); start(); });

    slider.addEventListener('pointerenter', () => { paused = true; stop(); });
    slider.addEventListener('pointerleave', () => { paused = false; start(); });
    slider.addEventListener('focusin', () => { paused = true; stop(); });
    slider.addEventListener('focusout', () => { paused = false; start(); });

    let scrollTick = null;
    track.addEventListener('scroll', () => {
      if (scrollTick) clearTimeout(scrollTick);
      scrollTick = setTimeout(syncFromScroll, 120);
    }, { passive: true });

    window.addEventListener('resize', relayout);

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(([e]) => {
        offscreen = !e.isIntersecting;
        if (offscreen) stop(); else start();
      }, { threshold: 0.2 }).observe(slider);
    }

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) stop(); else start();
    });

    measure();
    buildDots();
    goTo(0, false);
    start();
  });

  /* ---------- переключатель полной и мобильной версии ---------- */

  const vswitch = document.querySelector('[data-viewport-switch]');

  if (vswitch) {
    const root = document.documentElement;
    const label = vswitch.querySelector('[data-viewport-label]');
    const icon = vswitch.querySelector('use');

    const isDesktop = () => root.getAttribute('data-force-desktop') === '1';

    const paint = () => {
      const desktop = isDesktop();
      if (label) label.textContent = desktop ? 'Мобильная версия' : 'Полная версия';
      if (icon) icon.setAttribute('href', desktop ? '#i-device-mobile' : '#i-desktop');
      vswitch.setAttribute('aria-pressed', String(desktop));
    };

    paint();

    vswitch.addEventListener('click', () => {
      const next = !isDesktop();
      try { localStorage.setItem('rks-desktop', next ? '1' : '0'); } catch (_) { /* приватный режим */ }

      const meta = document.querySelector('meta[name="viewport"]');
      if (next) {
        root.setAttribute('data-force-desktop', '1');
        if (meta) meta.setAttribute('content', 'width=1280');
      } else {
        root.removeAttribute('data-force-desktop');
        if (meta) meta.setAttribute('content', 'width=device-width, initial-scale=1');
      }

      paint();
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  /* ---------- год в подвале ---------- */

  const year = document.querySelector('[data-year]');
  if (year) year.textContent = String(new Date().getFullYear());
})();
