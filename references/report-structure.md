# Data contract and report structure

## Preparation

The JSON schema is the interchange contract; `schema_builder.py` is its readable
maintenance source. Regenerate the JSON with `python scripts/schema_builder.py`
after editing it. Tests require schema and builder to agree. Schema version 1.0
rejects unknown fields rather than silently discarding misspelled criteria.

Initialize JSON with `init_research.py` instead of hand-building the top-level
structure. Its defaults are a valid **unevaluated** plan, which can be exported as
a gap report if research access fails. Before treating research as finished,
replace pending reasons and describe actual coverage. `started_at` marks the
start; update `completed_at` after collection. Both are ISO 8601 with timezone.
Do not move the start backward merely to accept stale sources.

`products` holds stable identity, display name, canonical URL, industry and
regional market. Industry is a classification, not part of identity. Each
regional identity is a separate product record. Mixed-industry and mixed-market
comparisons are supported by the schema. Set these fields **before** collection;
when changing a market recompute its product ID and update its initial coverage
and custom result rows. Use the same canonical URL/market on subsequent runs.

## Claim example

This is a **synthetic record shape**, not an actual product finding. Replace
all sample values and IDs with researched evidence; never insert this example
in production storage.

```json
{
  "claim_id": "plan_monthly",
  "product_id": "p_REPLACE_WITH_COMPUTED_ID",
  "category": "pricing",
  "assertion": "The company publishes a monthly seat price in the specified market.",
  "status": "VERIFIED",
  "evidence_type": "official_statement",
  "source_ids": ["pricing_page"],
  "screenshot_ids": [],
  "date_checked": "2026-01-15",
  "confidence": 0.8,
  "notes": "Record actual billing, taxes, region and minimum commitment here.",
  "company_statement": true,
  "facet": "published_price",
  "value": 12,
  "currency": "USD",
  "unit": "seat",
  "billing_period": "month"
}
```

Resolve `source_ids` to `sources` records; screenshots require real files and
hashes. `facet` names an atomic comparable attribute. Free-form assertions are
still required so a numeric value is never detached from its meaning/conditions.
For unsupported values omit `value` entirely. Hypotheses and unverified claims
cannot carry it. Partial values export into their own explicitly partial column.

For a custom claim use `category: custom` with the criterion's `criterion_id`.
Create one `custom_results` row per product/criterion, even if the result is
not applicable or not evaluated. Additional criteria require no code edits.

Relations are explicit: `ux_issues.claim_id`, journey step `claim_ids`,
`opportunities.hypothesis_id` and `basis_claim_ids`, conflict `claim_ids`, and
comparison cells' product/claim IDs. Do not reference a claim from another
product in a product-specific journey or issue. Cross-product comparisons use
their explicit cells instead.

## Word report

The renderer creates a cover identifying products, market, scope, run and date;
supported executive claims; collection method, depth, tool coverage and
limitations; all 15 categories per product; every custom criterion; detailed
UX issues ordered by severity; executed or desk journeys; a separate hypothesis
section; strategic opportunities ordered P0 to P3; comparison evidence;
conflicts; available screenshots; and source verification details.

Each claim carries its ID, verification status, company statement label where
applicable, caveat, evidence IDs, date and confidence. Unsupported assertions
remain visibly unsupported. Source records include hyperlinks and short evidence
extracts. Screenshots preserve aspect ratio and fit the page. Tables repeat
headers; headings use a restrained black hierarchy and a page-number footer.
Strengths/weaknesses and business/market analysis appear in the standard
categories; `polarity` preserves the distinction in Excel.

Russian and English section labels are built in. Codex must author the research
prose in the requested language. For any other language, add `report_labels` with
translations for every key in `scripts/report.py:LABELS` and all 15 category IDs.
The renderer fails clearly if translations are missing; it never silently exports
English headings for a different requested language. Status/ID codes and worksheet
names remain stable. User/source quotations may retain their original language.

## Excel model

All rows include run, product, industry, market, completion timestamp and
`is_current`. Filter it to `TRUE` for the latest **complete snapshot** per product,
using completion time and lexical run ID as a deterministic tie-break. A new run
does not silently inherit prior findings absent from that snapshot. A later
incomplete run can become current; its coverage and limitations make that visible.

| Worksheet | Record grain |
| --- | --- |
| Overview | One identity/coverage row per product/run plus overview, positioning and trust claims |
| Audience & JTBD | One audience or needs claim |
| Features & Services | One capability or service claim |
| Pricing & Business | One pricing or monetization claim with typed value/units |
| Marketing | One acquisition or messaging claim |
| UX & UI | One journey, usability, design or accessibility claim |
| Strengths & Weaknesses | One strategy claim or separated hypothesis, with record type and polarity |
| Opportunities | One recommendation linked to a hypothesis |
| Custom Research | One coverage row per criterion/product/run plus atomic custom claims and hypotheses |
| Sources | One source or screenshot registry record |
| UX Issues | One issue, linked to its assertion/status |
| Research History | One product/run/limitation row, or one row when no limitations |
| Evidence Links | One claim/source, claim/screenshot or hypothesis/basis-claim relation |
| Coverage | One standard category or custom criterion evaluation |
| Journeys | One journey step/claim relation; empty reference for an untested desk step |
| Comparisons | One comparison/product/claim cell |
| Conflicts | One conflict/claim relation |

The five additional worksheets preserve relational records without JSON blobs or
large packed lists inside cells. All tables provide filters and frozen headings;
URLs and output files are hyperlinks. Date fields are typed Excel dates;
confidence and numeric values remain numeric. Text resembling a formula is stored
as literal text. Do not sum claim counts as product counts: use Overview rows
with `record_type = product`, and `is_current = TRUE` for the unique current list.

## Storage and transaction boundaries

Default root is `~/product-research/`. Each industry's safe slug has a short hash
to prevent sanitized-name collisions; the product directory uses its stable ID.
Run directories use completion date and UUID:

```text
product-research/
  competitors.xlsx
  .snapshots/<run-id>.json
  <industry-slug>_<hash>/<product-id>/<date>_<run-id>/
    report.docx
    research.json
    manifest.json
    screenshots/               when captured
```

For a multi-product run, each product receives the same self-contained comparison
report/JSON and evidence bundle. This intentionally duplicates screenshots to
keep every bundle independently inspectable and valid. `manifest.json` protects
bundle integrity. `.snapshots` is the immutable central registry used to rebuild
Excel; do not hand-edit it. These hashes detect accidental changes, not adversarial
tampering or fabricated source evidence.

Validation precedes any storage writes. Export locks the root, validates archived
bundles, builds all outputs in a staging directory on the target volume, then
publishes bundles, snapshot, and workbook. Ordinary errors roll back newly
published bundles/snapshot; the old workbook is replaced only as the final commit.
An identical run/content re-export verifies bundles and workbook snapshot revision
and performs no writes. Different content under an existing run ID is rejected.

Atomicity is per filesystem replacement. Power loss/process termination between
multiple replacements can leave recoverable partial publication; this is not a
distributed transaction. See README recovery. Keep the storage on a local disk;
network/cloud sync locking semantics are outside this guarantee. Excel is a
managed view: manual workbook changes are not imported and rebuilding replaces
them. Back up the entire root, not only the workbook.
