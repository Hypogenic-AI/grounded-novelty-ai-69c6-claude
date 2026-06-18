# Scientific Idea Generation with Grounded Novelty

First **controlled head-to-head ablation** of six "grounding" mechanisms for LLM scientific
ideation (deduction · induction · proposal writing · outcome imagination · small experiments ·
literature comparison) against an unguided control — same backbone (`gpt-4.1`), same 7 NLP topics
(Si et al. 2024), same output schema, **245 ideas**, evaluated three independent ways.

## Key findings
- **Grounding does not uniformly help.** No mechanism beats the unguided control on holistic
  *overall* quality; `small_experiment` is significantly worse.
- **It steers a novelty–feasibility trade-off.** Deduction / literature-comparison / outcome-
  imagination ↑ *judged novelty* but ↓ feasibility; induction / proposal-writing / small-experiment
  ↑ feasibility but ↓ novelty (small-experiment even rediscovers known methods like
  Chain-of-Verification).
- **Literature comparison is the standout:** wins 79% of pairwise comparisons vs unguided
  (CI [0.71, 0.87]) and is the only mechanism that increases idea-set diversity.
- **The "novelty mirage", measured.** An *objective* literature-distance novelty metric shows **no**
  grounding gain (proposal-writing even lowers it), and LLM-judged novelty is **uncorrelated** with
  it (Spearman ρ = 0.01, p = 0.85). Apparent novelty gains live in the judge's eye, not in distance
  from real prior work.
- All effects are **robust to a length covariate** and reproduce exactly from cache.

See **[REPORT.md](REPORT.md)** for full methodology, tables, statistics, and discussion.

## Reproduce
```bash
source .venv/bin/activate          # uv-managed env (see pyproject.toml)
python src/run_all.py              # full run: 245 ideas (≈25 min, ≈$3-4 API; free on re-run via cache)
python src/run_all.py --n 1        # quick 49-idea pilot
```
Requires env vars `OPENAI_API_KEY`, `OPENROUTER_KEY`, `S2_API_KEY` (all read from environment).

## File structure
```
planning.md                 Phase-0 motivation/novelty + full experimental plan
REPORT.md                   Primary deliverable: methods, results, analysis, limitations
src/
  config.py                 Models, topics, conditions, paths, sample sizes
  llm.py                    Cached + retrying LLM client, cost tracking
  conditions.py             The 7 grounding scaffolds (identical output schema)
  corpus.py                 Semantic Scholar prior-work corpus (objective metric + lit-comparison)
  generate.py               7×7×N idea generation (deterministic seeds)
  metrics.py                Objective novelty (LGN) + set-level diversity (GPU embeddings)
  judge.py                  2-judge off-family rubric + pairwise vs control
  analyze.py                Mixed-effects stats, effect sizes, Holm, judge validation, figures
  run_all.py                One-command reproduction
results/                    ideas.jsonl, judge_scores.jsonl, pairwise.jsonl, analysis_summary.json,
                            per_idea_table.csv, objective_metrics.json, qualitative_examples.json
figures/                    fig1_lgn … fig6_convergent (.png)
```

## Method in one paragraph
Every condition receives the identical topic seed and emits the identical idea JSON; only the
*reasoning scaffold* differs, isolating grounding from length/format confounds. Ideas are scored by
(1) an objective embedding metric — distance to 150 real prior-work abstracts/topic from Semantic
Scholar — (2) a 2-judge off-family LLM rubric (Claude-Sonnet-4.5 + Gemini-2.5-Flash), and (3)
position-controlled pairwise comparisons. Statistics use linear mixed-effects models with topic as a
random intercept, Cohen's d effect sizes, and Holm correction; the judge is validated via inter-judge
agreement and convergent validity against the objective metric.
