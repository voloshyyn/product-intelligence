# Methodology review and licensing

Reviewed online on **2026-10-21** before designing these modules. All three
requested source files existed. Links to `main` are moving references; this
review records the observed state, not a promise of future license conditions.
This project contains original instructions and Python code. No source code,
skill text, plugin router, proprietary asset or third-party command was copied.

| Source | Useful methodological principle | Observed licensing evidence |
| --- | --- | --- |
| [Anthropic Competitive Brief](https://github.com/anthropics/knowledge-work-plugins/blob/main/product-management/skills/competitive-brief/SKILL.md) | Link comparison to a decision, distinguish alternatives, consider buyer priorities, and state strategic implications with pricing caveats. | The scoped [product-management LICENSE](https://github.com/anthropics/knowledge-work-plugins/blob/main/product-management/LICENSE) declares Apache 2.0. Redistribution of licensed material requires the license, relevant notices and change notices; applicable NOTICE terms must be retained. No such material is redistributed here. |
| [OpenAI Product Design Research](https://github.com/openai/plugins/blob/main/plugins/product-design/skills/research/SKILL.md) | Separate observed user friction from inference and rank issues while acknowledging evidence weakness. | The plugin [manifest](https://github.com/openai/plugins/blob/main/plugins/product-design/.codex-plugin/plugin.json) explicitly declares `Proprietary`. Root LICENSE/LICENSE.md/LICENSE.txt and plugin LICENSE/LICENSE.txt checks returned 404. Public availability does not grant redistribution rights. Only general research ideas informed original writing; no plugin material or integrations are bundled. |
| [Firecrawl Competitor Analysis](https://github.com/firecrawl/web-agent/blob/main/agent-core/src/skills/definitions/competitor-analysis/SKILL.md) | Collect comparable entry, pricing and capability evidence; normalize conditions and retain the actual source registry. | The repository [LICENSE](https://github.com/firecrawl/web-agent/blob/main/LICENSE) declares MIT, copyright 2026 Firecrawl. Reusing substantial material requires its copyright and permission notice. This project does not redistribute it or require Firecrawl. |

The architecture follows the user's requested 15-category framework and original
data/evidence contracts. Vendor-specific slash commands, router/context skills,
`spawnAgents`, `agent.run` and output-format helpers from the references are not
part of this skill. Browsing and journey tools are discovered from Codex at runtime.

Licenses for installed Python packages remain their own; dependencies are listed
in requirements.txt and are not vendored into the installable skill. This review
is a record of observed license declarations, not legal advice or a grant of rights
over third-party content. Recheck the relevant scoped license if incorporating
third-party material in future changes.
