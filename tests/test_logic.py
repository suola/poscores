import random
from itertools import product

from poscores import combine


def _combine(scores):
    """convert input/output & combine"""
    in_ = [tuple(str(x) for x in score) for score in scores]
    res = combine(in_, "simple-max")
    out_ = [tuple(tuple(int(v) for v in x) for x in combo) for combo in res]
    return out_


class TestOneMatch:
    def test_one(self):
        scores = [(1, 1)]
        res = _combine(scores)
        assert len(res) == 1
        assert res == [((1,), (1,))]

    def test_two_distinct(self):
        scores = [(1, 1), (2, 2)]
        res = _combine(scores)
        assert len(res) == 2
        assert res == [((1,), (1,)), ((2,), (2,))]

    def test_two_combined(self):
        scores = [(1, 1), (2, 1)]
        res = _combine(scores)
        assert len(res) == 1
        assert res == [((1, 2), (1,))]

    def test_many_combined(self):
        scores = [(x, 1) for x in range(100)]
        res = _combine(scores)
        assert len(res) == 1
        assert res == [(tuple(range(100)), (1,))]

    def test_many_combined_both_scores(self):
        scores = list(product(range(100), repeat=2))
        assert len(scores) == 100 * 100
        res = _combine(scores)
        assert len(res) == 1

    def test_many_combined_both_scores_random_order(self):
        scores = list(product(range(100), repeat=2))
        random.shuffle(scores)
        assert len(scores) == 100 * 100
        res = _combine(scores)
        assert len(res) == 1

    def test_two_distinct_two_combined(self):
        scores = [(1, 1), (2, 1), (4, 2), (4, 3)]
        res = _combine(scores)
        assert len(res) == 2
        assert res == [((1, 2), (1,)), ((4,), (2, 3))]

    def test_three_combined_one_distinct(self):
        """Test size (3,1) is preferred to (2,2)"""
        scores = [(4, 1), (4, 2), (4, 4), (1, 2)]
        res = _combine(scores)
        assert len(res) == 2
        assert res == [((4,), (1, 2, 4)), ((1,), (2,))]

    def test_many_one_missing(self):
        scores = list(product(range(100), repeat=2))
        random.shuffle(scores)
        scores = scores[:-1]
        assert len(scores) == 100 * 100 - 1
        res = _combine(scores)
        assert len(res) == 2

    def test_many_draw_missing(self):
        scores = list((x, y) for x, y in product(range(100), repeat=2) if x != y)
        random.shuffle(scores)
        assert len(scores) == 100 * 100 - 100
        res = _combine(scores)
        # since draw is missing a separate combo for each home score is
        # required
        assert len(res) == 100


class TestManyMatches:
    def test_one(self):
        scores = [(1,) * 100]
        res = _combine(scores)
        assert len(res) == 1
        assert res == [((1,),) * 100]

    def test_two_distinct(self):
        scores = [(1,) * 100, (2,) * 100]
        res = _combine(scores)
        assert len(res) == 2

    def test_two_combined(self):
        scores = [(1,) * 100, (1,) * 99 + (2,)]
        res = _combine(scores)
        assert len(res) == 1

    def test_many_combined_all_scores(self):
        scores = list(product(range(5), repeat=5))
        random.shuffle(scores)
        assert len(scores) == 5**5
        res = _combine(scores)
        assert len(res) == 1
