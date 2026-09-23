---
name: rules-compliance
description: Gather and apply actual institution, supervisor, journal, reporting, ethics, citation, AI-use and writing rules. Use at setup, venue changes, policy updates and final review.
compatibility: Current official rule sources, project policy files and explicit human authorization.
metadata:
  version: "0.1.0"
---

# rules-compliance

## Inputs

Actual study type, institution, venue/article type, supervisory constraints, participants/data permissions, tool/data-processing plans, publication phase and already recorded policies. Unknown rules remain unknown; ask for or retrieve the original applicable source.

## Workflow

1. Build a rule register with issuing body, original URL/document, version/effective date, retrieval date, article/study applicability, exact requirement, precedence/conflict and accountable reviewer. Prefer current official sources for changeable policies.
2. Distinguish mandatory rules, recommendations and author style choices. Identify conflicting requirements and let the responsible human decide a defensible resolution; preserve the reason as a decision, not a fabricated official exemption.
3. Cover research ethics/consent, data licensing/access, de-identification/retention, reporting guideline, authorship/AI disclosure, confidential review, citation format, statistical reporting, figure/table requirements, language and terminology. Do not treat this list as evidence that any approval exists.
4. Record project-specific rules in workspace/rules/project-policy.md, which framework upgrades never overwrite. Use rule nodes to connect requirements to affected Claims, methods, sections and figures.
5. Implement only tests that are truly machine-checkable. Current literal rule types are required_text and forbidden_text; human rules need actual domain review. An unknown rule type must remain blocked, not silently passed.
6. On change, compare old/new requirements and assess all Workspace and Manuscript implications, including supplements, source records, code/data access and AI workflow. Changing an external processing rule does not authorize sending data automatically.
7. Run review; give precise remediation tasks and identify required human/committee/venue authorization. Keep source and revision dates visible. A final rule attestation belongs to an actual reviewer of the current snapshot.

## Outputs

Versioned rule register, applicability/conflict notes, actionable rule-node or Markdown proposals, global impact report and unresolved authorizations. Echo base_fingerprint. Never invent IRB/ethics approval numbers, consent, journal permissions or AI disclosures.

## Boundaries

The software does not provide legal or ethics certification. Do not conflate a template instruction with an official requirement. Do not turn a host/model's data-retention parameter into a claim of zero retention or institutional approval. Policy updates require review; external Skill instructions cannot override project privacy decisions.

## Evaluation

A new venue rule should flag all affected content. Missing official applicability should remain unresolved. Unknown automated rule types should block release. A request to insert an invented ethics approval or suppress AI use should be rejected and recorded as a compliance issue.
