"""
Test performance

Requires matplotlib which must be manually installed.
"""

import random
import sys
from itertools import product

try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit("matplotlib must be manually installed")

from poscores import combine


def _combine(scores):
    """convert input/output & combine"""
    in_ = [tuple(str(x) for x in score) for score in scores]
    res = combine(in_, "simple-max")
    out_ = [tuple(tuple(int(v) for v in x) for x in combo) for combo in res]
    return out_


def test_share_missing():
    # 4 games, scores 0-3 for all teams
    scores = list(product(range(4), repeat=8))
    n = len(scores)
    random.shuffle(scores)
    stats = {}
    for i in range(1, 101):
        partial_scores = scores[: int(i / 100 * len(scores))]
        res = _combine(partial_scores)
        print(i, len(partial_scores), len(res))
        stats[i] = (
            100 * len(partial_scores) / n,
            100 * len(res) / n,
            100 * len(res) / len(partial_scores),
        )

    plt.plot(stats.values())
    plt.grid(True)
    plt.title(f"4 matches w/ {{0..3}}-{{0..3}} ({n} possible combinations)")
    plt.xlabel("% of results included")
    plt.ylabel("% of coupons needed")
    plt.legend(["rows", "coupons", "coupons/rows"])
    plt.show()
