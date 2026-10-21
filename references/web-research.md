# Web research and browser operations

## Depth and coverage

Depth controls effort, not which criteria exist. Start with these adaptable
budgets; expand when necessary to address mandatory custom criteria or material
contradictions. Report limits instead of pretending a budget guarantees coverage.

| Depth | Starting source budget per product | Journey emphasis |
| --- | --- | --- |
| quick | Entry, price/terms, key capability/help, policies, one relevant independent source if available | Attempt one primary reversible task |
| standard | All core page types, audience/market evidence, several independent perspectives | Attempt discovery, consideration and primary task; desktop and narrow viewport |
| deep | Broader product/service surfaces, plan conditions, reputation samples and contradictory evidence | Several key tasks plus recovery, keyboard, errors, responsive and relevant authenticated flows when authorized |

For each checklist item record intended question, source approach and completion
state. The structured `coverage` and `custom_results` are the durable checklist;
use their `reason` to record the plan initially and actual coverage at completion.
Keep `NOT_APPLICABLE` with a product-specific rationale distinct from
`NOT_EVALUATED` with an access or scope limitation. No category may disappear.

## Source workflow and reuse

Use available search tools for discovery; prefer primary documents for product
conditions. Read the relevant page. Follow help, pricing, legal, locale and
support links when relevant. Independent sources should contribute context or
counterevidence, not merely duplicate company press releases.

Maintain the source registry as a run-local cache keyed by URL, product, market,
locale and auth state. Record the actual retrieval/check date and content
locator. Reuse a visited source within a run when the context is unchanged.
Revisit only to resolve a missing detail, changed state or contradiction.
Screenshots are cached evidence of a specific state and viewport, not live data.
Prior-run material is historical until checked again; record changes honestly.

Record access failures with URL, date, attempted method and observed reason.
Do not bypass login, CAPTCHA, regional restrictions or paywalls. Try another
legitimate source when it answers the same question. If search is unavailable,
inspect available sources and disclose the narrower evidence set. If all access
fails, export an honest gap report rather than assertions about the product.

## Browser execution

Discover the actual browser/Playwright tools exposed by this Codex session and
follow their documentation. This skill defines no imaginary API or required
Firecrawl integration. Read the available browser skill when that tool requires
it. Do not install browser packages as a hidden prerequisite.

Use a dedicated task tab where possible. Establish market, viewport, locale and
authentication state. Test goal-based tasks with expected and actual outcomes.
Record actual tool name, time, steps, observations and claim IDs in `journeys`.
A blocked flow is still useful evidence of the observed barrier, with a caveat
about its scope. Desk reconstructions must use `method: desk` and
`outcome: not_tested`; do not present expected steps as observed outcomes.

Screenshots are optional when tools cannot save them. Use actual screenshots
only, with a traceable URL and capture time; copy them into the working
`screenshots/` directory. Compute hashes, for example:

```powershell
Get-FileHash -LiteralPath "work/screenshots/onboarding.png" -Algorithm SHA256
```

If browser testing is unavailable set `browser_available: false`,
`browser_tested: false`, a reason, and explicit limitations. If available but not
used, keep `browser_tested: false`. A true flag requires a recorded browser
journey with supported observation claims. Never claim mobile-device testing
from resizing a desktop window; describe it as a viewport test.

Navigate and inspect reversible states within the user's scope. Stop before
payment, real personal-data submission, creating external commitments, messaging
others, deleting data or irreversible actions unless specifically authorized.
Existing permission persists. Do not solicit unnecessary account access.

## Finishing collection

Set completion time after collection, translate authored findings into the
requested language, resolve relationships and run validation before publishing.
Do not paste raw page dumps into report sections. Source excerpts stay short;
structured claims, journeys, issues and opportunities carry the analysis.
