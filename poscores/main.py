"""
Combine sport scores into combinations

Input:
- list of scores
- score: list of goals

Output
- list of score combinations
- score combination: list of goal options
- goal option: list of possible goals
"""

import argparse
import logging
import math
import pathlib
import random
import sys
from collections import defaultdict
from collections.abc import Iterable
from itertools import chain

# types
# input score, e.g. ("1", "2", "3", "1")
Score = tuple[str]
# output combo, e.g. (("1",), ("1", "2"), ("3",), ("1",))
Combo = tuple[tuple[str]]

logger = logging.getLogger("main")


def combine(scores: Iterable[Score], method="simple"):
    """Combine scores with a method."""
    if not scores:
        return ()

    # assert all scores have same number of games
    assert len(set(len(x) for x in scores)) == 1
    n = len(scores[0])
    logger.info(f"Found {len(scores)} results for {n//2} games")

    try:
        fcn = combine_fcns[method]
    except KeyError:
        raise ValueError(f"Invalid combine method {method}")

    return fcn(scores)


def combine_simple(scores):
    """Combine scores
    - in one round
    - in same order, from first to last score
    - require perfect match.
    """
    n = len(scores[0])
    logger.debug(f"combine_simple() for {n} results")
    for i in range(n):
        scores = list(find_combinations(scores, i))
        logger.debug(f"{i} {len(scores)} {len(scores[0][i])} {scores[0]}")
    return scores


def combine_simple_random(scores):
    """Combine scores
    - in one round
    - in random order
    - require perfect match
    """
    n = len(scores[0])
    for i in random.sample(range(n), k=n):
        scores = list(find_combinations(scores, i))
        logger.debug(f"{i} {len(scores)} {len(scores[0][i])} {scores[0]}")
    return scores


def combine_simple_max(scores):
    """Combine scores
    - on each round combine the score that compresses the most
    - require perfect match
    """
    n = len(scores[0])
    to_combine = set(range(n))
    while to_combine:
        # find the index of the remaning scores that compresses the most
        i_best = None
        min_len = math.inf
        for i in sorted(to_combine):
            d2 = list(find_combinations(scores, i))
            if len(d2) < min_len:
                i_best = i
                min_len = len(d2)

        # Now combine best option
        scores = list(find_combinations(scores, i_best))
        to_combine.remove(i_best)
        logger.debug(f"{i_best} {len(scores)} {len(scores[0][i_best]),} {scores[0]}")

    return scores


def combine_only_max(scores):
    """Combine scores
    - on each only one new combination, the one that compresses the most
    - require perfect match
    """
    n = len(scores)
    while True:
        scores = tuple(combine_one_combo(scores))
        if len(scores) == n:
            break
        n = len(scores)

    return scores


def combine_one_combo(scores):
    """Find combo that combines the most."""
    d = defaultdict(set)
    items = defaultdict(set)

    for i in range(len(scores[0])):
        for j, x in enumerate(scores):
            key = i, x[:i], x[i + 1 :]
            d[key].update(*x[i])
            items[key].add(j)

    k, js = sorted(items.items(), key=lambda x: len(x[1]), reverse=True)[0]

    logger.debug(f"combine {len(js)} {k=} {d[k]}")
    # now combine only the max
    yield k[1] + (tuple(sorted(d[k])),) + k[2]
    for j, row in enumerate(scores):
        if j not in js:
            yield row


def find_combinations(scores: Iterable[Score], i: int) -> Iterable[Combo]:
    """Find combinations from i'th item in scores."""
    # Key: tuple(pts before i, pts after i)
    # Value: combo values as set
    d = defaultdict(set)

    for score in scores:
        before, pts, after = score[:i], score[i], score[i + 1 :]
        if isinstance(pts, str):
            d[before, after].add(pts)
        else:
            d[before, after].update(*pts)

    # Sort by combo size, and combine collected combo with other pts
    for k, combo in sorted(d.items(), key=lambda x: x[1], reverse=True):
        yield k[0] + (sort_combo(combo),) + k[1]


def sort_combo(x: Combo) -> Combo:
    """Sort one combo"""
    return tuple(sorted(x, key=lambda x: int(x)))


def load_input(path: pathlib.Path) -> Iterable[Score]:
    """Load data from input file.

    Input should contain lines in format:
    "1-0;2-0;2-0;1-1"
    """
    try:
        data = open(path).read()
    except Exception as e:
        sys.exit(f"Error reading input {path} {e}")

    scores = (parse_input_line(line.strip()) for line in data.split("\n"))
    return list(filter(None, scores))


def parse_input_line(line: str) -> Score | None:
    """Parse input line into processable format.

    Input is assumed to be in format:
    3-1;2-1

    Function converts the input to format
    ("3", "1", "2", "1")
    """
    if not line:
        return None

    results = line.strip().split(";")
    return tuple(chain.from_iterable(x.split("-") for x in results))


def save_results(data: Iterable[Combo], path: pathlib.Path):
    """Save results into output file."""
    try:
        with open(path, "w") as fid:
            for row in data:
                fid.write(fmt_output(row) + "\n")
    except Exception as e:
        sys.exit(f"Error saving results in {path} {e}")


def fmt_output(combo: Combo) -> str:
    """Format one combination for output file."""
    home = combo[::2]
    away = combo[1::2]
    return ";".join(f"{','.join(h)}-{','.join(a)}" for h, a in zip(home, away))


def get_result_stats(data, n_input, n_top=20) -> dict:
    """Get result stats."""
    n = sum(n_combos(x) for x in data)
    data = sorted(data, key=lambda x: n_combos(x), reverse=True)
    n_top = min(n_top, len(data))

    return {
        "n_input": n_input,
        "n_output": len(data),
        "n_top": n_top,
        "n_top_sizes": [n_combos(row) for row in data[:n_top]],
        "n_top_percentage": 100 * sum(n_combos(x) for x in data[:n_top]) / n,
    }


def print_stats(stats: dict):
    """Print result stats."""
    print("Summary:")
    print(f"Input {stats['n_input']} scores, generated {stats['n_output']} coupons")
    print(
        f"top {stats['n_top']} coupon sizes: {', '.join(str(x) for x in stats['n_top_sizes'])}"
    )
    print(
        f"{stats['n_top_percentage']:.2f} % of scores covered by first {stats['n_top']} coupons"
    )


def n_combos(entry: Combo) -> int:
    return math.prod(len(x) if isinstance(x, (tuple)) else 1 for x in entry)


# Supported combine functions
combine_fcns = {
    "simple": combine_simple,
    "simple-max": combine_simple_max,
    "simple-random": combine_simple_random,
    "only-max": combine_only_max,
}


def run(
    input_path: pathlib.Path,
    output_path: pathlib.Path,
    *,
    method: str = "simple-max",
):
    """Combine from input to output file w/ method."""
    data = load_input(input_path)
    res = combine(data, method)
    save_results(res, output_path)
    stats = get_result_stats(res, len(data))
    print_stats(stats)


def cli_args():
    """Define and parse command line arguments."""
    parser = argparse.ArgumentParser(description="Combine scores.")
    parser.add_argument("input", nargs="?", type=pathlib.Path, default="input.txt")
    parser.add_argument("output", nargs="?", type=pathlib.Path, default="output.txt")
    parser.add_argument("-v", dest="verbosity", action="count", default=0)
    parser.add_argument(
        "-m", "--method", default="simple-max", choices=combine_fcns.keys()
    )
    return parser.parse_args()


def main():
    """Run as script main function."""
    args = cli_args()
    log_level = 30 - args.verbosity * 10
    logging.basicConfig(level=log_level)
    run(args.input, args.output, method=args.method)


# To run by importing the script:
# fn = "input.txt"
# run(fn, method="simple")
# run(fn, method="simple-max")
# run(fn, method="simple-random")
# run(fn, method="only-max")


if __name__ == "__main__":
    main()
