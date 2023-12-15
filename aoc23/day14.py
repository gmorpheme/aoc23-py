from typing import NamedTuple
from collections import Counter

TEST_INPUT = [
    'O....#....',
    'O.OO#....#',
    '.....##...',
    'OO.#O....O',
    '.O.....O#.',
    'O.#..O.#.#',
    '..O..#O..O',
    '.......O..',
    '#....###..',
    '#OO..#....',
]

CYCLE_1 = [
    '.....#....',
    '....#...O#',
    '...OO##...',
    '.OO#......',
    '.....OOO#.',
    '.O#...O#.#',
    '....O#....',
    '......OOOO',
    '#...O###..',
    '#..OO#....',
]

CYCLE_2 = [
    '.....#....',
    '....#...O#',
    '.....##...',
    '..O#......',
    '.....OOO#.',
    '.O#...O#.#',
    '....O#...O',
    '.......OOO',
    '#..OO###..',
    '#.OOO#...O',
]

CYCLE_3 = [
    '.....#....',
    '....#...O#',
    '.....##...',
    '..O#......',
    '.....OOO#.',
    '.O#...O#.#',
    '....O#...O',
    '.......OOO',
    '#...O###.O',
    '#.OOO#...O',
]

def tilt(items):
    balls = gaps = 0
    output = []
    for item in items:
        match item:
            case '.': gaps += 1
            case 'O': balls += 1
            case '#':
                output.extend(gaps * ['.'] + balls * ['O'] + ['#'])
                gaps = balls = 0
    output.extend(gaps * ['.'] + balls * ['O'])

    return output

class Puzzle:

    def __init__(self, lines):
        self.rows = [list(row.strip()) for row in lines]

    def __getitem__(self, key):
        x, y = key
        if isinstance(y, slice):
            return [r[x] for r in self.rows[y]]
        else:
            return self.rows[y][x]

    def __setitem__(self, key, val):
        x, y = key
        if isinstance(y, slice):
            for i, r in enumerate(self.rows[y]):
                 r[x] = val[i]
        else:
            self.rows[y][x] = val

    def tilt_n(self):
        for x in range(len(self.rows[0])): self[x, ::-1] = tilt(self[x, ::-1])
        return self

    def tilt_s(self):
        for x in range(len(self.rows[0])): self[x, :] = tilt(self[x, :])
        return self

    def tilt_e(self):
        for y in range(len(self.rows)): self[:, y] = tilt(self[:, y])
        return self

    def tilt_w(self):
        for y in range(len(self.rows)): self[::-1, y] = tilt(self[::-1, y])
        return self

    def step(self):
        """
        >>> p = Puzzle(TEST_INPUT)
        >>> p.step() == Puzzle(CYCLE_1)
        True
        >>> p.step() == Puzzle(CYCLE_2)
        True
        >>> p.step() == Puzzle(CYCLE_3)
        True
        """
        return self.tilt_n().tilt_w().tilt_s().tilt_e()

    def run(self, steps):
        checkpoints = {}
        cycle_target = None
        for i in range(steps):

            if i == cycle_target:
                return self

            if i % 1000 == 0:
                if not cycle_target:
                    h = hash(self)
                    if h in checkpoints:
                        cycle_start = checkpoints[h]
                        cycle_length = i - cycle_start
                        n = (steps - cycle_start) % cycle_length
                        if n == 0:
                            return self
                        cycle_target = i + n
                    else:
                        checkpoints[h] = i

            self.step()

        return self

    def evaluate_load(self):
        return sum((i+1) * Counter(r)['O'] for i, r in enumerate(self.rows[::-1]))

    def __eq__(self, other):
        return self.rows == other.rows

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.rows))

def day14a(lines):
    """
    >>> day14a(TEST_INPUT)
    136
    """
    return Puzzle(lines).tilt_n().evaluate_load()


def day14b(lines):
    """
    >>> day14b(TEST_INPUT)
    64
    """
    return Puzzle(lines).run(1_000_000_000).evaluate_load()

def main():
    with open('aoc23/data/day14input.txt') as fd:
        lines = list(fd)
    print(f'Day 14a: {day14a(lines)}')
    print(f'Day 14b: {day14b(lines)}')

if __name__ == '__main__':
    main()
