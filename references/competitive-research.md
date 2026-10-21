# Competitive research

## Scope and candidate selection

Frame the decision: customer segment, market, alternatives, relevant purchase
constraints and intended strategic use. Keep requested products in scope. When
discovery is requested, identify direct rivals, other approaches to the same
job, manual substitutes and plausible adjacent entrants. Explain the selection
using audience/job overlap and actual evidence, rather than popularity alone.
Desk research cannot establish commercial win/loss rates without suitable data.

Create one product record per canonical URL and regional market. Normalize with
`scripts/model.py`; preserve regional paths, meaningful query parameters,
subdomains, and separate HTTP/HTTPS identities. Do not silently merge aliases:
resolve redirects/canonical identity before planning and reuse that URL in later
runs. Product ID deliberately excludes industry and display name.

## Collection and comparison

Start with official entry, pricing/terms and capability documentation. Follow
actual links instead of guessing paths repeatedly. Inspect relevant secondary
evidence for user needs and reputation. Record date, geography and plan context
for each assertion. A vendor announcement establishes a statement about launch,
not demonstrated customer adoption.

Normalize comparison dimensions before drawing conclusions: buyer job, service
boundary, entitlement, capability depth, usage unit, billing commitment, minimum
quantity, taxes, currency and region. Retain original plan names. Never imply two
tiers are equivalent merely because their names sound alike. Keep unavailable
prices, sales-only quotes, unknown terms and true free tiers distinct.

Use `comparisons` records to align claims across products. Their cells reference
claims, not freshly invented values. Include caveats for unequal evidence,
conditions, test access and geography. For custom dimensions set category
`custom` and the same `criterion_id` on the comparison and all referenced claims.
Do not rank products by raw feature count. Any weighted score needs criteria,
weight rationale, evidence and sensitivity; this version intentionally exports
evidence matrices without an opaque automatic score.

## Interpretation

Analyze positioning promises, intended customer, alternatives and proof offered.
Evaluate acquisition channels from observable campaigns, landing pages,
distribution, content and partnerships; do not infer channel efficiency from
their presence. Keep monetization mechanism separate from unknown revenue.

Strengths and weaknesses must concern observed outcomes or well-supported
statements. Link each to atomic claims, optionally with `polarity`. Gaps in
research belong in limitations. Express strategic opportunities as hypotheses
with supporting claims, priority, impact assumptions, effort assumptions and
next test. Keep anticipated market effects separate from established facts.

For repeated work, compare dated snapshots, acknowledging changed scope and
access. The current view is the latest completed run per product/market, not a
merge of old and new findings. Historical gaps stay visible and are not filled
using stale rows.
