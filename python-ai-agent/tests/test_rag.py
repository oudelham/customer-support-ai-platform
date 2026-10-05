from src.rag.evaluation import precision_at_k, recall_at_k


def test_precision():
    results = [{"source": "a"}, {"source": "b"}, {"source": "c"}]
    assert precision_at_k(results, {"a", "c"}, 2) == 0.5


def test_recall():
    results = [{"source": "a"}, {"source": "b"}, {"source": "c"}]
    assert recall_at_k(results, {"a", "c"}, 3) == 1.0
