---
hide:
  - navigation
  - toc
---

<div id="rss-feed"></div>
<script>
  const feedUrl = "https://mytechinsights.wordpress.com/feed";
  const proxy = "https://api.rss2json.com/v1/api.json?rss_url=" + encodeURIComponent(feedUrl);

  fetch(proxy)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById("rss-feed");
      data.items.slice(0, 5).forEach(entry => {
        const item = document.createElement("div");
        item.className = "rss-item";

        const parser = new DOMParser();
        const doc = parser.parseFromString(entry.description, 'text/html');

        // Extract all <a> tags (which contain "Continue reading")
        const anchors = [...doc.querySelectorAll("a")];
        let readMoreLink = null;

        anchors.forEach(a => {
          if (a.textContent.toLowerCase().includes("continue reading")) {
            readMoreLink = a;
            a.remove(); // Remove it from the summary
          }
        });

        const summaryHTML = doc.body.innerHTML;

        item.innerHTML = `
          <h3><a href="${entry.link}" target="_blank">${entry.title}</a></h3>
          <div class="rss-summary">${summaryHTML}</div>
          ${readMoreLink ? `<a class="rss-read-more" href="${readMoreLink.href}" target="_blank">${readMoreLink.textContent}</a>` : ""}
        `;

        container.appendChild(item);
      });
    });
</script>
