from typing import NamedTuple
from math import sqrt, pow, ceil, floor
from functools import reduce
from operator import mul

TEST_INPUT = ['Time:      7  15   30', 'Distance:  9  40  200']


class Race(NamedTuple):
    time: int
    distance: int

    def roots(self):
        # roots of c(t - c) = d => -t ± sqrt(t^2 - 4d)  / -2
        disc = sqrt(pow(self.time, 2) - (4 * self.distance))
        root_a = (-self.time + disc) / -2
        root_b = (-self.time - disc) / -2
        return (root_a, root_b)

    def winning_range(self):
        l, r = self.roots()
        return range(floor(l + 1), ceil(r))

    def __repr__(self):
        return f'<Race({self.time}, {self.distance})>'


class Puzzle(NamedTuple):
    races: list[Race]

    @staticmethod
    def parse_a(lines):
        times = [int(t) for t in lines[0].split(':')[1].split()]
        distances = [int(t) for t in lines[1].split(':')[1].split()]
        return Puzzle([Race(*t) for t in zip(times, distances)])

    @staticmethod
    def parse_b(lines):
        time = int(''.join(t for t in lines[0].split(':')[1].split()))
        distance = int(''.join(t for t in lines[1].split(':')[1].split()))
        puzzle = Puzzle([Race(time, distance)])
        return puzzle

    def error_margin(self):
        return reduce(mul, (len(race.winning_range()) for race in self.races), 1)


def day6a(lines):
    """
    >>> day6a(TEST_INPUT)
    288
    """
    return Puzzle.parse_a(lines).error_margin()


def day6b(lines):
    """
    >>> day6b(TEST_INPUT)
    71503
    """
    return Puzzle.parse_b(lines).error_margin()


def main():
    with open('aoc23/data/day6input.txt') as f:
        lines = list(f)
    print(f'Day 6a: {day6a(lines)}')
    print(f'Day 6b: {day6b(lines)}')


if __name__ == '__main__':
    main()
