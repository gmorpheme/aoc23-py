from typing import NamedTuple, List
from enum import Enum
from itertools import takewhile
from operator import eq

TEST_INPUT_1 = [
    '-L|F7',
    '7S-7|',
    'L|7||',
    '-L-J|',
    'L|-JF',
]

TEST_INPUT_2  = [
    '..F7.',
    '.FJ|.',
    'SJ.L7',
    '|F--J',
    'LJ...',
]

TEST_INPUT_3 = [
    '...........',
    '.S-------7.',
    '.|F-----7|.',
    '.||.....||.',
    '.||.....||.',
    '.|L-7.F-J|.',
    '.|..|.|..|.',
    '.L--J.L--J.',
    '...........',
]

TEST_INPUT_4 = [
    '.F----7F7F7F7F-7....',
    '.|F--7||||||||FJ....',
    '.||.FJ||||||||L7....',
    'FJL7L7LJLJ||LJ.L-7..',
    'L--J.L7...LJS7F-7L7.',
    '....F-J..F7FJ|L7L7L7',
    '....L7.F7||L7|.L7L7|',
    '.....|FJLJ|FJ|F7|.LJ',
    '....FJL-7.||.||||...',
    '....L---J.LJ.LJLJ...',
]

TEST_INPUT_5 = [
    'FF7FSF7F7F7F7F7F---7',
    'L|LJ||||||||||||F--J',
    'FL-7LJLJ||||||LJL-77',
    'F--JF--7||LJLJ7F7FJ-',
    'L---JF-JLJ.||-FJLJJ7',
    '|F|F-JF---7F7-L7L|7|',
    '|FFJF7L7F-JF7|JL---7',
    '7-L-JL7||F7|L7F-7F7|',
    'L.L7LFJ|||||FJL7||LJ',
    'L7JLJL-JLJLJL--JLJ.L',
]


class Direction(Enum):
    N = 0
    S = 1
    E = 2
    W = 4

N,S,E,W = [Direction.N, Direction.S, Direction.E, Direction.W]

class Pos(NamedTuple):
    x: int
    y: int

    def move(self, d):
        match d:
            case Direction.N: return Pos(self.x, self.y - 1)
            case Direction.S: return Pos(self.x, self.y + 1)
            case Direction.E: return Pos(self.x + 1, self.y)
            case Direction.W: return Pos(self.x - 1, self.y)


class Puzzle:

    def __init__(self, lines):
        self.lines = [line.strip() for line in lines]
        self.start = self.find_start()
        self.dirs = set(self.available_directions(self.start))

    def __getitem__(self, pos):
        return self.lines[pos.y][pos.x]

    def find_start(self):
        for y, line in enumerate(self.lines):
            for x, c in enumerate(line):
                if c == 'S':
                    return Pos(x, y)

    def available_directions(self, pos) -> List[Direction]:
        dirs = [
            self.enter(N, pos.move(N)) and N,
            self.enter(S, pos.move(S)) and S,
            self.enter(E, pos.move(E)) and E,
            self.enter(W, pos.move(W)) and W]
        return [d for d in dirs if d]

    def enter(self, entry_dir, pos) -> tuple[Direction, Pos] | None:

        match entry_dir, self[pos]:
            case (Direction.N, '|'): exit_dir = N
            case (Direction.S, '|'): exit_dir = S
            case (Direction.E, '-'): exit_dir = E
            case (Direction.W, '-'): exit_dir = W
            case (Direction.N, 'F'): exit_dir = E
            case (Direction.W, 'F'): exit_dir = S
            case (Direction.E, '7'): exit_dir = S
            case (Direction.N, '7'): exit_dir = W
            case (Direction.S, 'J'): exit_dir = W
            case (Direction.E, 'J'): exit_dir = N
            case (Direction.S, 'L'): exit_dir = E
            case (Direction.W, 'L'): exit_dir = N
            case _: return None

        return (exit_dir, pos.move(exit_dir))

    def follow(self, init_dir, start):
        dir = init_dir
        dest = start.move(init_dir)
        yield dest
        while t := self.enter(dir, dest):
            dir, dest = t
            yield dest

    def a(self):
        a, b = self.dirs
        paths = zip(self.follow(a, self.start), self.follow(b, self.start))
        entries = takewhile(lambda t: not(eq(*t)), paths)
        return 1 + len(list(entries))

    def start_symbol(self):
        s = None
        if self.dirs == {N, S}: s = '|'
        if self.dirs == {E, W}: s = '-'
        if self.dirs == {N, W}: s = 'J'
        if self.dirs == {N, E}: s = 'L'
        if self.dirs == {S, W}: s = '7'
        if self.dirs == {S, E}: s = 'F'
        return s

    def b(self):
        path = {self.start: self.start_symbol()}
        for pos in self.follow(next(iter(self.dirs)), self.start):
            if pos == self.start:
                break
            path[pos] = self[pos]
        width = len(self.lines[0])
        height = len(self.lines)
        return LoopMap(width, height, path).inside_count()

class LoopMap:

    def __init__(self, width, height, path):
        self.grid = [['.' if Pos(x, y) not in path else path[Pos(x, y)] for x in range(width)] for y in range(height)]

    def __getitem__(self, pos):
        return self.grid[pos.y][pos.x]

    def __setitem__(self, pos, value):
        self.grid[pos.y][pos.x] = value

    def count_row_insides(self, row):
        state = []
        count = 0

        def push_pipe():
            if state and state[-1] == '|': state.pop()
            else: state.append('|')

        for c in row:
            if c == '.' and state: count += 1
            if c == '|': push_pipe()
            if c in {'F', 'L'}: state.append(c)
            if c == 'J' and state.pop() == 'F': push_pipe()
            if c == '7' and state.pop() == 'L': push_pipe()

        return count

    def inside_count(self):
        return sum(self.count_row_insides(r) for r in self.grid)

def day10a(lines):
    """
    >>> day10a(TEST_INPUT_1)
    4
    >>> day10a(TEST_INPUT_2)
    8
    """
    return Puzzle(lines).a()


def day10b(lines):
    """
    >>> day10b(TEST_INPUT_3)
    4
    >>> day10b(TEST_INPUT_4)
    8
    >>> day10b(TEST_INPUT_5)
    10
    """
    return Puzzle(lines).b()


def main():
    with open('aoc23/data/day10input.txt') as fd:
        lines = list(fd)
    print(f'Day 10a: {day10a(lines)}')
    print(f'Day 10b: {day10b(lines)}')


if __name__ == '__main__':
    main()
