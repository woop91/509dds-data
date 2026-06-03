import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from suggest_related import collection_dir, propose  # noqa: E402


def test_collection_dir():
    assert collection_dir("data/pay-scales/peer-states/CA/scheduled-rates.json") == "data/pay-scales/peer-states/CA"


def test_propose_small_cluster_pairs_only_and_flags_large():
    cards = []
    # small cluster: dir X has 2 members, neither linked -> 1 suggested pair
    cards.append(("m1", {"id": "x/a", "path": "data/x/a.json", "related": []}))
    cards.append(("m2", {"id": "x/b", "path": "data/x/b.json"}))  # no related key
    # large cluster: dir BIG has 5 members (> max_cluster=4) -> flagged, NOT paired
    for i in range(5):
        cards.append((f"b{i}", {"id": f"big/c{i}", "path": f"data/big/c{i}.json"}))
    res = propose(cards, max_cluster=4)
    pairs = {tuple(sorted(p)) for p in res["suggestions"]}
    assert ("x/a", "x/b") in pairs
    assert all("big/" not in a and "big/" not in b for a, b in pairs)  # large cluster not paired
    flagged = {f["dir"]: f["size"] for f in res["skipped_large_clusters"]}
    assert flagged.get("data/big") == 5
    # single-member dirs produce nothing
    assert all(len(p) == 2 for p in res["suggestions"])


def test_propose_skips_pairs_already_linked():
    cards = [
        ("m1", {"id": "x/a", "path": "data/x/a.json", "related": ["x/b"]}),
        ("m2", {"id": "x/b", "path": "data/x/b.json", "related": ["x/a"]}),
    ]
    res = propose(cards, max_cluster=4)
    assert res["suggestions"] == []  # already mutually linked
