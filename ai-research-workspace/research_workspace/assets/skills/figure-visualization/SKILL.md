---
name: figure-visualization
description: Design, generate or audit research figures, tables, framework diagrams, mechanisms and graphical abstracts. Use when data, Claims, figure purpose or publication requirements change.
compatibility: Authorized plotting/diagram tools chosen per task. Preserve data, code and generation provenance.
metadata:
  version: "0.1.0"
---

# figure-visualization

## Inputs

The exact question each figure answers, related Claim IDs, original data/evidence and result provenance, units/sample structure, audience, output medium, journal requirements and authorized tools. Read Idea Evaluation's expected-figure list and evaluation plan.

## Workflow

1. State the figure's purpose before choosing aesthetics. Separate quantitative results from conceptual diagrams, workflow schematics and hypotheses. Decide what a reader should legitimately infer and what cannot be inferred.
2. Discover appropriate available tools or reviewed external Skills. Compare reproducibility, editable output, accessibility, journal format, dependencies, costs and private-data handling. Do not force a paid generator or an image into every paper.
3. For quantitative figures, use actual data and inspectable transformations/code. Record aggregation, normalization, filtering, missingness, exclusions, uncertainty definition and units. Preserve raw observations where useful. Use fresh run outputs and hashes.
4. Choose truthful visual encodings: comparable scales, correctly mapped area/position, explicit baselines or axis breaks, uncertainty and sample information, visible missing values. Do not remove inconvenient observations or generate quantitative evidence with image models.
5. For schematics/mechanisms, distinguish established relationships from hypotheses and illustrative simplifications. Link each scientific relation to evidence/Claims. A generated concept illustration is not an experimental image.
6. Inspect the actual output at intended size. Check labels, fonts, symbols, overlap, color redundancy, contrast, legends, alt text, panel references, precision, uncertainty and caption. Verify current official journal requirements for the actual phase and figure type; never infer them from memory.
7. Register the figure/table node with path, sha256, claims, caption, purpose and alt_text; depend on Claim and real result/evidence. Keep the source data, code and regeneration instructions. Ensure the manuscript's interpretation matches what the figure actually shows.
8. Submit figure metadata and manuscript/caption changes for approval, run impact analysis, sync and independent review. Cosmetic and scientific edits must remain distinguishable.

## Outputs

Figure specification, tool choice rationale, reproducible generation plan or actual run provenance, output inspection findings, tracked Figure–Data/Evidence–Claim links, caption and alt text. Ordinary proposals cannot masquerade as executed code or new experimental results.

## Boundaries

Do not fabricate or selectively enhance scientific data/images. Do not claim automated formatting proves accessibility or venue compliance. The local runner is not a sandbox. Do not install or execute downloaded plotting scripts without review and explicit permission.

## Evaluation

Reject a chart request that hides unfavorable observations. A changed data file must invalidate prior figure provenance. A mechanism diagram must label speculative arrows. A figure that is polished but does not support the linked Claim must return a substantive issue.
