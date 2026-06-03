#!/usr/bin/env python3
"""search.py — semantic search over the 509dds-data card index.

Usage:
  python scripts/search.py "examiner burnout evidence"
  python scripts/search.py -k 5 --json "peer state pay scales"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_embeddings as be  # noqa: E402


def search(query, vectors, manifest, embedder=be.embed_query, k=8):
    q = embedder(query)
    scores = vectors @ q  # cosine == dot on normalized vectors
    top = np.argsort(-scores)[:k]
    hits = []
    for rank, idx in enumerate(top, start=1):
        v = manifest["vectors"][int(idx)]
        hits.append({"rank": rank, "score": float(scores[idx]),
                     "id": v["id"], "path": v["path"], "title": v["title"]})
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="natural-language search query")
    ap.add_argument("-k", type=int, default=8, help="number of results")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()
    vectors, manifest = be.load_artifact(be.OUT_DIR)
    hits = search(args.query, vectors, manifest, k=args.k)
    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
        return
    for h in hits:
        print(f"{h['rank']:2d}. {h['score']:.3f}  {h['path']}\n    {h['title']}")


if __name__ == "__main__":
    main()
