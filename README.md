# Product intelligence

A standalone Codex Skill for evidence-based product research, competitive
analysis and multi-product comparisons across industries. Codex gathers and
interprets evidence using the tools available in its session. Python validates
the structured research and generates Word reports and a historical Excel
database. The scripts are working offline CLIs, not an unattended web crawler.

This is an original implementation. It neither imports nor modifies the older
`product-deep-research` Skill. No API keys, paid scraping service, proprietary
plugin runtime, or extra browser integration is required by the Python code.

## Architecture

```text
User URL(s), market, depth, industry, custom criteria
    -> Codex research plan and available web/browser tools
    -> research.json + real screenshot assets
    -> JSON Schema + relational evidence validation
    -> staged python-docx report + openpyxl workbook
    -> immutable run bundles + snapshot registry + current/history Excel view
```

`SKILL.md` is the concise runtime entrypoint. Reference modules are read by phase.
`model.py` owns category vocabulary, normalized identity and plan defaults.
`schema_builder.py` owns the maintainable schema source. `validate_research.py`
owns offline validation. `report.py` owns document presentation. `database.py`
owns workbook projections, paths and storage locking. `export_research.py` owns
publication and rollback. Tests use only synthetic reserved-domain data in
isolated directories. Python 3.10 or newer is required.

```text
product-intelligence/
  SKILL.md
  README.md
  requirements.txt
  .gitignore
  references/
    competitive-research.md
    product-ux-research.md
    web-research.md
    evidence-policy.md
    report-structure.md
    research-schema.json
    methodology-sources.md
  scripts/
    __init__.py
    model.py
    schema_builder.py
    init_research.py
    validate_research.py
    report.py
    database.py
    export_research.py
  tests/
    __init__.py
    fixtures.py
    test_system.py
    create_demo.py
    artifacts/                     generated locally, excluded from installation
```

## Windows setup and verification

Run from the `product-intelligence` directory in PowerShell. `py` is the Windows
Python launcher; use an explicit working Python path if your launcher points to
an inaccessible Microsoft Store installation. A virtual environment avoids
global dependency changes. Activation is optional; an explicit interpreter
avoids PowerShell execution-policy issues.

```powershell
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
& .\.venv\Scripts\python.exe -m tests.create_demo
```

Dependencies are `python-docx`, `openpyxl`, and `jsonschema`. Format checks needed
for timestamps and UUIDs are enforced without optional format packages. No
pytest dependency is needed. The dependency ranges permit maintained compatible
updates; use a deployment-specific lock file if exact reproducibility is needed.
JSON Schema and semantic checks run before storage writes.

The demo creates **synthetic** DOCX/XLSX/JSON only under `tests/artifacts/`, with
explicit synthetic labels and `.example` domains. It never uses the default
production root. Open `tests/artifacts/outputs.json` for verified output paths.
The generated image is a test asset and is never represented as an actual product
capture. An initialized empty plan is an unevaluated gap report, not a research
result. Automated tests verify package structure and data; native Word/Excel
rendering is a separate visual QA step.

## Install after tests pass

User-scoped skills live under `~/.agents/skills/`; see the [official Codex skills
documentation](https://developers.openai.com/codex/skills/). No global installation
is performed by these scripts. From the workspace parent of this skill, use:

```powershell
$source = (Resolve-Path -LiteralPath '.\product-intelligence').Path
$target = Join-Path $env:USERPROFILE '.agents\skills\product-intelligence'
if (Test-Path -LiteralPath $target) { throw "Target exists; review it before updating: $target" }
New-Item -ItemType Directory -Path $target -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $source 'SKILL.md'), (Join-Path $source 'README.md'), (Join-Path $source 'requirements.txt') -Destination $target
Copy-Item -LiteralPath (Join-Path $source 'references') -Destination $target -Recurse
New-Item -ItemType Directory -Path (Join-Path $target 'scripts') | Out-Null
Get-ChildItem -LiteralPath (Join-Path $source 'scripts') -Filter '*.py' -File | Copy-Item -Destination (Join-Path $target 'scripts')
py -3 -m venv (Join-Path $target '.venv')
& (Join-Path $target '.venv\Scripts\python.exe') -m pip install -r (Join-Path $target 'requirements.txt')
```

This copies runtime files only. Tests, demo outputs, development dependency
folders and an existing virtual environment are not copied. Tell Codex to use
the installed `.venv\Scripts\python.exe` for this skill's script commands, or
use a session interpreter that already has the dependencies. If the skill does
not appear, restart the Codex session and confirm the folder contains SKILL.md
directly rather than a second nested `product-intelligence` directory.

## Research invocations

Single product, default report language Russian:

```text
Use $product-intelligence to research https://YOUR-PRODUCT-URL/.
Industry: retail. Market: Ukraine. Depth: deep.
Additional mandatory criteria: data portability, cancellation terms,
delivery coverage and customer support accessibility.
Export Word and the historical Excel database.
```

Comparison, English report:

```text
Use $product-intelligence to compare https://PRODUCT-A/ and https://PRODUCT-B/
for small businesses in Poland. Depth: standard. Report language: English.
Also investigate data export formats and minimum contract commitments.
```

Competitor discovery:

```text
Use $product-intelligence to research https://YOUR-PRODUCT-URL/ and identify
relevant direct competitors and substitute approaches for its core job.
Explain the selection, then compare the selected products for the stated market.
```

URL examples are placeholders. Codex must resolve real URLs before collection.
If several products are supplied, initialization defaults to comparison mode.
Set `--mode competitor` when the task is a competitive landscape study.

## CLI workflow

From the skill directory, using the configured Python interpreter:

```powershell
& .\.venv\Scripts\python.exe scripts/init_research.py --url "https://product.example/" --industry "Retail" --market "UA" --depth deep --criterion "Data portability" --criterion "Refund policy" --output "work/research.json"
```

Repeat `--url` for multiple products. Initialization creates a UUID, normalized
product IDs, the permanent 15-category checklist, and every custom criterion for
every product. It refuses to overwrite an existing plan. Fill the generated JSON
through actual research. Set scope, tools, limitations and completion time;
populate evidence registries, atomic claims, journeys, UX issues and hypotheses.
Never export the placeholder example above into production as real findings.

```powershell
& .\.venv\Scripts\python.exe scripts/validate_research.py "work/research.json" --assets "work"
& .\.venv\Scripts\python.exe scripts/export_research.py "work/research.json" --assets "work" --root "$HOME/product-research"
```

Omitting `--root` uses the same default. `--assets` defaults to the JSON file's
parent and must contain any referenced `screenshots/` files. Successful export
prints JSON with absolute report, research and workbook paths. Validation or
expected I/O failures return exit code 2 with a concise stderr message; argparse
usage errors also return 2. Unexpected programming errors remain visible.

To run Python helpers programmatically, add the skill directory to the import
path and import `scripts.model.new_run`, `scripts.validate_research.validate`,
and `scripts.export_research.export`. Pass an explicit isolated storage root in
any tests. The exporter never fetches URLs or automatically executes browser
actions. Research must happen before export.

## Configuration and evidence

| Setting | Default | Meaning |
| --- | --- | --- |
| URL(s) | Required | Canonical product identity, preserving regional variants |
| Industry | unspecified | Classification; does not change product ID |
| Market | global | Part of stable identity; keep naming consistent across runs |
| Depth | standard | quick, standard, deep; all categories/custom criteria persist |
| Mode | single or comparison | Also supports competitor |
| Language | ru | Russian/English labels built in; other languages use translated report_labels |
| Criteria | None | Arbitrary additional questions; no code changes required |
| Root | ~/product-research/ | Central local storage and competitors.xlsx |

Product IDs hash the normalized URL and case-folded market. Normalization removes
fragments/tracking parameters, default ports and trailing slashes; preserves
meaningful paths, query values and subdomains. It does not guess aliases or merge
HTTP and HTTPS. Choose and reuse a canonical URL before research. Market codes
are user-defined labels, so consistently use e.g. `UA` rather than alternating
with `Ukraine`. Read-only identity helper calls require no network.

The permanent framework covers overview/markets, positioning, audience/JTBD,
needs, features, services, pricing/terms, business model, acquisition, journeys,
usability, UI/design consistency, accessibility/responsiveness, trust/privacy/
reputation, and strengths/weaknesses/opportunities. See the [detailed
checklist](references/product-ux-research.md). Unavailable information is explicitly
not evaluated; not applicable requires a rationale.

Evidence statuses are VERIFIED, PARTIALLY_VERIFIED, HYPOTHESIS, UNVERIFIED and
NOT_ACCESSIBLE. Company statements remain attributed; unverified records have no
factual value fields. Hypotheses live separately. All references are relational,
and conflicts survive export. The validator checks record consistency and local
asset integrity, **not the truth or authenticity of supplied source content**.
Codex must review source support. See [evidence policy](references/evidence-policy.md)
and [schema/output contract](references/report-structure.md).

## Exports and history

```text
~/product-research/
  competitors.xlsx
  .snapshots/<run-id>.json
  <industry-slug>_<hash>/<stable-product-id>/<date>_<run-id>/
    report.docx
    research.json
    manifest.json
    screenshots/             only when supplied
```

Reports include the cover, executive evidence, methodology/limitations, 15
categories, all custom criteria, detailed UX audit, journeys, business/market
analysis, hypotheses, opportunities, comparisons, screenshots and source registry.
They match the requested language when Codex supplies translated prose/labels.

The workbook contains all required worksheets: Overview, Audience & JTBD,
Features & Services, Pricing & Business, Marketing, UX & UI, Strengths & Weaknesses,
Opportunities, Custom Research, Sources, UX Issues, Research History. Five
additional relational sheets preserve Evidence Links, Coverage, Journeys,
Comparisons and Conflicts without JSON blobs. Filter `is_current = TRUE` for the
latest snapshot per product/market. On Overview also filter
`record_type = product` for one current identity row per product. Latest means
completion timestamp, then lexical UUID for ties. Historical rows remain intact.

An identical run re-export is a byte-preserving no-op after integrity checks.
Changed content needs a new run ID. Multi-product runs place the same complete
comparison bundle under each product so each copy remains self-contained. The
workbook is a managed projection of immutable snapshots; manual workbook edits
are not imported and may be replaced by later exports/rebuilds. Export refuses
to replace an unrelated existing workbook without its internal ownership marker.
Do not point it at an unrelated database or transplant this marker manually.

## Recovery and Windows troubleshooting

| Symptom | Resolution |
| --- | --- |
| Python not found or Microsoft Store access error | Install/use a working Python 3.10+ interpreter; invoke its full path and create the venv from it. |
| PowerShell blocks Activate.ps1 | Use `.venv\Scripts\python.exe` directly; no policy change is needed. |
| Missing docx/openpyxl/jsonschema | Install requirements with the exact interpreter used to run scripts. |
| PermissionError replacing competitors.xlsx | Close the workbook in Excel and previews; verify the root is writable; retry the same validated run. The old workbook survives a normal failed commit. |
| Missing screenshot or hash mismatch | Verify `--assets`, relative path, exact file bytes and actual recorded hash; do not invent a replacement capture. |
| Validation rejects dates | Set correct timezone-aware start/completion times and actual source check dates; recheck old evidence rather than relabeling it. |
| Existing run ID has different content | Preserve that run and create a new UUID for revised research; do not edit archived bundles. |
| Stale workbook snapshot revision or missing workbook | Close Excel and run the rebuild command below. |
| Storage lock exists | Inspect the PID in `.export.lock`; wait for a live exporter. Only after confirming no export is active, remove that exact stale lock and recover. Automatic stale-lock deletion is intentionally absent. |
| Run directory exists without a snapshot | A process may have stopped before registry commit. Inspect the exact run directories and manifest, preserve/quarantine the uncommitted bundle outside the root, then retry the original research. Do not delete other history. |
| Archive manifest differs | Restore the bundle from a backup or investigate the exact modification. Do not regenerate hashes to conceal corruption. Rebuild refuses inconsistent archives. |
| Report has missing translated labels | Supply all required report_labels keys for languages other than ru/en, and author research prose in that language. |
| Word pagination or screenshots look wrong | Open in Word/LibreOffice, inspect all pages, adjust renderer styles/assets and re-test with a fresh isolated output. Use a DOCX rendering tool when available. |

```powershell
& .\.venv\Scripts\python.exe scripts/export_research.py --rebuild --root "$HOME/product-research"
```

Storage publication uses a lock, same-volume staging and atomic per-file
replacement. Normal exceptions roll back new bundles/snapshot before changing
the old workbook. A power loss or forced termination can interrupt a multi-file
commit: if the registry contains the run and bundles are valid, rebuild Excel;
if no snapshot was committed, inspect/quarantine that uncommitted run before
retrying. Back up the whole root. Local disk is recommended; network shares and
cloud sync may not honor the same lock/replace assumptions.

## Tests and limitations

The suite covers schema conformance, evidence requirements, provenance labels,
hypothesis separation, screenshots, browser-record honesty, all Word sections,
all required Excel sheets, normalized evidence/custom rows, duplicate identity,
multiple industries, repeated/backdated runs, current view/history, idempotence,
input and disk/file-lock failures, archive corruption, rebuild, literal formula
text and CLI exit behavior. Temporary directories isolate each test. Demo files
are an additional inspectable sample, not production data.

Research quality depends on actual access and analyst judgment. Browser tests,
authenticated flows, screenshots, native Word/Excel viewing and web search depend
on available Codex tools. The scripts do not certify accessibility, estimate
private market metrics, run surveys or claim customer conversion data. There is
no unattended crawler, automatic scheduling, paid data connector, automatic
translation service or opaque product scoring. These are deliberate boundaries,
not hidden integrations.

Excel is rebuilt from all archived snapshots and archive assets are checked on
export. This favors integrity over very large-database throughput; memory/time
grow with history. XLSX also has Excel's worksheet row limits. The current
implementation is suited to research libraries rather than millions of records.
Concurrent writers fail fast and should be retried after the active export.
Hashes detect accidental changes but are not cryptographic proof of research
authenticity. Visual QA must be recorded separately from automated package checks.

## Methodologies and licenses

All three requested sources were verified and reviewed before design: Anthropic
Competitive Brief, OpenAI Product Design Research, and Firecrawl Competitor
Analysis. Their observed license declarations were Apache 2.0, Proprietary and
MIT respectively. Only general methodological principles informed this original
implementation. See [methodology-sources.md](references/methodology-sources.md)
for exact source/license links, review date, redistribution conditions and the
proprietary-content boundary. No third-party skill code/text is bundled.
