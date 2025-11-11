// inline-logo.js
document.addEventListener('DOMContentLoaded', () => {
  const selectors = [
    '.md-header__button.md-logo img[src$=".svg"]',
    '.md-nav__button.md-logo img[src$=".svg"]'
  ];

  document.querySelectorAll(selectors.join(',')).forEach(img => {
    const parentIsNav = img.closest('.md-nav__button.md-logo') !== null;
    const computed = getComputedStyle(img);
    const fallbackHeight = parentIsNav ? '1.75rem' : '2.5rem';
    const imgHeight = (computed.height && computed.height !== '0px') ? computed.height : fallbackHeight;
    const imgAlt = img.getAttribute('alt') || 'logo';

    fetch(img.src)
      .then(r => r.text())
      .then(txt => {
        const wrap = document.createElement('div');
        wrap.innerHTML = txt.trim();
        const svg = wrap.querySelector('svg');
        if (!svg) return;

        // Unfix size from markup so CSS can control it
        svg.removeAttribute('width');
        svg.removeAttribute('height');

        svg.setAttribute('role', 'img');
        svg.setAttribute('aria-label', imgAlt);
        svg.setAttribute('focusable', 'false');

        // class for shared rules + variant for nav vs header
        svg.classList.add('logo-svg');
        svg.classList.add(parentIsNav ? 'logo-svg--nav' : 'logo-svg--header');

        // apply the computed/fallback height directly to preserve theme sizing
        svg.style.height = imgHeight;
        svg.style.width = 'auto';

        img.replaceWith(svg);
      })
      .catch(() => {});
  });
});
