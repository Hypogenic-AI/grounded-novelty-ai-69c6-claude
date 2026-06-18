"""Objective, judge-free metrics computed from sentence embeddings (on GPU).

- Literature-Grounded Novelty (LGN): 1 - max cosine similarity of an idea to the
  nearest REAL prior-work abstract for its topic (All-That-Glitters recommendation).
- Set-level diversity: mean pairwise cosine DISTANCE among ideas in a cell.
- Dedup rate: fraction of near-duplicate idea pairs at cosine >= 0.8 (Si threshold).
"""
import json

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from config import (CONDITIONS, CORPUS_FILE, EMBED_MODEL, IDEAS_FILE, LGN_FILE,
                    TOPICS)

DUP_THRESHOLD = 0.8


def load_ideas():
    return [json.loads(l) for l in open(IDEAS_FILE)]


def embed(texts, model):
    return model.encode(texts, batch_size=64, convert_to_numpy=True,
                        normalize_embeddings=True, show_progress_bar=False)


def compute():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Embedding on {device}")
    model = SentenceTransformer(EMBED_MODEL, device=device)

    ideas = load_ideas()
    corpus = json.load(open(CORPUS_FILE))

    # Pre-embed each topic's prior-work corpus once.
    topic_corpus_emb = {}
    for topic in TOPICS:
        abstracts = [p["title"] + ". " + p["abstract"] for p in corpus[topic]]
        topic_corpus_emb[topic] = embed(abstracts, model)

    # Embed all ideas.
    idea_emb = embed([r["text"] for r in ideas], model)
    for r, e in zip(ideas, idea_emb):
        r["_emb"] = e

    # --- LGN per idea: distance to nearest prior-work abstract (same topic) ---
    for r in ideas:
        C = topic_corpus_emb[r["topic"]]
        sims = C @ r["_emb"]            # cosine (vectors normalized)
        r["lgn"] = float(1.0 - sims.max())
        r["lgn_top5"] = float(1.0 - np.sort(sims)[-5:].mean())

    # --- Set-level diversity + dedup within each (condition, topic) cell ---
    cell_diversity = {}
    cond_emb = {c: [] for c in CONDITIONS}
    for topic in TOPICS:
        for cond in CONDITIONS:
            E = np.array([r["_emb"] for r in ideas
                          if r["topic"] == topic and r["condition"] == cond])
            cond_emb[cond].append(E)
            if len(E) < 2:
                continue
            sim = E @ E.T
            iu = np.triu_indices(len(E), k=1)
            pair_sims = sim[iu]
            cell_diversity[f"{topic}__{cond}"] = {
                "mean_pairwise_distance": float(1.0 - pair_sims.mean()),
                "dup_rate": float((pair_sims >= DUP_THRESHOLD).mean()),
            }

    # --- Per-condition aggregate diversity (across that condition's whole set) ---
    cond_diversity = {}
    for cond in CONDITIONS:
        E = np.vstack([e for e in cond_emb[cond] if len(e)])
        sim = E @ E.T
        iu = np.triu_indices(len(E), k=1)
        ps = sim[iu]
        cond_diversity[cond] = {
            "mean_pairwise_distance": float(1.0 - ps.mean()),
            "dup_rate": float((ps >= DUP_THRESHOLD).mean()),
            "n": int(len(E)),
        }

    # Strip embeddings before saving the per-idea records.
    per_idea = [{k: v for k, v in r.items() if k != "_emb"} for r in ideas]
    out = {
        "per_idea": per_idea,
        "cell_diversity": cell_diversity,
        "cond_diversity": cond_diversity,
        "embed_model": EMBED_MODEL,
        "dup_threshold": DUP_THRESHOLD,
    }
    with open(LGN_FILE, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Saved objective metrics to {LGN_FILE}")

    # Quick console summary
    import statistics
    print("\nMean LGN by condition (higher = more novel vs prior work):")
    for cond in CONDITIONS:
        vals = [r["lgn"] for r in ideas if r["condition"] == cond]
        print(f"  {cond:24s} {statistics.mean(vals):.4f}")
    print("\nPer-condition set diversity (mean pairwise distance):")
    for cond in CONDITIONS:
        print(f"  {cond:24s} {cond_diversity[cond]['mean_pairwise_distance']:.4f} "
              f"dup={cond_diversity[cond]['dup_rate']:.3f}")
    return out


if __name__ == "__main__":
    compute()
