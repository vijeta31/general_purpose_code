---
description: Plan and build a parallel LLM-based failure analysis over the evaluation run of the ticket-recommendation pipeline.
---

# Goal
Analyze the evaluation run of ~1150 tickets to find WHERE and WHY the pipeline fails,
and produce a ranked list of failure causes with examples and suggested fixes.

# Inputs
- Eval dataset: JSONL, one ticket per line: ticket_id, text, product, relevant (doc_id → grade 0/1/2).
- Pipeline run output: JSONL per ticket: top-20 candidates with scores, final top-3,
  selection LLM's reasons (if logged).
- Document store: doc_id → title, summary (or truncated body).
Ask me for exact file paths and field names before planning. Do not assume them.

# Phase 1 — Deterministic triage (no LLM)
For every ticket compute:
- gold_rank: best rank of any relevant doc in the top-20 (null if absent).
- outcome: SUCCESS (relevant doc in final top-3), RANKING_MISS (relevant in top-20
  but not top-3), RETRIEVAL_MISS (no relevant doc in top-20), NO_GOLD (no labeled doc).
Output a summary table of outcomes overall and per product.
Only non-SUCCESS tickets go to Phase 2, plus a random 5% sample of SUCCESS tickets
as a sanity check.

# Phase 2 — Open coding pilot (run before the full taxonomy)
Run the judge on a random 40 failed tickets with an open-ended question:
"Describe in 1–2 sentences the most likely reason the correct document was not
recommended." Cluster the answers and propose a failure taxonomy. STOP and show me
the taxonomy for approval before Phase 3.

# Phase 3 — Parallel LLM judging
Starting taxonomy (refine with Phase 2 results):
- vocabulary_mismatch: ticket and doc describe the same issue in different words.
- intent_misread: the ticket's actual problem differs from its surface wording.
- wrong_product_or_version: retrieved docs are for another product/version.
- multi_issue_ticket: ticket contains several problems; only one was addressed.
- selection_error: a better doc was in the top-20 but the LLM chose worse ones.
- near_duplicates: top-3 wasted slots on near-identical docs.
- outdated_doc: recommended or gold doc is stale.
- kb_gap: no document in the KB actually solves this ticket.
- label_error: the recommended doc is actually correct; the ground-truth label is
  wrong or incomplete.
- ambiguous_ticket: not enough information to determine the right doc.

Judge input per ticket: ticket text, product, gold docs (title + summary), final top-3
(title + summary + selection reasons), gold_rank, outcome.
Judge output: strict JSON validated with Pydantic:
{ "ticket_id", "primary_cause", "secondary_cause" (nullable),
  "top3_relevance": {doc_id: 0|1|2}, "evidence" (≤2 sentences quoting the ticket/docs),
  "suggested_fix" (≤1 sentence), "confidence": "low"|"medium"|"high" }

Execution requirements:
- Python asyncio with a semaphore (configurable concurrency, default 10).
- Retries with exponential backoff and jitter on rate-limit/timeout errors.
- Resumable: append each result to results.jsonl as it completes; on restart,
  skip ticket_ids already present.
- Invalid JSON: retry once with the validation error in the prompt, then log to
  errors.jsonl.
- Temperature 0. Use a different model from the pipeline's selection LLM to
  reduce self-preference bias.
- Track tokens and cost; print a cost estimate from a 10-ticket dry run before
  the full run and wait for my confirmation.
- If the provider offers a batch API, offer it as an option (cheaper, not latency
  sensitive).

# Phase 4 — Aggregation and report
Generate reports/failure_analysis.md with:
- Outcome breakdown (Phase 1) overall and per product.
- Primary cause counts and percentages, cross-tabbed with outcome and product.
- 3 representative examples per cause (ticket excerpt, what was recommended,
  what should have been).
- Tickets flagged label_error, as a list for label correction.
- Ranked recommendations: which causes to fix first, by ticket count and
  estimated fixability, mapped to pipeline stages (query understanding, retrieval,
  reranking, selection, confidence gate, KB content).

# Phase 5 — Calibration
Export 50 random judgments to a CSV for human review (columns: ticket_id,
primary_cause, evidence, human_agrees, human_cause). Compute agreement once filled.
If agreement is below ~80%, refine the judge prompt and taxonomy before trusting
the aggregates.

# Constraints
- Tickets are already cleaned; documents are indexed whole (no chunking).
- Don't modify the production pipeline; this is a standalone analysis tool under
  tools/eval_analysis/.
- Keep prompts in separate files so they can be versioned and edited.
