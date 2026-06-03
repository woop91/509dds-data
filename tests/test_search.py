import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_embeddings as be  # noqa: E402
import search as srch  # noqa: E402

DIM = be.DIM


def test_search_ranks_by_cosine():
    # 3 unit vectors along axes 0,1,2
    vectors = np.zeros((3, DIM), dtype=np.float32)
    for i in range(3):
        vectors[i, i] = 1.0
    manifest = {"dim": DIM, "vectors": [
        {"id": "a", "path": "data/a", "title": "A"},
        {"id": "b", "path": "data/b", "title": "B"},
        {"id": "c", "path": "data/c", "title": "C"},
    ]}

    def stub_query(q):
        v = np.zeros(DIM, dtype=np.float32)
        v[1] = 1.0  # aligns with vector "b"
        return v

    hits = srch.search("anything", vectors, manifest, embedder=stub_query, k=2)
    assert hits[0]["id"] == "b"
    assert hits[0]["rank"] == 1
    assert abs(hits[0]["score"] - 1.0) < 1e-5
    assert len(hits) == 2


@pytest.mark.integration
def test_real_search_finds_payscale_card():
    pytest.importorskip("fastembed")
    repo = Path(__file__).resolve().parents[1]
    vectors, manifest = be.load_artifact(repo / "embeddings")
    hits = srch.search("disability examiner salary pay scale", vectors, manifest, k=10)
    paths = " ".join(h["path"] for h in hits)
    assert "pay-scales" in paths  # a pay-scale dataset surfaces in top-10
