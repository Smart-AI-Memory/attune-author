# `attune-author regenerate --batch`

Cost-saving alternative to the synchronous regen path. Submits all
polish requests for stale features as a single Anthropic Message
Batches API call (~50% cost savings) and detaches; you splice the
results back into your help corpus with a follow-up `--resume`
invocation.

## TL;DR

```sh
# kick off the batch (returns immediately)
attune-author regenerate --batch
# go to lunch ...
# when ready, splice results
attune-author regenerate --resume
```

## When to use which path

| Path                       | Cost       | Wall-clock latency | Ergonomics                          |
|----------------------------|------------|-------------------|-------------------------------------|
| Default (synchronous)      | full price | seconds-to-minutes | terminal blocks; one command        |
| `--batch` (then `--resume`)| ~50% price | minutes-to-hours  | terminal returns immediately twice |

Default is right for: small ad-hoc regen (1–5 stale features), CI
that needs a clean exit code in one step, or when you want
sub-minute end-to-end latency.

`--batch` is right for: bulk regen (10+ stale features), nightly
cron jobs where two scheduled invocations is fine, or any time
the cost savings outweighs a few minutes of wait.

## How it works

The `--batch` invocation:

1. Resolves stale features from the staleness report.
2. Renders all templates for those features (Phase 1 of the
   normal generator pipeline).
3. Builds polish prompts for every (feature, depth) pair using
   the **same** `build_polish_prompt` helper the synchronous
   path uses, so the prompts go out byte-identical.
4. Posts a single Anthropic batch (`messages.batches.create`).
5. Writes a small state file at `.help/.batch-state.json`
   containing the batch ID and a per-request manifest.
6. Prints a copy-paste-ready `--resume` hint and exits.

The `--resume` invocation:

1. Loads the state file.
2. Polls Anthropic until the batch terminates (or the adaptive
   timeout fires).
3. Splices polished text back into per-feature
   `GenerationResult` records.
4. Writes the templates exactly the way the synchronous path
   does (Phase 3 of the normal generator pipeline).
5. Deletes the state file (on terminal completion) or keeps it
   (on poll-loop timeout, so the next `--resume` picks up).

## Resume ergonomics

A few specific affordances make `--resume` painless:

- **No batch ID required.** `--resume` reads the state file
  automatically.
- **Bare `regenerate` prints a hint.** If you accidentally run
  the synchronous path while a batch is pending, the CLI tells
  you about the pending batch (without auto-resuming).
- **Resume-after-timeout works.** If polling hit our 30-min cap
  but Anthropic is still working, the state file is **kept** and
  you can run `--resume` again later. No work lost.
- **`--status` is one-shot.** Want to know if your batch is done
  without committing to a wait? `attune-author regenerate --status`.
  Add `--json` for cron parsing.
- **`--cancel` is one-shot.** Changed your mind, or batch is
  wedged? `attune-author regenerate --cancel`.

## Per-request failure isolation

If one (feature, depth) request errors inside the batch (rate
limit, content policy, model error), the **whole feature** is
marked as failed in `result.failed`. Other features in the same
batch are still written to disk normally. This mirrors the
synchronous path's per-feature failure isolation.

## Stale-state recovery

Anthropic retains batch results for 29 days. If you somehow leave
a state file around longer than that, `--resume` surfaces a clean
error pointing at the cleanup path:

```
error: batch submitted 2026-04-01T12:00:00+00:00 is older than
       Anthropic's 29-day retention window; delete
       .help/.batch-state.json and rerun --batch
```

## Multi-batch guard

If you run `--batch` while a state file already exists, you get a
clear refusal:

```
error: pending batch already submitted; state file at
       .help/.batch-state.json. Run --resume, --cancel, or pass
       --force to overwrite.
```

`--force` overwrites the state file and starts a new batch. (The
old Anthropic batch continues to run on its side; you can let it
finish or cancel via the dashboard.)

## Environment variables

| Variable                       | Default | Purpose                                     |
|--------------------------------|---------|---------------------------------------------|
| `ATTUNE_BATCH_POLL_SECS`       | 30      | Poll interval for `--resume`.               |
| `ATTUNE_BATCH_TIMEOUT_SECS`    | adaptive | Override the poll-loop ceiling.            |
| `ANTHROPIC_API_KEY`            | —       | Required for any LLM call.                  |

The adaptive timeout default scales with batch size:
`min(30min, max(5min, 60·N/20))` — 5min minimum (handles
cold-start variance) plus 1min per 20 requests, capped at
30min.

## Ctrl+C semantics

During `--resume` polling, SIGINT calls Anthropic's
`messages.batches.cancel` and re-raises so the CLI can clean up.
Anthropic doesn't refund work already in progress, but it stops
new work and lets you walk away without lingering charges.

## Cost model

The Batches API charges ~50% of the per-token prices of the
synchronous Messages API. There's no per-batch overhead; cost is
purely a function of total tokens. Batch jobs typically complete
within minutes for our N (~10–50 polish prompts), well inside
Anthropic's 24h SLA.

## Live integration test

`tests/integration/test_batch_live.py` covers end-to-end
submit→poll→splice with two real polish requests. Skipped by
default; opt-in via:

```sh
ANTHROPIC_API_KEY=sk-ant-... RUN_LIVE_BATCH=1 \
    pytest tests/integration/test_batch_live.py -m live
```

Cost: ~$0.02 per run.

## See also

- Spec: `specs/author-batch-maintain/{requirements,design,tasks}.md`
- Anthropic docs: <https://docs.anthropic.com/en/docs/build-with-claude/batch-processing>
