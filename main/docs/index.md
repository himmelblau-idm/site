---
title: Himmelblau
hide:
  - navigation
  - toc
---

<script>
  if (document.querySelector('link[rel=canonical][href$="/"]')) {
    document.body.setAttribute('data-home', 'true');
  }
</script>

<section class="home-hero">
  <div class="hero-floats" aria-label="Highlights">
    <a href="https://www.heise.de/select/ix/2026/1/2528006422371218161" target="_blank" rel="noopener" class="press-float">
      <span class="press-float-badge">Featured In</span>
      <img src="assets/ix-logo.svg" alt="iX Magazine" class="press-float-logo">
      <span class="press-float-text">iX Magazine</span>
    </a>
    <aside class="hb-donate-banner" id="hb-donate-banner" role="region" aria-label="Support Himmelblau">
      <div class="hb-donate-banner__inner">
        <div class="hb-donate-banner__text">
          <span class="hb-donate-banner__title">Help me keep the lights on.</span>
          <span class="hb-donate-banner__copy">Contributions fund the hardware, travel, and support work behind the scenes.</span>
        </div>
        <div class="hb-donate-banner__actions">
          <a class="hb-donate-banner__cta" href="https://opencollective.com/himmelblau/contribute/sponsors-84876/checkout" target="_blank" rel="noopener">Contribute</a>
          <button class="hb-donate-banner__dismiss" type="button" aria-label="Dismiss donation banner">Maybe later</button>
        </div>
      </div>
    </aside>
  </div>
  <div class="hero-card">
    <h1>Seamless Azure Entra ID and Intune integration for Linux</h1>
    <p>SSO, MFA, Intune compliance and TPM-backed keys — with a cleaner experience than Windows.</p>
    <div>
      <a href="/downloads/index.html" class="md-button md-button--primary">Download Himmelblau for Linux</a>
      <a href="/community" class="md-button">Join the Community</a>
    </div>
  </div>
</section>

<section class="capabilities">

  <div class="hb-slider" aria-roledescription="carousel">
<div class="hb-track" tabindex="0">
  <figure id="gif-login" class="hb-slide">
    <a class="hb-prev" href="#gif-o365" aria-label="Previous">‹</a>
    <a class="hb-next" href="#gif-display-manager"  aria-label="Next">›</a>

    <img src="assets/login.gif" alt="Device join and Hello enrollment" loading="lazy" decoding="async">
    <figcaption><strong>Join &amp; Hello Enroll</strong><br>
      Device join and Hello for Business key provisioning.
    </figcaption>
  </figure>

  <figure id="gif-display-manager" class="hb-slide">
    <a class="hb-prev" href="#gif-login" aria-label="Previous">‹</a>
    <a class="hb-next" href="#gif-nss"  aria-label="Next">›</a>

    <img src="assets/himmelblau-display-manager.gif" alt="Himmelblau Display Manager login screen" loading="lazy" decoding="async">
    <figcaption><strong>Display Manager</strong><br>
      Himmelblau Display Manager — a GDM replacement with native Entra ID and OIDC support. Currently experimental.
    </figcaption>
  </figure>

  <figure id="gif-nss" class="hb-slide">
    <a class="hb-prev" href="#gif-display-manager"   aria-label="Previous">‹</a>
    <a class="hb-next" href="#gif-firefox" aria-label="Next">›</a>

    <img src="assets/nss.gif" alt="NSS id and getent demo" loading="lazy" decoding="async">
    <figcaption><strong>Identity Lookup</strong><br>
      Linux <code>id</code> and <code>getent</code> integrated with Entra ID via NSS.
    </figcaption>
  </figure>

  <figure id="gif-firefox" class="hb-slide">
    <a class="hb-prev" href="#gif-nss"  aria-label="Previous">‹</a>
    <a class="hb-next" href="#gif-o365" aria-label="Next">›</a>

    <img src="assets/firefox.gif" alt="Firefox SSO demo" loading="lazy" decoding="async">
    <figcaption><strong>Browser SSO</strong><br>
      Seamless sign-on in Firefox with PRT-based authentication.
    </figcaption>
  </figure>

  <figure id="gif-o365" class="hb-slide">
    <a class="hb-prev" href="#gif-firefox" aria-label="Previous">‹</a>
    <a class="hb-next" href="#gif-login"   aria-label="Next">›</a>

    <img src="assets/o365.gif" alt="Office 365 web apps demo" loading="lazy" decoding="async">
    <figcaption><strong>Office 365 Web Apps</strong><br>
      Single sign-on across Outlook, Teams, and OneDrive.
    </figcaption>
  </figure>
</div>
    <nav class="hb-dots" aria-label="Choose slide">
      <a href="#gif-login"   aria-label="Join & Hello Enroll">•</a>
      <a href="#gif-display-manager" aria-label="Display Manager">•</a>
      <a href="#gif-nss"     aria-label="Identity Lookup">•</a>
      <a href="#gif-firefox" aria-label="Browser SSO">•</a>
      <a href="#gif-o365"    aria-label="O365 Web Apps">•</a>
    </nav>
  </div>
</section>
