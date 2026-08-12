---
title: About Himmelblau
description: The history of Himmelblau, from a SambaXP conversation to an open identity platform for Linux.
hide:
  - navigation
  - toc
---

<script>
  document.body.setAttribute("data-about", "true");
</script>

<div class="hb-about">
  <header class="hb-about-hero">
    <div class="hb-shell hb-about-hero__grid">
      <div class="hb-about-hero__copy">
        <p class="hb-kicker">The project history</p>
        <h1>Linux cloud identity, built in the open.</h1>
        <p class="hb-about-hero__lede">Himmelblau began with a question inside the Samba community: could Linux participate fully in the new generation of cloud identity protocols? The answer grew from an experiment into a production platform—and into shared infrastructure used beyond Himmelblau itself.</p>
        <a class="hb-button hb-button--dark" href="#history">Follow the story <span aria-hidden="true">↓</span></a>
      </div>
      <div class="hb-about-hero__mark">
        <img src="../assets/samba-team-sambaxp-2026.jpg" width="800" height="599" alt="Members of the Samba Team gathered at SambaXP 2026">
      </div>
    </div>
  </header>

  <section id="history" class="hb-history hb-anchor-target" aria-labelledby="hb-history-title">
    <div class="hb-shell">
      <header class="hb-about-heading">
        <p class="hb-kicker">From an idea to an ecosystem</p>
        <h2 id="hb-history-title">A history shaped by interoperability.</h2>
        <p>Some early conversations happened informally and their dates are approximate.</p>
      </header>

      <ol class="hb-timeline">
        <li class="hb-era">
          <div class="hb-era__date"><span>2019</span></div>
          <article class="hb-era__card">
            <p class="hb-era__eyebrow">The first idea</p>
            <h3>A conversation at SambaXP</h3>
            <p>Around SambaXP 2019, David Mulder and Microsoft engineer Tom Talpey discussed whether Samba’s Winbind could grow beyond traditional domain authentication and support a new generation of cloud identity protocols.</p>
            <p>The setting mattered. Microsoft was presenting a <a href="https://sambaxp.org/fileadmin/user_upload/sambaxp2019-slides/farooqi_sambaxp2019_WindowsHelloForBusiness.pdf">Windows Hello for Business protocol deep dive</a> at the conference, while Talpey was arguing for closer collaboration between Microsoft and the Samba Team. The idea that Linux might one day speak those protocols natively had taken root.</p>
            <figure class="hb-history-photo">
              <img src="../assets/tom-talpey-sambaxp-2025.jpg" width="1280" height="959" alt="Tom Talpey speaking into a microphone during a SambaXP discussion" loading="lazy">
              <figcaption>Tom Talpey in discussion at SambaXP 2025. His long advocacy for sustained Microsoft–Samba collaboration helped create the setting for Himmelblau’s earliest conversations.</figcaption>
            </figure>
          </article>
        </li>

        <li class="hb-era">
          <div class="hb-era__date"><span>2022</span></div>
          <article class="hb-era__card">
            <p class="hb-era__eyebrow">The need becomes real</p>
            <h3>Linux vendors confront cloud identity</h3>
            <p>The subject returned around SambaXP 2022 as Microsoft explored a Linux solution for Azure AD (now Microsoft Entra ID). David joined an ongoing conversation between Microsoft engineers and representatives from Red Hat, Canonical, and SUSE.</p>
            <p>Microsoft’s proposed direction centered on a proprietary authentication plugin that Linux distributions could consume. Distribution engineers had practical concerns about timing, maintainability, and asking the Linux community to support code it could not inspect.</p>
            <p>While those broader conversations continued, Canonical had been developing its own implementation in the background. The arrival of aad-auth made clear that the distributions did not need to wait for a future Microsoft component to emerge.</p>
          </article>
        </li>

        <li class="hb-era">
          <div class="hb-era__date"><span>May 2023</span></div>
          <article class="hb-era__card">
            <p class="hb-era__eyebrow">Himmelblau is born</p>
            <h3>An open implementation begins</h3>
            <p>David initially tried to package aad-auth for openSUSE. That evaluation exposed authentication and MFA behavior that did not meet the requirements of a production, community-supported identity component. Rather than ship something the community could not confidently maintain, he started a new implementation.</p>

            <a class="hb-commit" href="https://github.com/himmelblau-idm/himmelblau/commit/5bd4ac4" aria-label="View Himmelblau's initial commit on GitHub">
              <span class="hb-commit__branch" aria-hidden="true">main</span>
              <strong>Initial commit</strong>
              <span>David Mulder committed 5bd4ac4 on May 22, 2023</span>
              <code>himmelblau</code>
            </a>

            <p>The early client drew on Kanidm’s Rust architecture and components. Within weeks it had a daemon, PAM and NSS modules, persistent caching, and open-source MSAL integration. Password authentication came first; Device Authorization Grant support followed when Entra ID required MFA. Version 0.1.0 arrived in September 2023.</p>
            <aside class="hb-name-note"><strong>Why “Himmelblau”?</strong> The German word means “sky blue”—or azure. It is a playful reference to Microsoft’s cloud and a declaration that this implementation belongs in the open.</aside>
          </article>
        </li>

        <li class="hb-era">
          <div class="hb-era__date"><span>2024</span></div>
          <article class="hb-era__card">
            <p class="hb-era__eyebrow">A standalone stack</p>
            <h3>Still connected to Samba</h3>
            <p>An effort to integrate Himmelblau directly into the Samba source tree was ultimately set aside in favor of an independent project. The architectural connection remained: the protocol engine became <a href="https://gitlab.com/samba-team/libhimmelblau">libhimmelblau</a>, owned by the Samba Team and maintained by David.</p>
            <p>That separation let both layers advance quickly. In 2024, the project added device registration, Windows Hello for Business provisioning and PIN authentication, Kerberos credential support, and browser single sign-on.</p>
          </article>
        </li>

        <li class="hb-era">
          <div class="hb-era__date"><span>2025</span></div>
          <article class="hb-era__card">
            <p class="hb-era__eyebrow">A production platform</p>
            <h3>From authentication to managed devices</h3>
            <p>Himmelblau grew into a complete Entra ID and Intune interoperability suite. TPM-backed credentials, offline login and SSO, broader Linux packaging, custom compliance checks, and Intune policy enforcement moved the project well beyond its original login prototype.</p>
            <p>Himmelblau 1.0 was tagged on July 30, 2025. Earlier that year, David presented the daemon’s proposed Samba integration and the underlying OAuth 2.0 work at SambaXP, bringing the project’s story back to the community where it began.</p>
          </article>
        </li>

        <li class="hb-era">
          <div class="hb-era__date"><span>2025</span></div>
          <article class="hb-era__card">
            <p class="hb-era__eyebrow">The ecosystem converges</p>
            <h3>Shared infrastructure wins</h3>
            <p>Canonical archived aad-auth in May 2024 and replaced it with the broader Authd project. In 2025, Authd’s Entra broker began consuming libhimmelblau for device registration and native MFA, building on the protocol work already completed by the Himmelblau and Samba communities.</p>
            <p>The convergence was public and practical. In an <a href="https://github.com/canonical/authd/discussions/688">Authd community discussion</a>, a Canonical engineer described the goal of using libhimmelblau to bring Himmelblau’s device-registration work into Authd. A library born from one implementation was now improving another.</p>

            <div class="hb-ecosystem" aria-label="libhimmelblau ecosystem">
              <a href="https://gitlab.com/samba-team/libhimmelblau" class="hb-ecosystem__core"><small>Samba Team</small><strong>libhimmelblau</strong><span>Open protocol and authentication core</span></a>
              <div class="hb-ecosystem__consumers">
                <a href="https://github.com/himmelblau-idm/himmelblau"><strong>Himmelblau</strong><span>Entra ID, Intune, and OIDC suite</span></a>
                <a href="https://github.com/canonical/authd"><strong>Canonical Authd</strong><span>Consumer for Entra integration</span></a>
              </div>
            </div>

          </article>
        </li>

        <li class="hb-era">
          <div class="hb-era__date"><span>2025–2026</span></div>
          <article class="hb-era__card">
            <p class="hb-era__eyebrow">Beyond Entra ID</p>
            <h3>Himmelblau embraces OIDC</h3>
            <p>Himmelblau’s next step was to apply its Linux login experience beyond Microsoft’s identity platform. Generic OpenID Connect authentication arrived in late 2025, opening the same PAM and NSS foundation to providers such as Keycloak and Okta.</p>
            <p>In 2026, browser-orchestrated MFA brought richer, provider-agnostic authentication into native Linux sign-in. What began as an Entra ID interoperability project had grown into a broader open platform for cloud identity.</p>
          </article>
        </li>
      </ol>
    </div>
  </section>

  <section class="hb-about-now" aria-labelledby="hb-about-now-title">
    <div class="hb-shell hb-about-now__grid">
      <div>
        <p class="hb-kicker">The work continues</p>
        <h2 id="hb-about-now-title">Open identity infrastructure is a community project.</h2>
        <p>Himmelblau is maintained by David Mulder, Samuel Cabrero, William Brown, and a growing community of contributors, with SUSE as its primary sponsor. Its participation in the <a href="https://github.blog/open-source/maintainers/securing-the-ai-software-supply-chain-security-results-across-67-open-source-projects/">GitHub Secure Open Source Fund</a> reflects the same principle that shaped its beginning: identity infrastructure should be inspectable, testable, and improved in the open.</p>
      </div>
      <nav class="hb-about-now__links" aria-label="Project links">
        <a href="https://github.com/himmelblau-idm/himmelblau"><span>Build with us</span><strong>Contribute on GitHub →</strong></a>
        <a href="/community/"><span>Talk with us</span><strong>Join the community →</strong></a>
        <a href="/donations/"><span>Support the work</span><strong>Back Himmelblau →</strong></a>
      </nav>
    </div>
  </section>
</div>
