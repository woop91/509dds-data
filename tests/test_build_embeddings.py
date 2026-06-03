import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_embeddings as be  # noqa: E402

DIM = be.DIM


def _stub(texts):
    """Deterministic fake embedder: vector seeded by text length, normalized."""
    out = np.zeros((len(texts), DIM), dtype=np.float32)
    for i, t in enumerate(texts):
        out[i, len(t) % DIM] = 1.0  # unit vector along one axis
    return out


def _cards():
    return [
        ("data/a.csv.meta.json", {"id": "a", "path": "data/a.csv", "title": "Alpha",
                                  "description": "first", "tags": ["x"]}),
        ("data/b.csv.meta.json", {"id": "b", "path": "data/b.csv", "title": "Beta",
                                  "description": "second", "tags": ["y"]}),
    ]


def test_build_returns_vectors_and_manifest_in_card_order():
    vecs, manifest = be.build(_cards(), embedder=_stub)
    assert vecs.shape == (2, DIM)
    assert vecs.dtype == np.float32
    assert manifest["count"] == 2
    assert manifest["dim"] == DIM
    assert manifest["model"] == be.MODEL
    assert [v["id"] for v in manifest["vectors"]] == ["a", "b"]
    assert manifest["vectors"][0]["path"] == "data/a.csv"
    assert manifest["vectors"][0]["tags"] == ["x"]


def test_pack_unpack_roundtrip():
    vecs, _ = be.build(_cards(), embedder=_stub)
    blob = be.pack(vecs)
    assert len(blob) == 2 * DIM * 4  # float32
    back = be.unpack(blob, DIM)
    assert np.array_equal(back, vecs)


def test_write_then_load_artifact_roundtrips(tmp_path):
    vecs, manifest = be.build(_cards(), embedder=_stub)
    be.write_artifact(vecs, manifest, tmp_path)
    assert (tmp_path / "index.bin").exists()
    assert (tmp_path / "manifest.json").exists()
    loaded_vecs, loaded_manifest = be.load_artifact(tmp_path)
    assert np.array_equal(loaded_vecs, vecs)
    assert loaded_manifest["count"] == 2
    assert loaded_manifest["vectors"][1]["id"] == "b"
