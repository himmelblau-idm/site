---
title: Stable Repositories
description: Subscribe to official stable Himmelblau packages for predictable, versioned Linux deployments. Open source, no per-host licensing, and no feature restrictions.
hide:
  - navigation
  - toc
---

<script>document.body.setAttribute("data-stable-repositories", "true");</script>

<div class="hb-stable">
  <header class="hb-stable-hero hb-shell">
    <p class="hb-kicker">Official stable package distribution</p>
    <h1>Stable packages for production deployments</h1>
    <p class="hb-stable-lede">Run Himmelblau from official stable repositories with predictable, versioned releases for supported Linux distributions.</p>
    <p>A subscription provides maintained DEB and RPM packages through entitlement tokens. You pay for building, hosting, organizing, and distributing release packages, while helping fund release maintenance and continued development.</p>
    <div class="hb-actions"><a class="hb-button hb-button--primary" href="#subscribe">Get stable repository access</a><a class="hb-button hb-button--ghost" href="/downloads/?channel=nightly">Use Community Nightly</a></div>
    <p class="hb-stable-note">Repository access does not include technical support.</p>
  </header>

  <section class="hb-shell hb-stable-section" aria-labelledby="subscribe">
    <h2 id="subscribe">Choose the contribution that fits your use</h2>
    <p>Both options provide the same repository access, including the 3.x and 4.x streams. Monthly and yearly subscriptions differ only in billing frequency. Open Collective shows the current amounts at checkout.</p>
    <p>Contributions use the honor system: choose an amount that responsibly reflects your deployment size and the value Himmelblau provides. There is no per-host licensing or feature restriction.</p>
    <div class="hb-stable-grid">
      <article class="hb-stable-card">
        <h3>Personal</h3><p>Homelabs, individual professionals, and personal systems.</p>
        <ul><li>Official stable repository access</li><li>Both 3.x and 4.x streams</li><li>3 host limit</li><li>No technical support included</li></ul>
        <div class="hb-actions"><a class="hb-button hb-button--primary" href="https://opencollective.com/himmelblau/contribute/himmelblau-stable-repos-personal-monthly-105887/checkout?interval=month&amount=10&contributeAs=me">Personal monthly</a><a class="hb-button hb-button--ghost" href="https://opencollective.com/himmelblau/contribute/himmelblau-stable-repos-personal-yearly-105888/checkout?interval=year&amount=120&contributeAs=me">Personal yearly</a></div>
      </article>
      <article class="hb-stable-card">
        <h3>Organization</h3><p>Businesses, institutions, and production fleets.</p>
        <ul><li>Official stable repository access</li><li>Both 3.x and 4.x streams</li><li>No host limits</li><li>No technical support included</li></ul>
        <div class="hb-actions"><a class="hb-button hb-button--primary" href="https://opencollective.com/himmelblau/contribute/himmelblau-stable-repos-corporate-monthly-105889/checkout?interval=month&amount=250&contributeAs=me">Organization monthly</a><a class="hb-button hb-button--ghost" href="https://opencollective.com/himmelblau/contribute/himmelblau-stable-repos-corporate-yearly-105890/checkout?interval=year&amount=3000&contributeAs=me">Organization yearly</a></div>
      </article>
    </div>
  </section>

  <section class="hb-shell hb-stable-section" aria-labelledby="access-title">
    <h2 id="access-title">From subscription to installation</h2>
    <ol><li>Choose Personal or Organization and subscribe through Open Collective.</li><li>You should receive entitlement tokens automatically by email, with a separate token for each stable stream.</li><li>Run the guided installer, choose Stable Repositories, and paste the token for the stream you want. The installer identifies the repository automatically; we recommend 4.x for new deployments.</li></ol>
    <pre><code>curl -fsSL https://himmelblau-idm.org/install | sh</code></pre>
    <p><a href="/downloads/?channel=stable">View installation options</a> or <a href="/docs/installation/">read the installation guide</a>.</p>
    <p>If your subscription email does not arrive, contact <a href="mailto:dmulder@himmelblau-idm.org">dmulder@himmelblau-idm.org</a> with proof of subscription. You should receive a response within one business day. This assistance is for repository access; technical support is not included.</p>
  </section>

  <section class="hb-shell hb-stable-section" aria-labelledby="open-title">
    <h2 id="open-title">Open source for everyone</h2>
    <p>Community Nightly packages remain freely available for evaluation, development, and testing.</p>
    <p>A repository subscription provides predictable release packages for ongoing deployments. It does not include an SLA, certification, or a guarantee of compatibility or uptime.</p>
    <div class="hb-actions"><a class="hb-button hb-button--primary" href="/downloads/?channel=nightly">Use Community Nightly</a><a class="hb-button hb-button--ghost" href="/community/">Join the community</a></div>
    <p>Want to fund development directly? <a href="/donations/">Explore donations and development sponsorship</a>.</p>
  </section>
</div>
