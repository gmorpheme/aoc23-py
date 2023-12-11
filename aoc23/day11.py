import re
from typing import NamedTuple
from itertools import accumulate, combinations

TEST_INPUT = [
    '...#......',
    '.......#..',
    '#.........',
    '..........',
    '......#...',
    '.#........',
    '.........#',
    '..........',
    '.......#..',
    '#...#.....',
]

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

class Universe:

    def __init__(self, galaxies):
        self.galaxies = set(galaxies)
        self.max_y = max(y for _, y in self.galaxies)
        self.max_x = max(x for x, _ in self.galaxies)

    def expanded(self, n = 2):
        x_gaps = [0 if any(filter(lambda t: t[0] == x, self.galaxies)) else n-1 for x in range (0, self.max_x + 1)]
        x_int = list(accumulate(x_gaps))
        x_shift = [d + x for x, d in zip(range(self.max_x + 1), x_int)]
        y_gaps = [0 if any(filter(lambda t: t[1] == y, self.galaxies)) else n-1 for y in range (0, self.max_y + 1)]
        y_int = accumulate(y_gaps)
        y_shift = [d + y for y, d in zip(range(self.max_y + 1), y_int)]
        return Universe((x_shift[x], y_shift[y]) for x, y in self.galaxies)

    def distances(self):
        return (manhattan_distance(a, b) for a, b in combinations(self.galaxies, 2))

    @staticmethod
    def parse(lines):
        return Universe(sum([[(m.start(), y) for m in re.finditer(r'\#', line)] for y, line in enumerate(lines)], []))

def day11a(lines):
    """
    >>> day11a(TEST_INPUT)
    374
    """
    return sum(Universe.parse(lines).expanded().distances())


def day11b(lines, n = 1_000_000):
    """
    >>> day11b(TEST_INPUT, 10)
    1030
    >>> day11b(TEST_INPUT, 100)
    8410
    """
    return sum(Universe.parse(lines).expanded(n).distances())


def main():
    with open('aoc23/data/day11input.txt') as fd:
        lines = list(fd)
    print(f'Day 11a: {day11a(lines)}')
    print(f'Day 11b: {day11b(lines)}')


if __name__ == '__main__':
    main()
