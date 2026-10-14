(() => {
  // Phone menu: the section links drop down under the top bar.
  const menuBtn = document.querySelector('.menu-btn');
  const nav = document.getElementById('sections-nav');
  if (menuBtn && nav) {
    const setOpen = (open) => {
      menuBtn.setAttribute('aria-expanded', String(open));
      menuBtn.textContent = open ? 'Close' : 'Menu';
      nav.classList.toggle('open', open);
    };
    menuBtn.addEventListener('click', () => setOpen(!nav.classList.contains('open')));
    nav.addEventListener('click', (event) => { if (event.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && nav.classList.contains('open')) { setOpen(false); menuBtn.focus(); }
    });
  }

  // Mark the nav link for the section currently on screen.
  const links = nav ? [...nav.querySelectorAll('a[href^="#"]')] : [];
  const sections = links.map((a) => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  if (sections.length && 'IntersectionObserver' in window) {
    const spy = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        links.forEach((a) => {
          if (a.getAttribute('href') === `#${entry.target.id}`) a.setAttribute('aria-current', 'true');
          else a.removeAttribute('aria-current');
        });
      }
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach((section) => spy.observe(section));
  }

  // Image viewer: every [data-full] inside a [data-gallery] belongs to that gallery.
  const viewer = document.querySelector('.viewer');
  if (!viewer || typeof viewer.showModal !== 'function') return;

  const img = viewer.querySelector('img');
  const cap = viewer.querySelector('.viewer-cap');
  const count = viewer.querySelector('.viewer-count');
  const prev = viewer.querySelector('.viewer-prev');
  const next = viewer.querySelector('.viewer-next');
  const close = viewer.querySelector('.viewer-close');
  let items = [];
  let index = 0;
  let opener = null;

  const preload = (el) => { if (el) new Image().src = el.dataset.full; };

  function show(i) {
    index = (i + items.length) % items.length;
    const item = items[index];
    const thumb = item.querySelector('img');
    img.src = item.dataset.full;
    img.alt = thumb ? thumb.alt : item.dataset.caption || '';
    cap.textContent = item.dataset.caption || '';
    count.textContent = items.length > 1 ? `${index + 1} / ${items.length}` : '';
    prev.hidden = next.hidden = items.length < 2;
    preload(items[(index + 1) % items.length]);
  }

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('button[data-full]');
    if (!trigger) return;
    const gallery = trigger.closest('[data-gallery]');
    items = gallery ? [...gallery.querySelectorAll('[data-full]')] : [trigger];
    opener = trigger;
    show(items.indexOf(trigger));
    viewer.showModal();
    close.focus();
  });

  prev.addEventListener('click', () => show(index - 1));
  next.addEventListener('click', () => show(index + 1));
  close.addEventListener('click', () => viewer.close());

  viewer.addEventListener('click', (event) => {
    if (event.target === viewer || event.target.classList.contains('viewer-fig')) viewer.close();
  });
  viewer.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') show(index - 1);
    if (event.key === 'ArrowRight') show(index + 1);
  });
  viewer.addEventListener('close', () => {
    if (opener) opener.focus({ preventScroll: true });
  });

  // Swipe between images on touch screens.
  let startX = null;
  viewer.addEventListener('pointerdown', (event) => { startX = event.clientX; });
  viewer.addEventListener('pointerup', (event) => {
    if (startX === null || items.length < 2) return;
    const dx = event.clientX - startX;
    startX = null;
    if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
  });
})();
