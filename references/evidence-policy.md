# Evidence policy

## Three independent axes

**Provenance** identifies who produced the evidence: official, independent,
user report, or direct observation. **Status** describes how well the assertion
has been checked. **Confidence** is an analyst estimate between zero and one,
not a statistical probability or a substitute for evidence. Do not derive status
from a confidence threshold.

| Status | Required handling |
| --- | --- |
| VERIFIED | Direct evidence supports the precise assertion; source IDs resolve to accessed source records or screenshot IDs resolve to hash-checked files. Use an appropriate evidence type. |
| PARTIALLY_VERIFIED | Some accessible evidence exists; record an explicit `caveat` describing what remains unsupported. |
| HYPOTHESIS | Store only in `hypotheses`; describe an inference or proposed intervention, its basis and how to test it. No factual `value`. |
| UNVERIFIED | A question or report remains unconfirmed. No factual `value`; do not promote it into the executive summary. |
| NOT_ACCESSIBLE | Investigation was blocked. Document the actual barrier and access attempt. No factual `value`. |

An official source verifies **that the company says something**. Set
`company_statement: true` whenever an official source supports a claim, and phrase
the assertion as a company statement. A vendor's claim about outcomes, users,
revenue, performance or security is not independent verification of that result.
Vendor prices should be described as published prices with date, market, tax,
billing period, seat minimums and other terms. Export separates
`company_reported_value`, `partial_value`, and independently `verified_value`.

User reviews verify that the author reported an experience, not its prevalence
or that all users experience it. Cite sample size and dates when available. A
single observed journey establishes an outcome in that tested context, not a
population conversion rate. A page's privacy statement is not proof of actual
privacy practices; a visual accessibility check is not a compliance certification.

## Claim contract

Each claim/hypothesis has `claim_id`, `product_id`, `category`, `assertion`,
`status`, `evidence_type`, `source_ids`, `screenshot_ids`, `date_checked`,
`confidence`, `notes`, and `company_statement`. References resolve through
the source/screenshot registries to URL or local screenshot path. IDs are unique
within a run and are always joined using `run_id` in historical storage.

Use narrow atomic assertions. For structured comparison also provide `facet`
and `value`, with `unit`, `currency`, `billing_period` where relevant. Avoid
packing feature lists, multiple prices or several markets into one cell.
`criterion_id` is mandatory for category `custom`, prohibited otherwise.

Source records need product ownership, URL, title, provenance, access status,
check date, a short supporting excerpt or observed detail, locator, collection
method, and notes. Respect source copyright: keep excerpts short and paraphrase
where appropriate. A search URL is not evidence for the underlying fact. A source
record marked accessed must contain actual supporting text. Browser observations
may use an observation source record and/or a real screenshot.

Screenshots include product ID, relative `screenshots/<name>` path, actual source
URL, capture timestamp with timezone, caption, viewport, SHA-256. Collect only
needed surfaces; avoid sensitive data. If redaction is necessary, label it, hash
the stored redacted image, and document what was obscured. Never manufacture a
capture. The validator verifies file presence, safe paths and hash consistency;
it cannot prove the image depicts the stated URL.

## Conflicts and boundaries

Preserve contradictory claims as separate records with a `conflicts` relation
and explanation. Mark affected assertions partially verified or unverified with
explicit caveats. Do not average incompatible prices or select the convenient
source. Consider dates, plan tier, market, currency, tax treatment and audience
before declaring a conflict. A documented change over time is not inherently a
conflict. A missing page is not a missing feature.

The Python validator enforces schema, IDs, relationships, evidence requirements,
status separation, date ranges, company labels, category/custom coverage, browser
records and screenshot integrity. It **does not retrieve sources, verify textual
entailment, detect fabricated evidence, or replace analyst review**. Review every
assertion against its cited material before export. An inference must remain a
hypothesis even if it cites credible sources.

Use source check dates inside the run's start/completion date range. Do not
redate prior evidence to make it current. Set dates in one consistent research
timezone; timestamps must include offsets. Runs remain historical snapshots,
not continuously current facts.
