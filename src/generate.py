"""Phase 2/4: generate the 7x7xN idea grid (the core ablation).

Every condition uses the SAME backbone (gpt-4.1) and emits the SAME idea schema;
only the grounding scaffold differs. Runs are cached and parallelized.
"""
import argparse
import hashlib
import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from conditions import build_messages
from config import (CONDITIONS, GEN_MAX_TOKENS, GEN_MODEL, GEN_PROVIDER,
                    GEN_TEMPERATURE, GEN_TOP_P, IDEAS_FILE, N_IDEAS_PER_CELL,
                    SEED, TOPICS)
from corpus import build_corpus, prior_work_snippets
from llm import chat, extract_json, usage_summary

REQUIRED_KEYS = ["title", "problem", "motivation", "method", "experiment_plan"]


def idea_text(idea):
    """Flatten the idea dict into the single string the metrics operate on."""
    return " ".join(str(idea.get(k, "")).strip() for k in REQUIRED_KEYS)


def generate_one(condition, topic, rep, corpus):
    topic_desc = TOPICS[topic]
    prior = None
    if condition == "literature_comparison":
        prior = prior_work_snippets(corpus, topic, k=8)
    messages = build_messages(condition, topic_desc, prior_work=prior)
    # Deterministic per-cell seed (stable hash, not builtin hash() which is
    # randomized per process) so each replicate is distinct AND reproducible.
    stable = int(hashlib.sha256((condition + topic).encode()).hexdigest()[:8], 16)
    seed = SEED + rep * 1000 + stable % 997
    raw = chat(messages, model=GEN_MODEL, provider=GEN_PROVIDER,
               temperature=GEN_TEMPERATURE, top_p=GEN_TOP_P,
               max_tokens=GEN_MAX_TOKENS, seed=seed)
    try:
        idea = extract_json(raw)
        idea = {k: idea.get(k, "") for k in REQUIRED_KEYS}
        ok = all(idea[k] for k in REQUIRED_KEYS)
    except Exception:
        idea, ok = {k: "" for k in REQUIRED_KEYS}, False
    text = idea_text(idea)
    return {
        "id": f"{topic}__{condition}__{rep}",
        "topic": topic, "condition": condition, "rep": rep,
        "idea": idea, "text": text, "n_words": len(text.split()),
        "parse_ok": ok, "raw": raw,
    }


def main(n_per_cell=N_IDEAS_PER_CELL, workers=12):
    random.seed(SEED)
    corpus = build_corpus()
    jobs = [(c, t, r) for t in TOPICS for c in CONDITIONS for r in range(n_per_cell)]
    print(f"Generating {len(jobs)} ideas "
          f"({len(CONDITIONS)} conditions x {len(TOPICS)} topics x {n_per_cell})")
    results = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(generate_one, c, t, r, corpus): (c, t, r)
                for (c, t, r) in jobs}
        for i, fut in enumerate(as_completed(futs), 1):
            results.append(fut.result())
            if i % 25 == 0:
                print(f"  {i}/{len(jobs)} done")
    results.sort(key=lambda x: x["id"])
    with open(IDEAS_FILE, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    n_bad = sum(1 for r in results if not r["parse_ok"])
    print(f"Saved {len(results)} ideas to {IDEAS_FILE} ({n_bad} parse failures)")
    print("Usage:", usage_summary())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=N_IDEAS_PER_CELL)
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    main(args.n, args.workers)
