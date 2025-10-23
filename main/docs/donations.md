---
hide:
  - navigation
  - toc
---

# Support Himmelblau – Become a Sponsor

Himmelblau is an open-source project dedicated to bringing seamless Azure Entra ID authentication to Linux.
By becoming a Sponsor, you help sustain development, improve features, and keep Himmelblau independent and community-driven.

---

## Why sponsor?

Contributions from sponsors help fund development, fix bugs, and add features that matter to our users.

- Ensure Himmelblau stays actively maintained and evolving.
- Support open-source authentication for Linux.
- Help keep Himmelblau free and independent for everyone.

### Start sponsoring today:

👉 [Become a Sponsor](https://opencollective.com/himmelblau/contribute/sponsors-84876/checkout)

If you'd like to make a US tax-exempt contribution, you can make contributions via Software in the Public Interest (SPI).

👉 [US Tax exempt sponsorship](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=8GYKFLX9UNCH2)

---

## The Backer's Bounty – Fund a Specific Bug Fix or Feature

Want to see a particular bug fixed or a new feature added to Himmelblau? Contribute to the Backer’s Bounty and help drive development forward!
Your financial contribution influences the priority of implementation of specific issues that matter to you and the community.

### How it works:

1. Submit a [bug fix](https://github.com/himmelblau-idm/himmelblau/issues/new?template=bug_report.md) or [feature request](https://github.com/himmelblau-idm/himmelblau/issues/new?template=enhancement-request.md) (or review the [existing issues](https://github.com/himmelblau-idm/himmelblau/issues)).
2. Select your issue from the list below, and click `Donate`.
3. Your donation helps prioritize and accelerate development.
4. Progress updates will be shared transparently with contributors.

You’re not just donating—you’re actively driving Himmelblau’s evolution!

---

<input type="text" id="issue-search" placeholder="Search by issue number or title...">
<div id="issues-list">
            <p>Loading issues and contributions…</p>
</div>

<script>
            let allIssues = []; // Will store all fetched issues
            let contributionTotals = {}; // Summed contributions per issue

            // 1. Fetch issues from GitHub
            async function fetchIssues() {
                const apiUrl = 'https://api.github.com/repos/himmelblau-idm/himmelblau/issues';
                const response = await fetch(apiUrl);
                if (!response.ok) {
                    throw new Error(`GitHub API error: ${response.status}`);
                }
                const data = await response.json();
                // Filter out pull requests (which include a 'pull_request' property)
                return data.filter(item => !item.pull_request);
            }

            // 2. Fetch contributions from Open Collective's GraphQL API
            async function fetchContributions() {
                const graphqlUrl = 'https://api.opencollective.com/graphql/v2';
                const query = `
                  query account($slug: String) {
                    account(slug: $slug) {
                      transactions(limit: 100, type: CREDIT) {
                        nodes {
                          amount {
                            value
                          }
                          fromAccount {
                            name
                          }
                          createdAt
                        }
                      }
                    }
                  }
                `;
                const variables = { slug: "himmelblau" };
                const response = await fetch(graphqlUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, variables })
                });
                const json = await response.json();
                return json.data.account.transactions.nodes;
            }

            // 3. Parse contributions with fallback mapping from createdAt timestamp
            function parseContributions(contributions) {
                const totals = {};
                const manualMapping = {
                    "2025-02-18T18:31:54.631Z": "60",
                    "2025-04-23T10:19:19.914Z": "60",
                    "2025-04-23T10:18:01.038Z": "60",
                    "2025-09-22T18:32:56.895Z": "724",
                    "2025-10-21T18:22:28.370Z": "738",
                    // Add additional mappings as needed.
                };

                contributions.forEach(tx => {
                    let issueNum;
                    const nameField = tx.fromAccount?.name || '';
                    const match = nameField.match(/Contribution for Issue:\s*#(\d+)/);
                    if (match) {
                        issueNum = match[1];
                    } else {
                        const createdAt = tx.createdAt;
                        if (manualMapping[createdAt]) {
                            issueNum = manualMapping[createdAt];
                        } else {
                            console.log(`No mapping found for contribution at ${createdAt} with value $${tx.amount.value}`);
                        }
                    }
                    if (issueNum) {
                        const amount = parseFloat(tx.amount.value);
                        if (!isNaN(amount)) {
                            totals[issueNum] = (totals[issueNum] || 0) + amount;
                        }
                    }
                });
                return totals;
            }

function handleDonate(donationUrl, issueNumber, issueTitle) {
    // 1. Open donation link in a new tab
    window.open(donationUrl, "_blank");

    // 2. Build mailto link with subject + body
    const subject = encodeURIComponent(`Donation for Himmelblau Issue #${issueNumber}: ${issueTitle}`);
    const body = encodeURIComponent(`I've just contributed to Himmelblau, and I want my donation attributed to issue number ${issueNumber}.`);

    const mailto = `mailto:dmulder@himmelblau-idm.org?subject=${subject}&body=${body}`;

    // 3. Open mailto link (usually opens default email client)
    window.location.href = mailto;
}

            // 4. Render issues based on the current search filter
            function renderIssues(issuesToRender) {
                const issuesContainer = document.getElementById('issues-list');
                issuesContainer.innerHTML = '';

                if (!issuesToRender || issuesToRender.length === 0) {
                    issuesContainer.innerHTML = '<p>No matching issues found.</p>';
                    return;
                }

                let issueDisplayed = false;
                issuesToRender.forEach(issue => {
                    const issueNumber = issue.number;
                    const totalFunded = contributionTotals[issueNumber] || 0;

                    const issueElement = document.createElement('div');
                    issueElement.innerHTML = `
                        <h3>${issue.title} <a href="${issue.html_url}" target="_blank">#${issueNumber}</a></h3>
                        <p>Contributed: $${totalFunded.toFixed(2)}</p>
                        <a class="button" onclick="handleDonate('https://opencollective.com/himmelblau/contribute/backers-bench-84925/checkout', ${issueNumber}, '${issue.title}')">Donate</a>
			<a class="button" onclick="handleDonate('https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=8GYKFLX9UNCH2', ${issueNumber}, '${issue.title}')">Donate US Tax Exempt</a>
                        <a class="button secondary" href="${issue.html_url}" target="_blank">View Details</a>
                    `;
                    issuesContainer.appendChild(issueElement);
                    issueDisplayed = true;
                });

                if (!issueDisplayed) {
                    issuesContainer.innerHTML = '<p>No matching issues found.</p>';
                }
            }

            // 5. Filter issues by user input
            function filterIssues(searchTerm) {
                const lowerTerm = searchTerm.toLowerCase();
                const filtered = allIssues.filter(issue => {
                    const titleMatch = issue.title.toLowerCase().includes(lowerTerm);
                    const numberMatch = issue.number.toString().includes(lowerTerm);
                    return titleMatch || numberMatch;
                });
                renderIssues(filtered);
            }

            // 6. Main logic: fetch data, parse, sort, then initial render + attach event listener
            document.addEventListener('DOMContentLoaded', async function() {
                try {
                    const [issues, contributions] = await Promise.all([fetchIssues(), fetchContributions()]);
                    contributionTotals = parseContributions(contributions);

                    // Filter out pull requests by checking if item.pull_request is defined
                    allIssues = issues.filter(item => !item.pull_request);

                    // Sort issues by total contributions descending
                    allIssues.sort((a, b) => {
                        const aTotal = contributionTotals[a.number] || 0;
                        const bTotal = contributionTotals[b.number] || 0;
                        return bTotal - aTotal;
                    });

                    // Initial render (no filter)
                    renderIssues(allIssues);

                    // Attach event listener for search
                    const searchInput = document.getElementById('issue-search');
                    searchInput.addEventListener('input', () => {
                        filterIssues(searchInput.value);
                    });
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('issues-list').innerHTML = '<p>Failed to load issues. Please try again later.</p>';
                }
            });
</script>
