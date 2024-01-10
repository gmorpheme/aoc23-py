import re
from dataclasses import dataclass
from itertools import cycle
from math import lcm

TEST_INPUT_A = [
    'RL',
    '',
    'AAA = (BBB, CCC)',
    'BBB = (DDD, EEE)',
    'CCC = (ZZZ, GGG)',
    'DDD = (DDD, DDD)',
    'EEE = (EEE, EEE)',
    'GGG = (GGG, GGG)',
    'ZZZ = (ZZZ, ZZZ)',
]

TEST_INPUT_B = [
    'LLR',
    '',
    'AAA = (BBB, BBB)',
    'BBB = (AAA, ZZZ)',
    'ZZZ = (ZZZ, ZZZ)',
]

TEST_INPUT_C = [
    'LR',
    '',
    '11A = (11B, XXX)',
    '11B = (XXX, 11Z)',
    '11Z = (11B, XXX)',
    '22A = (22B, XXX)',
    '22B = (22C, 22C)',
    '22C = (22Z, 22Z)',
    '22Z = (22B, 22B)',
    'XXX = (XXX, XXX)',
]

link_re = re.compile(r'(\w{3}) = \((\w{3}), (\w{3})\)')


@dataclass
class Puzzle:
    route: list[int]
    graph: dict[str, tuple[str, str]]

    def follow(self, start='AAA'):
        node = start
        route = cycle(self.route)
        tick = 0
        while True:
            choice = next(route)
            tick += 1
            node = self.graph[node][choice]
            yield (choice, node, tick)

    @staticmethod
    def parse(lines):
        route = list(('L', 'R').index(c) for c in lines[0].strip())
        graph = {
            n: (l, r)
            for n, l, r in (link_re.match(line).groups() for line in lines[2:])
        }
        return Puzzle(route, graph)

    def ghost_starts(self):
        return [n for n in self.graph.keys() if n.endswith('A')]

    def measure_cycle(self, start):
        it = (state for state in self.follow(start) if state[1].endswith('Z'))
        a = next(it)[2]
        b = next(it)[2]
        # assert a % len(self.route) == 0
        # assert b % len(self.route) == 0
        return b - a


def day8a(lines):
    """
    >>> day8a(TEST_INPUT_A)
    2
    >>> day8a(TEST_INPUT_B)
    6
    """
    return next(
        t for _, (_, n, t) in enumerate(Puzzle.parse(lines).follow()) if n == 'ZZZ'
    )


def day8b(lines):
    """
    >>> day8b(TEST_INPUT_C)
    6
    """
    puzzle = Puzzle.parse(lines)
    return lcm(*[puzzle.measure_cycle(s) for s in puzzle.ghost_starts()])


def main():
    with open('aoc23/data/day8input.txt') as fd:
        lines = list(fd)
    print(f'Day 8a: {day8a(lines)}')
    print(f'Day 8b: {day8b(lines)}')


if __name__ == '__main__':
    main()
