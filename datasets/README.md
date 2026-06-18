# Datasets

Datasets for **Scientific Idea Generation with Grounded Novelty**. Data files are
**not committed to git** (see `datasets/.gitignore`). Follow the download/loading
instructions below. Each dataset is mapped to the grounding mechanism(s) it supports.

| # | Dataset | Where | Size | Task | Grounding link |
|---|---------|-------|------|------|----------------|
| 1 | HypoGen (DR1) | HF `UniverseTBD/hypogen-dr1` → `datasets/hypogen/data` | 5,478 train / 50 test | Hypothesis generation (Bit→Flip→Spark) | **deduction** (assumption→counterproposal), proposal_writing |
| 2 | Si et al. ideation human study | `code/AI-Researcher/reviews_ideation/data_points_all_anonymized.json` | 100+ ideas, blind reviews | Novelty/feasibility scoring reference | gold eval for **all** mechanisms |
| 3 | MOOSE social-science hypotheses | `code/MOOSE/Data/*.xlsx` | corpus + summaries | Open-domain hypothesis induction | **induction**, small_experiments (feedback) |
| 4 | SciMON / CLBD | `code/SciMON-clbd/data/*.zip` | ~170 MB unzipped | Literature-based idea generation | **literature_comparison** |

---

## Dataset 1: HypoGen (DR1)  ✅ downloaded

### Overview
- **Source**: HuggingFace `UniverseTBD/hypogen-dr1` (paper: *Sparks of Science*, arXiv 2504.12976)
- **Size**: 5,478 train + 50 test structured problem→hypothesis pairs from top CS conferences
- **Format**: HuggingFace `DatasetDict`, saved to `datasets/hypogen/data`
- **Columns**: `paper_id, title, authors, venue, year, citation, abstract, bit, flip, spark, chain_of_reasoning, url, pdf_url`
- **Schema**: **Bit** = conventional assumption · **Flip** = counterproposal · **Spark** = key insight · **chain_of_reasoning** = explicit Bit→Flip reasoning trace.
- **Why relevant**: The Bit-Flip-Spark + Chain-of-Reasoning structure is a direct operationalization of **grounding novelty through deduction** (deriving a counterproposal from a stated assumption). Ideal for the "deduction / proposal writing" arm of the hypothesis.

### Download
```python
from datasets import load_dataset
ds = load_dataset("UniverseTBD/hypogen-dr1")
ds.save_to_disk("datasets/hypogen/data")
```

### Load
```python
from datasets import load_from_disk
ds = load_from_disk("datasets/hypogen/data")   # ds['train'], ds['test']
```
Sample records: `datasets/hypogen/samples.json` (5 examples, committed).

---

## Dataset 2: Si et al. ideation human study  ✅ available locally (in code/)

### Overview
- **Source**: bundled in `code/AI-Researcher/reviews_ideation/data_points_all_anonymized.json` (paper arXiv 2409.04109)
- **Content**: ideas (LLM agent vs human experts) across NLP topics with **blind expert review scores** (novelty, feasibility, excitement, effectiveness, overall) — the gold standard for grounded-novelty evaluation.
- **Why relevant**: Provides a **calibrated human reference** to validate any automated novelty metric and to define the 7 topics used as ideation prompts. The single most important evaluation anchor for this project.
- **Companion**: `code/AI-Researcher/reviews_ideation/id_title_mapping.csv`, `stats_*.py`.

### Load
```python
import json
data = json.load(open("code/AI-Researcher/reviews_ideation/data_points_all_anonymized.json"))
```

---

## Dataset 3: MOOSE social-science hypotheses  ✅ available locally (in code/)

### Overview
- **Source**: bundled in `code/MOOSE/Data/` (paper arXiv 2309.02726)
- **Files**: `business_research.xlsx` (raw corpus), `summary*.xlsx` (background + gold hypotheses), `raw_corpus_trial.xlsx`, `Surveys/`.
- **Task**: open-domain hypothetical **induction** — from raw web/social-science corpus to novel, valid hypotheses, refined by present/past/future feedback.
- **Why relevant**: Directly supports the **induction** and **small-experiments/feedback** arms; ships expert + GPT-4 evaluation protocols.

### Load
```python
import pandas as pd   # pip/uv add openpyxl
df = pd.read_excel("code/MOOSE/Data/summary_to_read_with_pandas.xlsx")
```

---

## Dataset 4: SciMON / CLBD literature-based discovery  ✅ available locally (in code/)

### Overview
- **Source**: bundled zips in `code/SciMON-clbd/data/` (paper arXiv 2305.14259)
- **Files**: `local_context_dataset.zip` (train/val/test for the ideation task), `kg.zip` (IE results per abstract), `ct.zip` (citation network), `gold_subset.zip` (gold annotations), `biomedical.zip`, `e2t.zip`.
- **Task**: generate natural-language scientific ideas grounded in literature, with iterative novelty optimization vs prior papers.
- **Why relevant**: The reference dataset for the **literature_comparison** arm of the hypothesis.

### Unzip
```bash
cd code/SciMON-clbd/data && for z in *.zip; do unzip -o "$z"; done && cd -
```

---

## Other datasets (referenced, fetch if needed)
- **IdeaBench** (arXiv 2411.02429): titles+abstracts of influential papers + references; two-stage GPT-4o "Insight Score" eval. Distributed via the paper's repo/HF — search `IdeaBench` on HuggingFace before use.
- **RQ-Bench** (arXiv 2606.12071): author-anchored research questions from recent arXiv papers; for studying the LLM-judge "novelty mirage". Reconstructable from arXiv per the paper.
- **OpenReview / ICLR submissions**: many works (CoI Idea Arena, Deep-Ideation critic) train/evaluate against OpenReview review text — pull via the `openreview-py` API if a learned critic is needed.

## Notes
- `uv add openpyxl` is needed to read the MOOSE `.xlsx` files with pandas.
- HypoGen is the only dataset pre-downloaded (small). Items 2–4 are already on disk inside `code/` (cloned repos), so no extra download is required for them.
