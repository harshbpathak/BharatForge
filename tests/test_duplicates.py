import pytest
from bharatforge.analyzer import load_demo
from bharatforge.duplicates import find_candidates


def test_identical_pair_and_no_self_comparison():
    issue = load_demo().issues[0].issue
    second = issue.model_copy(update={"number":999})
    pairs = find_candidates([issue, second], threshold=.9)
    assert len(pairs) == 1
    assert pairs[0].first != pairs[0].second
    assert pairs[0].similarity == pytest.approx(1)


def test_empty_small_and_stop_words():
    assert find_candidates([]) == []
    issue = load_demo().issues[0].issue
    assert find_candidates([issue]) == []
    blank = issue.model_copy(update={"title":"the and", "body":""})
    assert find_candidates([blank, blank.model_copy(update={"number":999})]) == []


def test_unrelated_text_and_limit():
    issue = load_demo().issues[0].issue
    second = issue.model_copy(update={"number":999, "title":"Oranges apples pears", "body":""})
    assert not find_candidates([issue, second], .5)
    same = [issue.model_copy(update={"number":number}) for number in range(1, 10)]
    assert len(find_candidates(same)) == 8
    with pytest.raises(ValueError):
        find_candidates(same, 1.1)
