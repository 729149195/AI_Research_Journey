---
name: logic-methodology
description: Maintain the whole-paper argument and choose or audit research design, statistical inference and reproducible analysis. Use for changed questions, contribution, Claim strength, methods, data or reviewer objections.
compatibility: Local state and authorized analysis tools; actual code execution requires explicit permission.
metadata:
  version: "0.1.0"
---

# logic-methodology

## Inputs

Question, hypothesis/core idea, contribution, full argument, sections, Claims, source/evidence relationships, study design, data/code provenance, rules and current issues. Use Idea Evaluation when a direction changes. Separate known observations, assumptions, exploratory proposals and confirmed conclusions.

## Workflow

1. Build an explicit question → core idea → overall argument → section role → Claim → evidence/method/result → discussion → conclusion map. Identify unsupported transitions, circular justification, missing premises, inconsistent terms and sections with no argumentative role.
2. State the intended inference, estimand/outcome, unit of analysis, target population/system, comparator and validity limits. Compare a few feasible designs and explain what each can and cannot answer; let the author decide.
3. Examine selection, measurement, confounding, randomization/blinding where relevant, dependence, missingness, multiplicity, stopping rules, power/precision and robustness. Apply domain-specific frameworks only when applicable. Do not choose a test solely from a mechanical normality-test flowchart.
4. Keep effect size, uncertainty, substantive meaning and model assumptions distinct from significance. Avoid claiming that a p-value proves an effect or that nonsignificance establishes equivalence. Causal wording needs a defended identification strategy and expert review.
5. Propose method nodes, declared inputs, versioned outputs, script path, parameters and seed. Keep raw inputs unchanged; write inspectable code. Ask permission before execution. `rw run MTH-ID --allow-exec --actor NAME` records a real local run; it is not a security sandbox.
6. Verify dimensions, units, preprocessing, data leakage, exclusions, failed runs, sensitivity, output hashes and figure derivations. Preserve previous outputs; a new run uses new paths. Never populate results that were not generated.
7. Reassess every affected Claim and section, especially abstract, discussion, conclusion and captions. Changing “causes” to “is associated with” requires inferential and interpretive changes throughout, not only a text replacement.
8. Submit a proposal with remaining assumptions, alternatives, tests and failure/revisit conditions. Decisions record reasoning but do not become factual evidence. Send independent methodological objections to Reviewer.

## Outputs

Argument map, design/analysis comparison, method/result provenance requirements, appropriately bounded Claim changes, code-review findings and global impact tasks. Return base_fingerprint and reviewable operations. Actual execution receipts are created by the runner, not by an LLM response.

## Boundaries

A graph with no missing IDs can still be scientifically incoherent. Numerical reproducibility does not establish construct validity or ethics. Do not retroactively portray exploratory choices as preregistered. Do not fabricate an analysis, hide failed designs or optimize only for a desired conclusion.

## Evaluation

Individually plausible paragraphs with a broken overall inference should be flagged. Causal Claims without identification should block release. A changed method or dataset should invalidate stale results. A negative/contrary result should change the argument and scope, not disappear.
