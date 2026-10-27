(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Split headings into words ---------- */
  $$('[data-split]').forEach(el => {
    let i = 0;
    const walk = node => {
      [...node.childNodes].forEach(n => {
        if (n.nodeType === 3) {
          const frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(part => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
            const w = document.createElement('span');
            w.className = 'w';
            const wi = document.createElement('span');
            wi.className = 'wi';
            wi.style.setProperty('--i', i++);
            wi.textContent = part;
            w.appendChild(wi);
            frag.appendChild(w);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1 && n.tagName !== 'BR' && n.tagName !== 'svg') {
          walk(n);
        }
      });
    };
    walk(el);
  });

  /* Footer wordmark into letters */
  const fw = $('#footerWord');
  if (fw) {
    const esc = c => (c === ' ' ? '&nbsp;' : c === '&' ? '&amp;' : c);
    fw.innerHTML = [...fw.textContent].map((c, i) => `<span class="ch" style="--i:${i}">${esc(c)}</span>`).join('');
  }

  /* ---------- Reveal on scroll ---------- */
  const revealEls = $$('[data-reveal], [data-split], #footerWord');
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('in');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.14, rootMargin: '0px 0px -6% 0px' });
  revealEls.forEach(el => io.observe(el));

  /* ---------- Counters ---------- */
  const countIO = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target;
      countIO.unobserve(el);
      const end = parseFloat(el.dataset.count);
      const dec = parseInt(el.dataset.decimals || '0', 10);
      if (reduce) { el.textContent = end.toFixed(dec); return; }
      const dur = 1800;
      const t0 = performance.now();
      const tick = now => {
        const p = Math.min(1, (now - t0) / dur);
        const eased = 1 - Math.pow(1 - p, 4);
        el.textContent = (end * eased).toFixed(dec);
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.6 });
  $$('[data-count]').forEach(el => countIO.observe(el));

  /* ---------- Hero slideshow ---------- */
  const slides = $$('#heroSlides .slide');
  const bar = $('#slideBar');
  const num = $('#slideNum');
  const SLIDE_MS = 6500;
  let current = 0, timer;
  const go = idx => {
    slides[current].classList.remove('is-active');
    current = (idx + slides.length) % slides.length;
    slides[current].classList.add('is-active');
    num.textContent = String(current + 1).padStart(2, '0');
    restartBar();
  };
  const restartBar = () => {
    clearTimeout(timer);
    bar.classList.remove('run');
    void bar.offsetWidth;
    bar.style.setProperty('--slide-ms', SLIDE_MS + 'ms');
    bar.classList.add('run');
    timer = setTimeout(() => go(current + 1), SLIDE_MS);
  };
  if (slides.length > 1 && bar) {
    $('#nextSlide').addEventListener('click', () => go(current + 1));
    $('#prevSlide').addEventListener('click', () => go(current - 1));
    restartBar();
  }

  /* ---------- Nav state, active link, WhatsApp float ---------- */
  const nav = $('#nav');
  const wa = $('#waFloat');
  const hero = $('#home');
  const heroSlides = $('#heroSlides');
  const heroContent = $('#heroContent');

  /* Section highlighting only on the homepage; treatment pages mark "Treatments" statically */
  const navLinks = $$('.nav-links > a, .nav-links > .nav-dd > a');
  if (document.body.dataset.page === 'home') {
    const sectionIO = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        const id = e.target.id;
        navLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href').endsWith('#' + id)));
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    ['home', 'treatments', 'about', 'gallery', 'dentists', 'reviews', 'contact'].forEach(id => {
      const s = document.getElementById(id);
      if (s) sectionIO.observe(s);
    });
  }

  /* ---------- Scroll-driven effects ---------- */
  const pxEls = $$('[data-parallax]');
  const steps = $('#steps');
  const stepsFill = $('#stepsFill');
  const stepItems = $$('.step');
  let ticking = false;

  const onScroll = () => {
    const y = window.scrollY;
    const vh = window.innerHeight;

    nav.classList.toggle('scrolled', y > 60);
    wa.classList.toggle('show', y > vh * 0.6);

    if (reduce) return;

    // hero depth
    const hh = hero ? hero.offsetHeight : 0;
    if (hero && heroSlides && heroContent && y < hh) {
      const p = y / hh;
      heroSlides.style.transform = `translate3d(0, ${y * 0.28}px, 0) scale(${1 + p * 0.06})`;
      heroContent.style.transform = `translate3d(0, ${y * -0.12}px, 0)`;
      heroContent.style.opacity = String(1 - p * 1.1);
    }

    // parallax images
    pxEls.forEach(el => {
      const host = el.parentElement;
      const r = host.getBoundingClientRect();
      if (r.bottom < -100 || r.top > vh + 100) return;
      const p = (r.top + r.height / 2 - vh / 2) / vh;
      const amt = parseFloat(el.dataset.parallax) || 0.08;
      el.style.transform = `translate3d(0, ${(-p * amt * r.height).toFixed(1)}px, 0)`;
    });

    // process timeline
    if (steps && window.innerWidth > 1024) {
      const r = steps.getBoundingClientRect();
      let p = (vh * 0.82 - r.top) / (r.height * 0.9 + vh * 0.25);
      p = Math.max(0, Math.min(1, p));
      stepsFill.style.transform = `scaleX(${p})`;
      stepItems.forEach((s, i) => s.classList.toggle('lit', p >= i / stepItems.length + 0.02 || (i === 0 && p > 0.01)));
    }
  };

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => { onScroll(); ticking = false; });
      ticking = true;
    }
  }, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();

  /* ---------- Mobile menu ---------- */
  const body = document.body;
  const mmenu = $('#mmenu');
  $('#burger').addEventListener('click', () => {
    body.classList.add('menu-open');
    mmenu.setAttribute('aria-hidden', 'false');
  });
  $$('[data-close]', mmenu).forEach(el => el.addEventListener('click', () => {
    body.classList.remove('menu-open');
    mmenu.setAttribute('aria-hidden', 'true');
  }));

  /* ---------- FAQ accordion ---------- */
  $$('.acc-item').forEach(item => {
    const q = $('.acc-q', item);
    q.addEventListener('click', () => {
      const open = item.classList.contains('open');
      $$('.acc-item.open').forEach(o => { o.classList.remove('open'); $('.acc-q', o).setAttribute('aria-expanded', 'false'); });
      if (!open) { item.classList.add('open'); q.setAttribute('aria-expanded', 'true'); }
    });
  });

  /* ---------- Treatment → booking form ---------- */
  const select = $('#f-treat');
  const pick = val => {
    if (!select || !val) return;
    const opt = [...select.options].find(o => o.text === val || o.dataset.slug === val);
    if (opt) select.value = opt.value;
  };
  $$('[data-treat]').forEach(a => a.addEventListener('click', () => pick(a.dataset.treat)));
  // Treatment pages link to /?t=<slug>#contact
  pick(new URLSearchParams(location.search).get('t'));

  /* ---------- Booking form → WhatsApp ---------- */
  const form = $('#bookForm');
  if (form) form.addEventListener('submit', e => {
    e.preventDefault();
    const name = form.name.value.trim();
    const phone = form.phone.value.trim();
    [form.name, form.phone].forEach(f => {
      f.style.borderColor = f.value.trim() ? '' : '#d9826b';
    });
    if (!name || !phone) { (name ? form.phone : form.name).focus(); return; }
    const lines = [
      'Assalam-o-Alaikum! I would like to book an appointment at Braces & Faces Dental Clinic.',
      '',
      `Name: ${name}`,
      `Phone: ${phone}`,
      `Treatment: ${form.treatment.value}`
    ];
    if (form.date.value) lines.push(`Preferred date: ${form.date.value}`);
    if (form.message.value.trim()) lines.push(`Note: ${form.message.value.trim()}`);
    $('#formOk').classList.add('show');
    window.open('https://wa.me/923164936792?text=' + encodeURIComponent(lines.join('\n')), '_blank', 'noopener');
  });

  /* No past dates in the booking form */
  const dateIn = $('#f-date');
  if (dateIn) {
    const t = new Date();
    dateIn.min = new Date(t.getTime() - t.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  }

  const yr = $('#year');
  if (yr) yr.textContent = new Date().getFullYear();
})();
