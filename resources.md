# Resources Catalog — Scientific Idea Generation with Grounded Novelty

## Summary
Resources gathered for the hypothesis that LLMs generate higher-quality scientific ideas when
novelty is **grounded** (deduction · induction · proposal writing · outcome imagination · small
experiments · literature comparison) vs unguided generation.

- **Papers downloaded**: 18 (PDFs in `papers/`, git-ignored; manifest `papers/_arxiv_manifest.json`)
- **Datasets**: 4 ready locally (1 downloaded from HF, 3 bundled in cloned repos) + 3 referenced
- **Code repositories**: 8 cloned (`code/`, git-ignored; re-clone via `code/README.md`)
- **Synthesis**: `literature_review.md` · structured per-paper notes: `.neurico/paper_notes.json`

---

## Papers (18)
Ranked by citations. Full descriptions: `papers/README.md`. Per-mechanism analysis: `literature_review.md` §3.

| Title | Year | Cites | File | arXiv |
|-------|------|------|------|-------|
| Can LLMs Generate Novel Research Ideas? (Si et al.) | 2024 | 371 | `2409.04109_*.pdf` | 2409.04109 |
| SciMON: Scientific Inspiration Machines Optimized for Novelty | 2023 | 181 | `2305.14259_*.pdf` | 2305.14259 |
| LLMs for Automated Open-domain Scientific Hypotheses Discovery (MOOSE) | 2023 | 115 | `2309.02726_*.pdf` | 2309.02726 |
| Chain of Ideas | 2024 | 90 | `2410.13185_*.pdf` | 2410.13185 |
| Many Heads Are Better Than One (VirSci) | 2024 | 64 | `2410.09403_*.pdf` | 2410.09403 |
| Nova: Iterative Planning and Search | 2024 | 54 | `2410.14255_*.pdf` | 2410.14255 |
| Automating psychological hypothesis generation (causal graph) | 2024 | 46 | `2402.14424_*.pdf` | 2402.14424 |
| Can LLMs Unlock Novel Scientific Research Ideas? (IAScore) | 2024 | 27 | `2409.06185_*.pdf` | 2409.06185 |
| Learning to Generate Research Idea with Dynamic Control | 2024 | 20 | `2412.14626_*.pdf` | 2412.14626 |
| AutoDiscovery: Bayesian Surprise | 2025 | 19 | `2507.00310_*.pdf` | 2507.00310 |
| All That Glitters is Not Novel (plagiarism) | 2025 | 19 | `2502.16487_*.pdf` | 2502.16487 |
| Sparks of Science (HypoGen) | 2025 | 18 | `2504.12976_*.pdf` | 2504.12976 |
| A Survey on Hypothesis Generation (LLM era) | 2025 | 13 | `2504.05496_*.pdf` | 2504.05496 |
| IdeaBench | 2024 | 6 | `2411.02429_*.pdf` | 2411.02429 |
| HypoSpace (set-valued hypotheses) | 2025 | 6 | `2510.15614_*.pdf` | 2510.15614 |
| LLMs for Scientific Idea Generation: Creativity-Centered Survey | 2025 | 5 | `2511.07448_*.pdf` | 2511.07448 |
| Deep Ideation (concept network + critic) | 2025 | 4 | `2511.02238_*.pdf` | 2511.02238 |
| On the Limits of LLM-as-Judge for Novelty (RQ-Bench) | 2026 | 0 | `2606.12071_*.pdf` | 2606.12071 |

---

## Datasets
Details + download/load instructions: `datasets/README.md`.

| Name | Source | Size | Task | Location | Grounding |
|------|--------|------|------|----------|-----------|
| HypoGen (DR1) | HF `UniverseTBD/hypogen-dr1` | 5,478 / 50 | Bit→Flip→Spark hypothesis gen | `datasets/hypogen/data` ✅ | deduction |
| Si et al. ideas+reviews | `AI-Researcher` repo | 49×3 ideas, 298 reviews | Novelty/feasibility gold scores | `code/AI-Researcher/reviews_ideation/*.json` ✅ | eval anchor |
| MOOSE / TOMATO | `MOOSE` repo | 50 papers, 7 disciplines | Open-domain induction | `code/MOOSE/Data/*.xlsx` ✅ | induction |
| SciMON / CLBD | `SciMON-clbd` repo | ~170 MB | Literature-based idea gen | `code/SciMON-clbd/data/*.zip` ✅ | literature_comparison |
| IdeaBench / S2ORC / DiscoveryBench / RQ-Bench | various | — | benchmarks/metrics | referenced | mixed |

---

## Code Repositories (8)
Details + grounding mapping + re-clone commands: `code/README.md`.

| Name | URL | Purpose | Location | Grounding |
|------|-----|---------|----------|-----------|
| AI-Researcher | github.com/NoviScl/AI-Researcher | Si et al. baseline agent + human scores | `code/AI-Researcher/` | lit-comparison, proposal |
| SciMON-clbd | github.com/eaglew/clbd | Iterative novelty vs literature | `code/SciMON-clbd/` | literature_comparison |
| MOOSE | github.com/ZonglinY/MOOSE | Inductive hypothesis + feedback | `code/MOOSE/` | induction, small-exp |
| CoI-Agent | github.com/DAMO-NLP-SG/CoI-Agent | Chain-of-Ideas + Idea Arena | `code/CoI-Agent/` | literature_comparison |
| Virtual-Scientists | github.com/open-sciencelab/Virtual-Scientists | Multi-agent ideation | `code/Virtual-Scientists/` | proposal, multi-agent |
| AutoDiscovery | github.com/allenai/autodiscovery | Bayesian-surprise MCTS | `code/AutoDiscovery/` | outcome-imag, small-exp |
| Future-Idea-Generation | github.com/sandeep82945/Future-Idea-Generation | IAScore / Distinctness metrics | `code/Future-Idea-Generation/` | lit-comparison (metrics) |
| Deep-Ideation | github.com/kyZhao-1/Deep-Ideation | Concept network + learned critic | `code/Deep-Ideation/` | lit-comparison, small-exp |

---

## Resource Gathering Notes

### Search strategy
Used the paper-finder service (`localhost:8000`) in **diligent** mode with three complementary
queries: (1) grounding novelty in LLM idea/hypothesis generation; (2) literature-based hypothesis
generation via induction/deduction/feedback; (3) benchmarks & datasets for evaluating idea-gen
novelty. 150+ hits, 49 at relevance 3; selected 18 highest-signal papers spanning all six grounding
mechanisms + evaluation/critique papers. PDFs resolved to arXiv and downloaded via `requests`.
Per-paper structured notes were extracted by a parallel reading workflow (18 agents, deep reads on
the 3 foundational papers).

### Selection criteria
One+ strong representative per grounding mechanism; the foundational human study (Si et al.) and its
released data; the standard benchmarks (IdeaBench, HypoGen) and metrics (IAScore, Insight Score,
HypoSpace VR/NR); and two critical "evaluation skepticism" papers (plagiarism; LLM-judge mirage).

### Challenges & workarounds
- Paper-finder needed `httpx` (installed); the first background run's stdout capture truncated, so
  searches were re-run with file redirection (cache made this fast).
- `arxiv==4.0.0` lacks `download_pdf`; resolved IDs via the API and downloaded PDFs with `requests`.
- A few titles fuzzy-matched the wrong arXiv entry (e.g., an astronomy "Nova"); fixed with
  tighter per-paper queries. Scideator (workshop) and the SciMON journal extension are not on arXiv;
  Scideator is covered via its abstract, the extension via SciMON itself (same authors/data).

### Gaps
- No single dataset compares all six grounding mechanisms under one protocol — this is the
  experiment's opportunity (build the comparison from the local datasets + a fixed topic set).
- Deep-Ideation's repo was mostly a README at clone time (code release may be pending).

---

## Recommendations for Experiment Design
(see `literature_review.md` §6 for the full design)

1. **Primary datasets**: HypoGen (deduction, ready), MOOSE/TOMATO (induction), Si et al. ideas
   (eval anchor + 7-topic prompts), SciMON/CLBD (literature comparison) — all already on disk.
2. **Baselines**: vanilla/unguided prompting (the hypothesis control) + Si et al. RAG agent +
   Chain-of-Ideas + SciMON.
3. **Metrics**: 1–10 novelty/feasibility/effectiveness rubric **plus** a literature-grounded
   reference metric (IAScore / Insight Score / embedding distance) **plus** set-level diversity
   (HypoSpace VR/NR). Use **comparative** judging and **validate the LLM judge against Si et al.
   human scores** (RQ-Bench warns of the novelty mirage; report agreement).
4. **Code to reuse**: SciMON, MOOSE, AI-Researcher agent, Future-Idea metrics, AutoDiscovery — read
   their prompts/metrics directly; do not co-install conflicting dependencies into the workspace venv.
