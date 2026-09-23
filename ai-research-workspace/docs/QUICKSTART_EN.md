# Start without previous context

AI Research Workspace is a local-first research beta with a standard-library Python CLI and nine portable Skills. It keeps research state and manuscript as sibling directories. It does not include a large language model, authenticate reviewer identities, or certify scientific validity.

## Install and try

Install Python 3.11+ and Git, clone the repository's feat/ai-research-workspace branch, and enter ai-research-workspace. After the PR is merged, the default branch can be used.

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
rw doctor
rw demo ../../research-demo
```

The demonstration requires no API key. It creates synthetic paired data, actually runs a descriptive calculation, records evidence and result provenance, synchronizes both directions, exercises project asset upgrades/rollback and checks release gates. All human verification and review declarations in the example are explicitly simulated. Open research-demo/workspace/reports/dashboard.html and walkthrough.json. The dashboard is an offline read-only snapshot.

## Create your study

Keep study directories outside the framework Git checkout:

```bash
rw init ../../my-paper --name "My study" --author "Your name"
rw --project ../../my-paper skills install --target .agents/skills
# Claude Code: --target .claude/skills
rw --project ../../my-paper packet idea-evaluation --task "Critique my idea, compare feasible options and identify missing evidence."
```

Open my-paper in your authorized coding agent. Read START_HERE.md, AGENTS.md, project policies and workspace/state.json. Fill workspace/research/idea-evaluation.md; empty templates remain in workspace/templates for future upgrades. The worksheet preserves the owner's ten-slide visualization-oriented planning structure and separates added Workspace fields from the original text.

The workflow is discovery → original reading → evidence verification → logic/methods → proposals → approval → writing/figures → synchronization → independent review → next tasks. Unknown facts, unrun experiments and unavailable sources stay unknown. History and AI memory are context, not evidence.

## Apply changes explicitly

An ordinary task response returns summary, base_fingerprint and operations. An upsert contains a complete node, not a partial patch. Markdown writes need the original file hash. Stage JSON using `rw propose FILE --actor NAME`, inspect the returned proposal with `rw show ID`, then the accountable author applies it with `rw apply ID --actor NAME --approve --note "Actual checks and reasons"`.

`rw sync status` shows both sides against the previous baseline. `rw sync propose --actor sync-agent` creates a proposal; divergent edits need explicit resolution. Every manuscript-to-research change creates semantic review work. Text equality does not establish that Claims, methods and conclusions are scientifically consistent.

`rw review` writes machine checks; return code 1 means the quality gate remains blocked. `rw cycle --actor coordinator` routes issues to Skills without starting a background autonomous loop. Qualified people perform domain reviews; current-snapshot declarations and author release are required before `rw export NEW_DIRECTORY`.

## Incremental upgrades after real use

Close active study writers. In the framework checkout and its dedicated virtual environment:

```bash
python scripts/update.py --project ../../my-paper --ref origin/feat/ai-research-workspace --check
python scripts/update.py --project ../../my-paper --ref origin/feat/ai-research-workspace --apply --actor "Your name"
```

After merge, normally switch your clean Git checkout to main and use origin/main. A squash merge may create divergent history; the updater refuses forced resets. It never automatically stashes or discards source edits.

The project updater compares the previous defaults, current local files and new defaults. Non-overlapping edits merge; unresolved conflicts stop the whole asset update. Filled research, raw data, evidence, methods, project-specific policy and manuscript are never default-asset targets. Preserve .rw/framework.json and maintain separate full research-data backups.

```bash
rw --project ../../my-paper upgrade check
rw --project ../../my-paper upgrade apply --actor "Your name" --approve
rw --project ../../my-paper upgrade history
rw --project ../../my-paper upgrade rollback UPDATE-ACTUAL_ID
```

These subcommands update project defaults only. The Python script additionally fetches and installs framework code. Git/pip/project writes are separate stages; partial failures are reported. Rollback refuses to overwrite edits made after an update. Unknown research schemas are refused until an explicit tested migration exists. See [UPDATING](UPDATING.md).

## Models, privacy and actual verification

External AI is disabled until project consent, an HTTPS host allowlist, RW_API_KEY and explicit per-call permission are supplied. The API adapter is one bounded JSON request, not a browser/tool agent. An authorized coding-agent host can perform multi-step work using its own permitted tools. See [SKILLS](SKILLS.md).

Markdown is the native manuscript format. Word, LaTeX, Overleaf, Zotero and authenticated multi-user editing are not implemented. Local Python execution is not sandboxed. Do not upload confidential manuscripts, personal/participant data or credentials to a public repository or unauthorized model service.

Run the tests and consult the actual GitHub Checks. [TEST_REPORT](TEST_REPORT.md), [architecture](ARCHITECTURE.md), [schema](SCHEMA.md), [contribution rules](../CONTRIBUTING.md) and [security](../SECURITY.md) explain what was implemented, how to validate it and what remains outside the guarantee.
