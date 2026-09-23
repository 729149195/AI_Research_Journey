---
name: knowledge-evidence
description: Read original research material, extract exact evidence and maintain supporting, refuting and qualifying Claim relationships. Use whenever a citation, result, source or Claim meaning changes.
compatibility: Authorized source-reading tools and the local Workspace CLI. Human verification remains separate.
metadata:
  version: "0.1.0"
---

# knowledge-evidence

## Inputs

Current Claim text, strength and scope; source candidates; authorized original material; research question; Source Policy; existing evidence, contradictory findings and review issues. Read the actual source instead of inferring its contents from title, abstract-only metadata or another AI's summary.

## Workflow

1. Verify identity, version, publication status and original-source role for the specific research question. Obtain a lawful readable original or bounded UTF-8 extract preserving locator and context. If only an abstract is accessible, explicitly limit the evidence to it.
2. Record the design, sample/system, measures, comparison, assumptions, results, uncertainty and limitations needed to interpret the passage. Distinguish author conclusions, observed results and your interpretation.
3. Create a source node with category, original URL/local provenance and snapshot path. Do not label a record peer reviewed just because it has a DOI or a journal-like provider type.
4. Create one evidence record per meaningful relation: source, claim, exact quote, locator, scope and relation (supports/refutes/qualifies). Quote only necessary material, preserve qualifications and record table/figure/page context. Evidence must depend on its source; Claims must depend on all relevant evidence, including refutations and qualifications.
5. Maintain a matrix: Claim ID | exact bounded assertion | evidence ID | relation | original locator | applicability | verification state | unresolved issue. This is a view of the state, not a second competing truth database.
6. Check whether methods and populations support the stated inference. Document real counterevidence search coverage and Claim responses. Absence in one search is not evidence of universal absence.
7. Submit proposed nodes. Ask the actual verifier to open originals and record their checks via `rw verify SRC-ID --human --actor NAME --note "..."`, then EVD-ID. Never execute human declarations on the author's behalf.
8. On source, quote, Claim text/strength/scope or result changes, invalidate/reassess old applicability and run `rw impact ID`. Hand affected methods/logic, sections, figures and conclusions to their Skills.

## Outputs

Evidence matrix, precise source/Claim/evidence operations, discrepancies, counterevidence responses still needed and downstream review tasks. Return base_fingerprint and proposal operations. No fabricated verification receipts, experimental results or scientific certainty.

## Boundaries

Exact quotation matching detects integrity, not entailment. Human declarations do not authenticate identities. A preprint remains a preprint. A newspaper/blog can be primary corpus material for an explicitly justified study of that text, while general commentary remains discovery-only. Decisions and AI memory cannot support a factual Claim.

## Evaluation

A quote absent from the original must fail. A source edited after verification must require recheck. Changing association to causation must not retain evidence applicability automatically. Strong contrary evidence must remain visible even when inconvenient to the argument.
