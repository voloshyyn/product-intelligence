# Product and UX research checklist

## Permanent framework

Use these exact category IDs. All 15 require a coverage record per product.
Custom criteria supplement this table and never replace its rows.

| ID | Category | Questions and evidence targets |
| --- | --- | --- |
| overview | Product overview and geographic markets | What is offered, by whom and where? Check company/product pages, supported locale and region conditions; site language does not prove market availability. |
| positioning | Positioning and unique value proposition | What promise, category and differentiation does the company communicate? Separate attributed messaging from demonstrated outcomes. |
| audience | Target audience and jobs to be done | Who is addressed, in which context, trying to accomplish what? Distinguish marketing segments, observed users and inferred jobs. |
| needs | User problems and needs | What problems are described or observed? Preserve evidence scope; complaints do not establish prevalence. |
| features | Features and functionality | Which atomic capabilities, limits, prerequisites and integrations are documented or tested? Unknown does not mean absent. |
| services | Products and services | What product lines, service components, delivery models and support offerings exist? Distinguish bundled from optional. |
| pricing | Pricing plans and terms | Price, currency, region, taxes, billing, minimum commitment, limits, trial, renewal, cancellation and sales-only conditions. Never infer a missing amount. |
| business | Business model and monetization | Who pays, for what and by which unit? Separate observed revenue mechanisms from unavailable financial performance. |
| marketing | Marketing and customer acquisition | Which channels, messages, conversion paths and partnerships are observable? Do not invent spend, traffic, CAC or conversion. |
| journeys | Core user journeys | How do users discover, evaluate, start, complete and recover from a central task? Record actual steps and barriers. |
| usability | UX heuristics and usability | Assess feedback, task fit, control, consistency, error prevention, recognition, efficiency, recovery and help in context. |
| design | UI design system and visual consistency | Inspect hierarchy, typography, color, components, spacing, states and content patterns on sampled screens. Do not infer internal tokens from appearance. |
| accessibility | Accessibility and responsive behavior | Inspect keyboard/focus, names/labels, text alternatives, legibility, contrast when measured, zoom/reflow and narrow viewports. Record method and scope. |
| trust | Trust privacy and reputation | Identify business identity, terms, privacy statements, permissions, security disclosures, reputation and source bias. Policy text is an attributed statement, not proof of compliance. |
| strategy | Strengths weaknesses and strategic opportunities | Synthesize supported strengths and weaknesses; formulate opportunities separately as testable hypotheses. Research gaps are neither weaknesses nor threats. |

For a product without a digital self-service interface, investigate its actual
customer journey, service interactions and available digital touchpoints. Mark
specific UI/accessibility dimensions not applicable only with a rationale. Lack
of access to a physical service or authenticated interface is not evaluated.

## UX records

Anchor each `ux_issues` record to one claim, with user goal, surface, heuristic,
frequency signal, severity and recommendation. Its status comes from that claim.
The exporter preserves uncertain issue statuses instead of upgrading them.
If only a user report supports an issue, describe it as a reported experience.
Put a speculative problem in `hypotheses` with a next test.

Severity is an explicit judgment, not a measured business result:

| Value | Meaning |
| --- | --- |
| 0 | Observation with no demonstrated task impairment |
| 1 | Minor friction; straightforward workaround |
| 2 | Material delay, confusion or repeated effort in the observed task |
| 3 | Important task blocked or serious error risk in the observed context |
| 4 | Critical observed barrier to a core task with no acceptable recovery |

Do not equate severity with population frequency. Use `frequency_signal` to
state actual sample information or explicitly say frequency is unknown.
Opportunity priority P0–P3 expresses recommended sequencing; impact and effort
are estimates with assumptions. Avoid fabricated conversion improvements.

For journey records distinguish documented/anticipated flows from executed
tasks. Include the entry state, step order, actions, expected result, observed
result, evidence claim IDs, tool/time and outcome. Steps can reference several
atomic claims. A desk flow remains `not_tested`. Do not call visual inspection
an interview, participant study or formal usability test.

## Accessibility scope

Apply established accessibility principles using available inspection tools.
Consult current primary standards when asserting a specific requirement; record
the version and criterion. A limited heuristic review cannot certify compliance.
If a metric such as contrast is not measured, phrase it as a concern requiring
measurement and retain uncertainty. Test viewports and input methods explicitly
and do not generalize to devices or assistive technologies not exercised.

## Synthesis

Separate observed workflow issues, feature gaps, content/help issues and
reliability reports. Connect evidence to the user goal and practical implication.
For custom criteria with no UX relevance, research the appropriate business,
technical, market or operational sources rather than forcing them into UX.
