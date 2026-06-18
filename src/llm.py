"""Thin, cached, retrying LLM client shared by generation and judging.

Every call is keyed by (model, messages, params) and cached to disk so the
entire experiment reproduces exactly and re-runs cost nothing. Token usage is
accumulated for cost reporting.
"""
import hashlib
import json
import os
import threading
import time

from openai import OpenAI

from config import CACHE, PROVIDERS

_clients = {}
_usage = {"calls": 0, "cache_hits": 0, "prompt_tokens": 0, "completion_tokens": 0}
_lock = threading.Lock()


def _client(provider):
    if provider not in _clients:
        cfg = PROVIDERS[provider]
        _clients[provider] = OpenAI(
            base_url=cfg["base_url"], api_key=os.getenv(cfg["key_env"])
        )
    return _clients[provider]


def _cache_path(key):
    h = hashlib.sha256(key.encode()).hexdigest()[:32]
    return os.path.join(CACHE, h + ".json")


def chat(messages, model, provider="openai", temperature=0.7, max_tokens=1200,
         top_p=1.0, seed=None, json_mode=False):
    """Return assistant text for a chat completion, using an on-disk cache.

    The cache key includes every parameter that affects the output, so changing
    any of them produces a fresh call while identical calls are free.
    """
    key = json.dumps({
        "model": model, "messages": messages, "temperature": temperature,
        "max_tokens": max_tokens, "top_p": top_p, "seed": seed,
        "json_mode": json_mode,
    }, sort_keys=True)
    path = _cache_path(key)
    if os.path.exists(path):
        with _lock:
            _usage["cache_hits"] += 1
        with open(path) as f:
            return json.load(f)["content"]

    kwargs = dict(model=model, messages=messages, temperature=temperature,
                  max_tokens=max_tokens, top_p=top_p)
    if seed is not None:
        kwargs["seed"] = seed
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    last_err = None
    for attempt in range(6):
        try:
            resp = _client(provider).chat.completions.create(**kwargs)
            content = resp.choices[0].message.content or ""
            with _lock:
                _usage["calls"] += 1
                if resp.usage:
                    _usage["prompt_tokens"] += resp.usage.prompt_tokens
                    _usage["completion_tokens"] += resp.usage.completion_tokens
            with open(path, "w") as f:
                json.dump({"content": content, "model": model}, f)
            return content
        except Exception as e:  # noqa: BLE001 - robust to any provider error
            last_err = e
            wait = min(2 ** attempt, 30)
            time.sleep(wait)
    raise RuntimeError(f"LLM call failed after retries: {last_err}")


def usage_summary():
    """Return a copy of cumulative usage + a rough USD cost estimate."""
    u = dict(_usage)
    # Rough blended estimate (gpt-4.1 ~$2/$8 per M; judges cheaper). Order-of-mag.
    u["est_cost_usd"] = round(
        _usage["prompt_tokens"] / 1e6 * 2.0
        + _usage["completion_tokens"] / 1e6 * 8.0, 3)
    return u


def extract_json(text):
    """Best-effort JSON extraction from a model response (handles code fences)."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip("` \n")
    # find the outermost object
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return json.loads(text)
