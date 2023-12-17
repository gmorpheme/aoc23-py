from enum import IntFlag, auto
from typing import NamedTuple

TEST_INPUT = [
    r'.|...\....',
    r'|.-.\.....',
    r'.....|-...',
    r'........|.',
    r'..........',
    r'.........''\\',
    r'..../.\\..',
    r'.-.-/..|..',
    r'.|....-|.''\\',
    r'..//.|....',
]

class Direction(IntFlag):
    N = auto()
    S = auto()
    E = auto()
    W = auto()

    def exits(self, widget):
        match widget:
            case '.':
                return self
            case '\\':
                match self:
                    case Direction.N: return Direction.W
                    case Direction.S: return Direction.E
                    case Direction.E: return Direction.S
                    case Direction.W: return Direction.N
            case '/':
                match self:
                    case Direction.N: return Direction.E
                    case Direction.S: return Direction.W
                    case Direction.E: return Direction.N
                    case Direction.W: return Direction.S
            case '-':
                match self:
                    case Direction.N: return [Direction.W, Direction.E]
                    case Direction.S: return [Direction.W, Direction.E]
                    case _: return self
            case '|':
                match self:
                    case Direction.E: return [Direction.N, Direction.S]
                    case Direction.W: return [Direction.N, Direction.S]
                    case _: return self
            case _:
                print(self, widget)


    def __str__(self):
        if self ==  Direction(0):
            return '.'
        else:
            n = len(list(self))
            if n == 1:
                return '#'
            else:
                return f'{n}'

class Pos(NamedTuple):
    x: int
    y: int

    def move(self, direction):
        match direction:
            case Direction.N: return Pos(self.x, self.y - 1)
            case Direction.S: return Pos(self.x, self.y + 1)
            case Direction.E: return Pos(self.x + 1, self.y)
            case Direction.W: return Pos(self.x - 1, self.y)

    def in_bounds(self, width, height):
        return (0 <= self.x < width) and (0 <= self.y < height)

class Track:

    def __init__(self, width, height):
        self.track = [[Direction(0)] * width for i in range(height)]
        self.entries = []

    def __getitem__(self, pos):
        x, y = pos
        return self.track[y][x]

    def __setitem__(self, pos, val):
        x, y = pos
        self.track[y][x] = val

    def active_count(self):
        n = 0
        for row in self.track:
            for d in row:
                if d != Direction(0):
                    n += 1
        return n

    def add_entry(self, entry):
        self.entries.append(entry)

    def dump(self):
        for line in self.track:
            print(''.join(str(dir) for dir in line))

def flip_to_entry(pos, direction):
    match direction:
        case Direction.N:
            return (pos.move(Direction.S), Direction.S)
        case Direction.S:
            return (pos.move(Direction.N), Direction.N)
        case Direction.E:
            return (pos.move(Direction.W), Direction.W)
        case Direction.W:
            return (pos.move(Direction.E), Direction.E)

class Puzzle:

    def __init__(self, lines):
        self.lines = [list(line.strip()) for line in lines]
        self.height = len(self.lines)
        self.width = len(self.lines[0])
        self.track = Track(self.width, self.height)

    def __getitem__(self, pos):
        x, y = pos
        return self.lines[y][x]

    def enter(self, pos, direction):
        if not pos.in_bounds(self.width, self.height):
            self.track.add_entry(flip_to_entry(pos, direction))
            return []
        if self.track[pos] & direction: # already followed
            return []
        self.track[pos] |= direction
        return direction.exits(self[pos])

    def reset(self):
        self.track = Track(self.width, self.height)

    def trace(self, start = (Pos(0, 0), Direction.E)):
        todo = [start]
        while todo:
            pos, dir = todo.pop(0)
            todo.extend((pos.move(dir), dir) for dir in self.enter(pos, dir))
        return self.track


def day16a(lines):
    """
    >>> day16a(TEST_INPUT)
    46
    """
    return Puzzle(lines).trace().active_count()


def day16b(lines):
    """
    >>> day16b(TEST_INPUT)
    """
    p = Puzzle(lines)
    tracks = {}

    entries = [(Pos(x, 0), Direction.S) for x in range(p.width)] + \
        [(Pos(x, p.height - 1), Direction.N) for x in range(p.width)] + \
        [(Pos(0, y), Direction.E) for y in range(p.height)] + \
        [(Pos(p.width - 1, y), Direction.W) for y in range(p.height)]

    for e in entries:
        if e not in tracks:
            p.reset()
            p.trace(start = e)
            tracks |= {k: p.track for k in p.track.entries}

    return max(t.active_count() for t in tracks.values())


def main():
    with open('aoc23/data/day16input.txt') as fd:
        lines = list(fd)
        print(len(lines))
    print(f'Day 16a: {day16a(lines)}')
    print(f'Day 16b: {day16b(lines)}')


if __name__ == '__main__':
    main()
