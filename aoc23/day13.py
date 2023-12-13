from itertools import groupby

TEST_INPUT = [
    '#.##..##.',
    '..#.##.#.',
    '##......#',
    '##......#',
    '..#.##.#.',
    '..##..##.',
    '#.#.##.#. ',
    '',
    '#...##..#',
    '#....#..#',
    '..##..###',
    '#####.##.',
    '#####.##.',
    '..##..###',
    '#....#..#',
]

def find_reflection(values):
    growing = []
    shrinking = []

    for n, value in enumerate(values):
        shrinking = [s[:-1] for s in shrinking if s[-1] == value]
        if not(all(shrinking)): return (n + 1) // 2

        match growing:
            case [x]:
                if x == value: return 1
            case [*xs, x] if x == value: shrinking.append(xs)

        growing.append(value)

    if shrinking:
        return (len(values) + len(shrinking[0])) // 2

def find_smudged_reflection(values):
    growing = []
    shrinking_precise = []
    shrinking_smudged = []

    def differ_by_one(l, r):
        return sum(1 for a, b in zip(l, r) if a != b) == 1

    for n, value in enumerate(values):
        shrinking_smudged = \
            [s[:-1] for s in shrinking_smudged if s[-1] == value] + \
            [s[:-1] for s in shrinking_precise if differ_by_one(s[-1], value)]
        shrinking_precise = \
            [s[:-1] for s in shrinking_precise if s[-1] == value and len(s) > 1]
        if not(all(shrinking_smudged)): return (n + 1) // 2

        match growing:
            case [x]:
                if differ_by_one(x, value): return 1
            case [*xs, x] if differ_by_one(x, value): shrinking_smudged.append(xs)
            case [*xs, x] if x == value: shrinking_precise.append(xs)

        growing.append(value)

    if shrinking_smudged:
        return (len(values) + len(shrinking_smudged[0])) // 2

class Puzzle:

    def __init__(self, lines):
        self.rows = [line.strip() for line in lines]
        self.cols = [''.join(row[n] for row in self.rows) for n in range(len(self.rows[0]))]

    def solution_a(self):
        return find_reflection([hash(c) for c in self.cols]) or (100 * (find_reflection([hash(r) for r in self.rows]) or 0))

    def solution_b(self):
        return find_smudged_reflection(self.cols) or (100 * (find_smudged_reflection(self.rows) or 0))

def day13a(lines):
    """
    >>> day13a(TEST_INPUT)
    405
    """
    puzzles = [Puzzle(block) for k, block in groupby((x.strip() for x in lines), key = lambda x: len(x)) if k]
    return sum(puzzle.solution_a() for puzzle in puzzles)


def day13b(lines):
    """
    >>> day13b(TEST_INPUT)
    400
    """
    puzzles = [Puzzle(block) for k, block in groupby((x.strip() for x in lines), key = lambda x: len(x)) if k]
    return sum(puzzle.solution_b() for puzzle in puzzles)

def main():
    with open('aoc23/data/day13input.txt') as fd:
        lines = list(fd)
    print(f'Day 13a: {day13a(lines)}')
    print(f'Day 13b: {day13b(lines)}')

if __name__ == '__main__':
    main()
