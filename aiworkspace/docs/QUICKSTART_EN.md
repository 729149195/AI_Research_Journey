# English quickstart

AI Research Workspace is a local-first, evidence-governed research framework. The engine, nine editable Agent Skills, templates, tests and documentation live under `aiworkspace/`; the public updater and main usage README sit at the repository root. The existing Vue application is preserved and is not required.

## Install and run a real software demonstration

Python 3.11+ and Git are required. Run from a terminal:

```bash
git clone https://github.com/729149195/AI_Research_Journey.git
cd AI_Research_Journey
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-deps --no-build-isolation -e ./aiworkspace
rw doctor
rw demo ../research-demo
```

On Windows use `py -3 -m venv .venv`, then `.venv\Scripts\python.exe` for Python commands and `.venv\Scripts\python.exe -m research_workspace` instead of `rw`. No execution-policy change is needed. Runtime dependencies are standard-library only; installation needs the build tools above.

The demo actually computes synthetic observations, creates JSON/text/SVG artifacts, links Claims and evidence, synchronizes both directions, tests an incremental asset update and rollback, and exports only a explicitly labeled demonstration package. Simulated human declarations are not real expert review. View `../research-demo/workspace/reports/dashboard.html` offline and read `walkthrough.json`. Use a new destination when repeating it.

## Create a separate research study

```bash
rw init ../my-paper --name "My research paper" --author "Your name"
rw --project ../my-paper status
rw --project ../my-paper review
```

A fresh study is expected to be blocked. Fill `workspace/research/idea-evaluation.md` and `workspace/rules/project-policy.md`. The study has sibling `workspace/` and `manuscript/` directories. Store private research outside the public framework checkout. Keep `.rw/framework.json`; it is the update baseline.

The Idea Evaluation template faithfully retains the supplied ten-part visualization-research structure. Its source transcription and adapted worksheet are Markdown, with added Workspace fields identified. No PPT binary or invented scoring rubric is distributed; original template rights remain reserved.

## Bring your own authorized agent

```bash
rw --project ../my-paper skills install --target .agents/skills
# For a Claude Code host, choose .claude/skills instead.
rw --project ../my-paper packet idea-evaluation --task "Review my filled idea worksheet and identify evidence gaps"
```

Start the host at the study root and ask it to read START_HERE.md and AGENTS.md. Skill files do not grant a model account, network permission or database access. Alternatively pass an authorized task packet to your model. The model returns proposed operations; it must not impersonate a human verifier or reviewer.

```bash
rw --project ../my-paper propose aiworkspace/examples/first-proposal.json --actor ai-session
rw --project ../my-paper show PROP-ID
rw --project ../my-paper apply PROP-ID --actor "Your name" --approve --note "I reviewed the actual draft change and its implications; scientific validation is still pending."
```

Replace placeholder IDs with actual returned IDs. Next, verify original sources, execute reviewed analysis, prepare writing/figures and synchronize. `rw sync propose` is itself a proposal. Both-side conflicts require explicit choices; manuscript edits create semantic review tasks. `rw review` and `rw cycle --actor coordinator` identify the next work rather than running an invisible agent loop.

## Update an already-used study

From the framework repository root, stop active writers, back up research data, and use the dedicated venv:

```bash
python update_aiworkspace.py --project ../my-paper --check
python update_aiworkspace.py --project ../my-paper --apply --actor "Your name"
```

Add `--expected-commit FULL_PREVIEWED_SHA` to lock the reviewed target, or `--offline` to use fetched objects. The three-way asset merge preserves local-only edits, merges nonoverlapping changes and stops on conflicts. Research state, filled worksheets, project policy, evidence, data, methods, results and manuscripts are not asset overwrite targets.

```bash
rw --project ../my-paper upgrade history
rw --project ../my-paper upgrade rollback UPDATE-ID
```

Rollback protects subsequent local edits and restores managed assets only. Engine recovery is separate. Unknown schemas are blocked; no guessed migration resets a study. See [Updating](UPDATING.md).

## Verification and limitations

Run `python aiworkspace/scripts/run_tests.py`, `python aiworkspace/scripts/smoke_root_update.py`, and `python aiworkspace/scripts/check_docs.py`. Read [Delivery](../DELIVERY.md) for actual results and limitations. Native sync is Markdown-only; full Word/LaTeX/Overleaf round trips, authenticated approvals and real-time collaborative storage are not implemented. External API mode is opt-in and was tested with mocks, not a paid live provider. Machine integrity checks do not certify scientific validity or publication readiness.

See [Architecture](ARCHITECTURE.md), [Schema](SCHEMA.md), [Skills](SKILLS.md), [Contributing](../CONTRIBUTING.md) and [Security](../SECURITY.md).
