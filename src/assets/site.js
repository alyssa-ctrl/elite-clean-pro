/* ═══════════════════════════════════════════════════════════
   Elite Clean Pro — Shared site behavior
   Runs on every page (loaded via base layout).
   ═══════════════════════════════════════════════════════════ */

// ── Mobile menu open/close ─────────────────────────────────
(function(){
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  const mobileMenuClose = document.getElementById('mobile-menu-close');
  const mobileOverlay = document.getElementById('mobile-menu-overlay');
  if (!hamburger || !mobileMenu) return;

  function openMenu() {
    mobileMenu.classList.add('open');
    mobileOverlay && mobileOverlay.classList.add('open');
    document.body.classList.add('menu-open');
    hamburger.setAttribute('aria-expanded','true');
    mobileMenu.setAttribute('aria-hidden','false');
  }
  function closeMenu() {
    mobileMenu.classList.remove('open');
    mobileOverlay && mobileOverlay.classList.remove('open');
    document.body.classList.remove('menu-open');
    hamburger.setAttribute('aria-expanded','false');
    mobileMenu.setAttribute('aria-hidden','true');
  }

  hamburger.addEventListener('click', openMenu);
  mobileMenuClose && mobileMenuClose.addEventListener('click', closeMenu);
  mobileOverlay && mobileOverlay.addEventListener('click', closeMenu);
  mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
})();

// ── Header shrinks on scroll ───────────────────────────────
(function(){
  const nav = document.querySelector('nav.main');
  if (!nav) return;
  window.addEventListener('scroll', function(){
    nav.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });
})();

// ── Live time in ticker (Mountain Time, locked) ────────────
(function(){
  function update() {
    const el = document.getElementById('ticker-clock');
    if (!el) return;
    const opts = { timeZone: 'America/Edmonton', hour: '2-digit', minute: '2-digit', hour12: false };
    el.textContent = new Date().toLocaleTimeString('en-CA', opts) + ' MT';
  }
  update();
  setInterval(update, 30000);
})();

// ── Copyright year in footer ───────────────────────────────
(function(){
  const el = document.getElementById('copyright-year');
  if (el) el.textContent = '© ' + new Date().getFullYear();
})();
