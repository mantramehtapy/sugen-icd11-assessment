from analysis.failure_report import classify_failure


def test_classify_failure_distinguishes_retrieval_and_ranking():
    assert classify_failure(gold_in_candidates=False, predicted_top1=False) == "retrieval"
    assert classify_failure(gold_in_candidates=True, predicted_top1=False) == "ranking"
    assert classify_failure(gold_in_candidates=True, predicted_top1=True) == "correct"
