---
title: Himmelblau
description: Entra ID login, native MFA, Intune compliance, and single sign-on for Linux desktops and SSH.
hide:
  - navigation
  - toc
---

<script>
  document.body.setAttribute("data-home", "true");
</script>

<div class="hb-home">
  <section class="hb-hero" aria-labelledby="hb-hero-title">
    <div class="hb-shell hb-hero__content">
      <h1>Cloud identity for Linux</h1>
      <p class="hb-hero__lede">SSO, MFA, compliance, and TPM-backed keys across Entra ID/Intune and OIDC providers such as Keycloak and Okta — with a practical path toward sovereign cloud identity.</p>
      <div class="hb-actions">
        <a class="hb-button hb-button--primary" href="#install" data-hb-event="hero-install">Start installation</a>
        <a class="hb-button hb-button--ghost" href="#ssh">See how it works <span aria-hidden="true">↓</span></a>
      </div>
    </div>
    <a class="hb-scroll-cue" href="#identity-gap"><span>Scroll to explore</span><i aria-hidden="true"></i></a>
  </section>

  <section class="hb-statement" aria-labelledby="identity-gap-title">
    <div class="hb-shell hb-shell--narrow hb-anchor-target" id="identity-gap">
      <p class="hb-kicker">One identity plane</p>
      <h2 id="identity-gap-title">Your cloud identity should follow users to every Linux session.</h2>
      <p>Remote servers and graphical workstations are different security contexts. Himmelblau gives each the right authentication experience while connecting both to the same Entra ID, PAM, and NSS foundation.</p>
      <div class="hb-paths" aria-label="Authentication paths">
        <a href="#ssh"><span aria-hidden="true">⌁</span><strong>Remote access</strong><small>Cloud credentials + native MFA</small></a>
        <a href="#desktop"><span aria-hidden="true">◉</span><strong>Desktop access</strong><small>Device-bound Hello PIN</small></a>
      </div>
    </div>
  </section>

  <section class="hb-chapter hb-chapter--ink" aria-labelledby="ssh-title">
    <header class="hb-chapter__header hb-shell hb-anchor-target" id="ssh">
      <p class="hb-kicker">For administrators</p>
      <h2 id="ssh-title">MFA-secured SSH, directly against your cloud identity.</h2>
      <p>Resolve Entra or OIDC users through NSS, authenticate through PAM, complete the tenant’s MFA challenge, and enter the shell. Remote sessions require MFA by default.</p>
    </header>

    <div class="hb-scene hb-shell" data-hb-scene>
      <div class="hb-scene__stage hb-terminal-stage">
        <div class="hb-terminal-bar" aria-hidden="true"><span></span><span></span><span></span><b>ssh tux@192.168.1.73</b></div>
        <div class="hb-frame-stack" aria-label="SSH authentication sequence">
          <figure class="hb-frame is-active" data-hb-frame><img src="assets/ssh-01.png" width="1920" height="1080" alt="A terminal initiating an SSH connection for the Entra user tux"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/ssh-02.png" width="1920" height="1080" loading="lazy" alt="SSH prompting the user for their Entra ID password"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/ssh-03.png" width="1920" height="1080" loading="lazy" alt="SSH displaying a Microsoft Authenticator number-matching challenge"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/ssh-04.png" width="1920" height="1080" loading="lazy" alt="The Entra user successfully signed in to a Linux shell over SSH"></figure>
        </div>
      </div>
      <div class="hb-scene__steps">
        <article class="hb-step is-active" data-hb-step>
          <span>01</span><h3>Connect as a Cloud user</h3>
          <p>Himmelblau resolves the cloud identity as a Linux account through NSS—without pre-creating a local user.</p>
        </article>
        <article class="hb-step" data-hb-step>
          <span>02</span><h3>Authenticate with the Identity Provider</h3>
          <p>PAM hands the request to Himmelblau. The exact credential flow follows the authentication methods configured by the Identity Provider.</p>
        </article>
        <article class="hb-step" data-hb-step>
          <span>03</span><h3>Complete native MFA</h3>
          <p>MFA happens inside the SSH experience.</p>
        </article>
        <article class="hb-step" data-hb-step>
          <span>04</span><h3>Enter the shell</h3>
          <p>The authenticated cloud identity arrives as a normal POSIX session, ready for shared hosts, remote administration, and group-based access control.</p>
        </article>
      </div>
    </div>
  </section>

  <section class="hb-chapter hb-chapter--mist" aria-labelledby="desktop-title">
    <header class="hb-chapter__header hb-shell hb-anchor-target" id="desktop">
      <p class="hb-kicker">For workstations</p>
      <h2 id="desktop-title">The first desktop login becomes a secure daily habit.</h2>
      <p>Users establish their identity, satisfy MFA, and enroll a Hello PIN bound to that Linux device. Linux Hello can optionally be disabled, requiring MFA at every desktop login.</p>
    </header>

    <div class="hb-scene hb-shell" data-hb-scene>
      <div class="hb-scene__stage hb-screen-stage">
        <div class="hb-frame-stack" aria-label="First-time graphical login sequence">
          <figure class="hb-frame is-active" data-hb-frame><img src="assets/desktop-first-01.png" width="1916" height="1023" loading="lazy" alt="GNOME login screen with a local user and the Not listed option"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-first-02.png" width="1916" height="1023" loading="lazy" alt="Entering the Entra username tux at the GNOME login screen"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-first-03.png" width="1916" height="1023" loading="lazy" alt="GNOME prompting for the Entra ID password"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-first-04.png" width="1916" height="1023" loading="lazy" alt="Entering the Entra ID password at the GNOME login screen"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-first-05.png" width="1916" height="1023" loading="lazy" alt="GNOME displaying a Microsoft Authenticator number-matching prompt"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-first-06.png" width="1916" height="1023" loading="lazy" alt="GNOME asking the user to set up a new Hello PIN"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-first-07.png" width="1916" height="1023" loading="lazy" alt="The user entering a new device-bound Hello PIN"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-first-08.png" width="1916" height="1023" loading="lazy" alt="GNOME asking the user to confirm the Hello PIN"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-first-09.png" width="1916" height="1023" loading="lazy" alt="Himmelblau enrolling the confirmed Hello PIN"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-first-10.png" width="1916" height="1023" loading="lazy" alt="The Entra user signed in to the GNOME desktop"></figure>
        </div>
      </div>
      <div class="hb-scene__steps">
        <article class="hb-step is-active" data-hb-step><span>01</span><h3>Choose the cloud account</h3><p>“Not listed?” opens a prompt for entering your Cloud identity username.</p></article>
        <article class="hb-step" data-hb-step><span>02</span><h3>Establish identity</h3><p>The user signs in with their Cloud credentials and the tenant’s configured authentication requirements.</p></article>
        <article class="hb-step" data-hb-step><span>03</span><h3>Satisfy MFA</h3><p>Native MFA is presented at the Linux greeter, keeping the first-login journey in one coherent flow.</p></article>
        <article class="hb-step" data-hb-step><span>04</span><h3>Enroll a Hello PIN</h3><p>The PIN unlocks a cryptographic credential tied to this device. With a hardware TPM configured, key material can be hardware-backed.</p></article>
        <article class="hb-step" data-hb-step><span>05</span><h3>Start the session</h3><p>The desktop opens as the Cloud user, with the identity and token foundation needed by browser and application SSO.</p></article>
      </div>
    </div>
  </section>

  <section class="hb-chapter hb-chapter--return" aria-labelledby="return-title">
    <header class="hb-chapter__header hb-shell">
        <p class="hb-kicker">The next login</p>
        <h2 id="return-title">Enroll once. Return with the device-bound PIN.</h2>
        <p>Hello PIN is intended for local authentication by default: convenient at the workstation, without weakening the remote SSH boundary.</p>
    </header>
    <div class="hb-scene hb-shell" data-hb-scene>
      <div class="hb-scene__stage hb-screen-stage">
        <div class="hb-frame-stack" aria-label="Returning desktop login sequence">
          <figure class="hb-frame is-active" data-hb-frame><img src="assets/desktop-return-01.png" width="1916" height="1023" loading="lazy" alt="GNOME lock screen"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-return-02.png" width="1916" height="1023" loading="lazy" alt="GNOME asking Tux Penguin for the Linux Hello PIN"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-return-03.png" width="1916" height="1023" loading="lazy" alt="GNOME validating the entered Hello PIN"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/desktop-return-04.png" width="1916" height="1023" loading="lazy" alt="The local desktop unlocked successfully"></figure>
        </div>
      </div>
      <div class="hb-scene__steps">
        <article class="hb-step is-active" data-hb-step><span>01</span><h3>Wake the workstation</h3><p>Return to the familiar local lock screen on the enrolled Linux device.</p></article>
        <article class="hb-step" data-hb-step><span>02</span><h3>Enter the device-bound PIN</h3><p>The user authenticates locally with the Hello PIN enrolled during their first sign-in.</p></article>
        <article class="hb-step" data-hb-step><span>03</span><h3>Unlock the protected credential</h3><p>Himmelblau validates the PIN and unlocks the cryptographic credential bound to this device.</p></article>
        <article class="hb-step" data-hb-step><span>04</span><h3>Continue the workday</h3><p>The desktop opens with native SSO integration.</p></article>
      </div>
    </div>
  </section>

  <section class="hb-chapter hb-chapter--cloud" aria-labelledby="sso-title">
    <header class="hb-chapter__header hb-shell hb-anchor-target" id="sso">
      <p class="hb-kicker">The session continues</p>
      <h2 id="sso-title">Sign in to Linux. Open the workday already authenticated.</h2>
      <p>The authenticated session can carry SSO into Firefox, Thunderbird, and Microsoft 365 web applications, while packaged launchers make the suite feel at home on the desktop.</p>
    </header>
    <div class="hb-scene hb-shell" data-hb-scene>
      <div class="hb-scene__stage hb-app-stage">
        <div class="hb-frame-stack" aria-label="Single sign-on application examples">
          <figure class="hb-frame is-active" data-hb-frame><img src="assets/sso-apps.png" width="1918" height="1034" loading="lazy" alt="Microsoft 365 application launchers pinned to the GNOME dash"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/sso-firefox.png" width="1916" height="1035" loading="lazy" alt="Firefox already signed in to the Microsoft Azure portal as the Entra user"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/sso-outlook.png" width="1918" height="1034" loading="lazy" alt="Outlook running as a Linux desktop web application"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/sso-teams.png" width="1918" height="1034" loading="lazy" alt="A Microsoft Teams meeting running on the Linux desktop"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/sso-word.png" width="1918" height="1034" loading="lazy" alt="Microsoft Word running as a Linux desktop web application"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/sso-excel.png" width="1918" height="1034" loading="lazy" alt="Microsoft Excel running as a Linux desktop web application"></figure>
          <figure class="hb-frame" data-hb-frame><img src="assets/sso-powerpoint.png" width="1918" height="1034" loading="lazy" alt="Microsoft PowerPoint running as a Linux desktop web application"></figure>
        </div>
      </div>
      <div class="hb-scene__steps">
        <article class="hb-step is-active" data-hb-step><span>01</span><h3>Applications feel native</h3><p>Launch Outlook, Teams, Word, Excel, and PowerPoint from the desktop rather than rebuilding the workday around browser tabs.</p></article>
        <article class="hb-step" data-hb-step><span>02</span><h3>Browser SSO</h3><p>PRT-based authentication lets supported browsers reach Entra-protected services without another full sign-in.</p></article>
  <article class="hb-step" data-hb-step>
    <span>03</span>
    <h3>Outlook, already signed in</h3>
    <p>Open Outlook from the desktop and get straight to mail and calendar with the same authenticated identity.</p>
  </article>

  <article class="hb-step" data-hb-step>
    <span>04</span>
    <h3>Meet in Teams</h3>
    <p>Join Teams meetings from Linux without breaking the flow of your desktop workspace.</p>
  </article>

  <article class="hb-step" data-hb-step>
    <span>05</span>
    <h3>Work in Word</h3>
    <p>Create and edit Microsoft 365 documents while remaining connected to your Entra identity.</p>
  </article>

  <article class="hb-step" data-hb-step>
    <span>06</span>
    <h3>Build in Excel</h3>
    <p>Work with spreadsheets from the Linux desktop without another round of authentication.</p>
  </article>

  <article class="hb-step" data-hb-step>
    <span>07</span>
    <h3>Present with PowerPoint</h3>
    <p>Open presentations directly from the desktop and keep the Microsoft 365 workflow connected end to end.</p>
  </article>
      </div>
    </div>
  </section>

  <section class="hb-compliance" aria-labelledby="compliance-title">
    <div class="hb-shell hb-compliance__grid hb-anchor-target" id="compliance">
      <div class="hb-compliance__copy">
        <p class="hb-kicker">Intune integration</p>
        <h2 id="compliance-title">Linux devices, visible and compliant.</h2>
        <p>Himmelblau brings Linux devices into the Intune view and can apply compliance at authentication time.</p>
        <ul class="hb-checks"><li>Linux device registration</li><li>Compliance status in Intune</li><li>Policy enforcement during authentication</li></ul>
        <a class="hb-text-link" href="/docs/intune/">Explore Intune policy integration →</a>
      </div>
      <figure class="hb-compliance__image">
        <img src="assets/compliance-devices.png" width="1920" height="1080" loading="lazy" alt="Microsoft Intune admin center showing two openSUSE Linux devices with Compliant status">
        <figcaption>Linux devices reporting compliant in the Intune admin center.</figcaption>
      </figure>
    </div>
  </section>

  <section class="hb-proof" aria-labelledby="proof-title">
    <div class="hb-shell">
      <header class="hb-section-heading"><p class="hb-kicker">Trusted in the open</p><h2 id="proof-title">Identity infrastructure you can inspect, test, and improve.</h2></header>
      <div class="hb-proof__grid">
        <a class="hb-proof-card" href="https://github.com/himmelblau-idm/himmelblau" target="_blank" rel="noopener"><span>GPLv3+</span><strong>Open source by design</strong><p>Review the implementation, follow development, and contribute on GitHub.</p></a>
        <a class="hb-proof-card" href="https://github.blog/open-source/maintainers/securing-the-ai-software-supply-chain-security-results-across-67-open-source-projects/" target="_blank" rel="noopener"><span>Security program</span><strong>GitHub Secure Open Source Fund</strong><p>Himmelblau participated in GitHub’s project security initiative.</p></a>
        <article class="hb-proof-card hb-proof-card--patch"><span>Security engineering</span><strong>Patch the Planet participant</strong><p>Himmelblau is participating in the OpenAI and Trail of Bits initiative that pairs AI-assisted research with expert review to find, validate, and patch security issues in open-source software.</p><div class="hb-proof-card__links"><a href="https://trailofbits.com/patch-the-planet/" target="_blank" rel="noopener">Program overview →</a><a href="https://openai.com/index/patch-the-planet/" target="_blank" rel="noopener">OpenAI announcement →</a></div></article>
      </div>
      <a class="hb-press-strip" href="https://www.heise.de/select/ix/2026/1/2528006422371218161" target="_blank" rel="noopener"><img src="assets/ix-logo.svg" width="72" height="72" loading="lazy" alt="iX Magazine"><span><small>Featured in iX Magazine</small><strong>Read independent technical coverage of Himmelblau.</strong></span><b aria-hidden="true">Read the article →</b></a>
      <div class="hb-compare-callout"><div><p class="hb-kicker">Evaluating your options?</p><h3>Compare Himmelblau with Authd, SSSD, and Intune for Linux.</h3></div><a class="hb-button hb-button--dark" href="/alternatives/">Compare solutions →</a></div>
    </div>
  </section>

  <section class="hb-install" aria-labelledby="install-title">
    <div class="hb-shell hb-shell--narrow hb-anchor-target" id="install">
      <p class="hb-kicker">Ready when you are</p>
      <h2 id="install-title">Bring your Linux systems into the identity plane.</h2>
      <p>The guided installer uses the native package manager, configures the identity provider, and starts the Himmelblau services.</p>
      <div class="hb-command"><code>curl -fsSL https://himmelblau-idm.org/install | sh</code><button type="button" data-hb-copy aria-label="Copy installation command"><span data-hb-copy-label>Copy</span></button></div>
      <p class="hb-install__note">Review scripts before running them in your environment.</p>
      <div class="hb-actions hb-actions--center"><a class="hb-button hb-button--primary" href="/downloads/" data-hb-event="install-options">Package options</a><a class="hb-button hb-button--ghost-light" href="/docs/" data-hb-event="install-docs">Deployment documentation</a></div>
      <div class="hb-distros" aria-label="Supported Linux families"><span>SUSE</span><span>openSUSE</span><span>Ubuntu</span><span>Mint</span><span>Debian</span><span>Fedora</span><span>RHEL</span><span>Rocky</span><span>Oracle</span><span>Alma</span><span>Amazon</span><span>NixOS</span></div>
    </div>
  </section>

  <section class="hb-close">
    <div class="hb-shell"><div><strong>Built by and for the community.</strong><p>Ask questions, report issues, help test, or support continued development.</p></div><nav aria-label="Community links"><a href="/community/">Join the community</a><a href="https://github.com/himmelblau-idm/himmelblau" target="_blank" rel="noopener">GitHub</a><a href="/donations/">Support Himmelblau</a></nav></div>
  </section>
</div>
