"""Build a per-topic prior-work corpus from Semantic Scholar.

Used for (a) the objective Literature-Grounded Novelty metric (embedding distance
to nearest real prior paper) and (b) the literature_comparison condition's
injected references. Cached to disk; safe to re-run.
"""
import json
import os
import time

import requests

from config import CORPUS_FILE, CORPUS_PER_TOPIC, TOPICS

S2_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"


def _search(query, limit):
    headers = {}
    if os.getenv("S2_API_KEY"):
        headers["x-api-key"] = os.getenv("S2_API_KEY")
    papers = []
    offset = 0
    while len(papers) < limit:
        batch = min(100, limit - len(papers))
        for attempt in range(5):
            try:
                r = requests.get(
                    S2_SEARCH,
                    params={
                        "query": query,
                        "fields": "title,abstract,year,citationCount",
                        "limit": batch,
                        "offset": offset,
                    },
                    headers=headers,
                    timeout=40,
                )
                if r.status_code == 429:
                    time.sleep(5 * (attempt + 1))
                    continue
                r.raise_for_status()
                data = r.json()
                break
            except Exception:
                time.sleep(3 * (attempt + 1))
                data = {"data": []}
        rows = data.get("data", [])
        if not rows:
            break
        for p in rows:
            if p.get("abstract"):
                papers.append({
                    "title": p["title"],
                    "abstract": p["abstract"],
                    "year": p.get("year"),
                    "citationCount": p.get("citationCount", 0),
                })
        offset += batch
        if offset >= 1000:
            break
        time.sleep(1.2)
    return papers


# Short, retrieval-friendly queries (S2 search prefers concise keyword queries).
TOPIC_QUERIES = {
    "Bias": "reducing social bias in large language models prompting",
    "Coding": "prompting large language models code generation",
    "Safety": "large language model jailbreak adversarial robustness prompting",
    "Multilingual": "multilingual prompting large language models low-resource",
    "Factuality": "reducing hallucination factuality large language models prompting",
    "Math": "mathematical reasoning prompting large language models",
    "Uncertainty": "uncertainty calibration confidence large language models",
}


def build_corpus(force=False):
    if os.path.exists(CORPUS_FILE) and not force:
        with open(CORPUS_FILE) as f:
            return json.load(f)
    corpus = {}
    for topic, desc in TOPICS.items():
        query = TOPIC_QUERIES.get(topic, desc)
        papers = _search(query, CORPUS_PER_TOPIC)
        if len(papers) < 20:  # fallback to an even simpler query
            papers = _search(topic + " large language models", CORPUS_PER_TOPIC)
        corpus[topic] = papers
        print(f"  {topic}: retrieved {len(papers)} abstracts")
    with open(CORPUS_FILE, "w") as f:
        json.dump(corpus, f)
    return corpus


def prior_work_snippets(corpus, topic, k=8):
    """Return k short 'Title — abstract[:300]' strings for literature_comparison.

    Pick a diverse, well-cited sample so the model must differentiate from real,
    influential work (not obscure papers).
    """
    papers = sorted(corpus.get(topic, []), key=lambda p: -p.get("citationCount", 0))
    snippets = []
    for p in papers[: k * 3][::3][:k]:  # spread across the cited ranking
        ab = p["abstract"][:300].replace("\n", " ")
        snippets.append(f"{p['title']} — {ab}")
    return snippets


if __name__ == "__main__":
    c = build_corpus()
    total = sum(len(v) for v in c.values())
    print(f"Total abstracts: {total}")
