# poscores

Combine match scores into systems.

## Introduction

Purpose of the program is to combine match scores into combinations of scores.
A combination is defined as set of values for each score so that a cartesian
product will generate only valid match scores.

Example:

- 3 matches
- score 1: 2-1, 0-0, 3-0
- score 2: 3-1, 0-0, 3-0
- score 3: 4-1, 1-0, 3-0

Scores 1 and 2 can be combined, so the output will contain two score
combinations.

- {2,3}-1, 0-0, 3-0
- 4-1, 1-0, 3-0

Score 3 cannot be combined since the result of the 2nd match differs from the
two other scores.

## Match score

Match scores are handled as individual goal counts. This is equivalent and
simpler when searching for possible combinations.

## Terminology

| Term   | Explanation | Example w/ 2 matches |
| ------ | ----------- | ------- |
| pts    | Number of goals / points scored by one team | "1" |
| score  | Points for each team | ("1", "2", "0", "3") |
| combo  | Score combination | ("1","2") or ("2",) |
| scores | All scores / combos. Each value maybe a point or a combo | (("1","2"), ("2",), "0", ("3",)) |

## Example:

```
➜ python poscores/main.py input/2310.txt
Summary:
Input 2310 scores, generated 1328 coupons
top 20 coupon sizes: 8, 8, 8, 8, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5, 4, 4, 4
5.24 % of scores covered by first 20 coupons
```
