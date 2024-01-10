from typing import NamedTuple, Mapping
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
import heapq
from itertools import pairwise
from aoc23.day22 import Pos

TEST_INPUT = [
    '#.#####################',
    '#.......#########...###',
    '#######.#########.#.###',
    '###.....#.>.>.###.#.###',
    '###v#####.#v#.###.#.###',
    '###.>...#.#.#.....#...#',
    '###v###.#.#.#########.#',
    '###...#.#.#.......#...#',
    '#####.#.#.#######.#.###',
    '#.....#.#.#.......#...#',
    '#.#####.#.#.#########v#',
    '#.#...#...#...###...>.#',
    '#.#.#v#######v###.###v#',
    '#...#.>.#...>.>.#.###.#',
    '#####v#.#.###v#.#.###.#',
    '#.....#...#...#.#.#...#',
    '#.#########.###.#.#.###',
    '#...###...#...#...#.###',
    '###.###.#.###v#####v###',
    '#...#...#.#.>.>.#.>.###',
    '#.###.###.#.###.#.#v###',
    '#.....###...###...#...#',
    '#####################.#',
]

class Dir(Enum):
    E = (+1, 0)
    S = (0, +1)
    W = (-1, 0)
    N = (0, -1)

    @staticmethod
    def of(ch):
        return list(Dir)['>v<^'.index(ch)]

class Plan:

    def __init__(self, lines):
        self.rows = [list(line.strip()) for line in lines]
        self.width = len(self.rows[0])
        self.height = len(self.rows)
        self.start = [(x, 0) for x in range(0, self.width) if self[x, 0] == '.'][0]
        self.end = [(x, self.height-1) for x in range(0, self.width) if self[x, self.height-1] == '.'][0]

    def __getitem__(self, pos):
        x, y = pos
        return self.rows[y][x]

    @cached_property
    def walls(self):
        return sum(sum(1 for c in row if c == '#') for row in self.rows)

    @cached_property
    def dots(self):
        return sum(sum(1 for c in row if c == '.') for row in self.rows)

    def dots_inaccessible(self, path):
        # blocked_y = 1
        # for y in range(path[-1][1], 0, -1):
        #     if all(self[x, y] == '#' or (x, y) in path for x in range(0, self.width)):
        #         blocked_y = y

        # missed_dots = 0
        # for y in range(blocked_y - 1, 0, -1):
        #     missed_dots += sum(int(self[x, y] == '.' and (x, y) not in path) for x in range(0, self.width))

        # missed_dots = 0
        # for y in range(0, self.height):
        #     for x in range(0, self.width):
        #         if self[x, y] == '.' and self.path_adjacent((x, y), path):
        #             missed_dots += 1

        blocked_radius = 1
        for r in range(1, path[-1][0]):
            border = [(x, r) for x in range(0, r)] + [(r, y) for y in range(0, r)]
            if all(self[pos] == '#' or pos in path for pos in border):
                blocked_radius = r

        missed_dots = 0
        for y in range(blocked_radius - 1, 0, -1):
            missed_dots += sum(int(self[x, y] == '.' and (x, y) not in path) for x in range(0, blocked_radius))

        return missed_dots

    def path_adjacent(self, pos, path):
        return pos != path and any(self.move(pos, d) in path[:-1] for d in self.options(pos))

    def options(self, pos):
        x, y = pos
        return [d for d in Dir if (0 <= x + d.value[0] < self.width) and (0<= y + d.value[1] < self.width) and self[(x + d.value[0], y + d.value[1])] != '#']

    def move(self, pos, d):
        x, y = pos
        dx, dy = d.value
        x1, y1 = x + dx, y + dy
        n = self[x1, y1]
        if n == '.':
            return [(x1, y1)]
        elif n in {'>', '<', '^', 'v'}:
            return [(x1, y1)] + self.move((x1, y1), Dir.of(n))
        else:
            return []

    def move_b(self, pos, d):
        x, y = pos
        dx, dy = d.value
        x1, y1 = x + dx, y + dy
        n = self[x1, y1]
        if n != '#':
            return [(x1, y1)]
        else:
            return []

def bfs(plan):
    queue = [[plan.start]]
    while queue:
        path = queue.pop()
        if path[-1] == plan.end:
            yield path
        else:
            for d in plan.options(path[-1]):
                extension = plan.move(path[-1], d)
                if extension and extension[-1] not in path:
                    queue.append(path + extension)

@dataclass
class Connection:

    """A connection between junctions. Non-junctions are irrelevant to the search."""

    source: Pos
    target: Pos
    distance: int

    def reversed(self):
        return Connection(self. target, self.source, self.distance)

def extract_connections(plan: Plan):

    """Represent the problem as network of connections between
    junctions to eliminate any computation associated with single
    square moves."""

    path = [plan.start]
    connections = {}

    def explore(path, start):
        start = start or path[-1]
        path = path[:]
        steps = 0
        while extensions := [ext for ext in [plan.move_b(path[-1], d) for d in plan.options(path[-1])] if ext[-1] not in path]:
            if len(extensions) == 1:
                path += extensions[0]
                steps += 1
                if path[-1] == plan.end:
                    connections[(start, path[-1])] = Connection(start, path[-1], steps)
                    return
            else:
                if (start, path[-1]) not in connections:
                    connections[(start, path[-1])] = Connection(start, path[-1], steps)
                    for ext in extensions:
                        explore(path + ext, path[-1])
                return

    explore(path, None)
    for (s, e) in list(connections.keys()):
        connections[(e, s)] = connections[(s, e)].reversed()
    return connections


def dfs_connections(plan, conns):

    """Yield all possible paths from entry to exit so we can find the longest."""

    stack = [[plan.start]]

    while stack:
        path = stack.pop()
        pos = path[-1]
        if pos == plan.end:
            yield path
        else:
            nexts = [conn for (s, e), conn in conns.items() if s == pos]
            for n in nexts:
                if n.target not in path:
                    stack.append(path + [n.target])

def day23a(lines):
    """
    >>> day23a(TEST_INPUT)
    94
    """
    return max(len(path) - 1 for path in bfs(Plan(lines)))

def day23b(lines, show_progress=False):
    """
    >>> day23b(TEST_INPUT)
    154
    """
    # another slow one, but does terminate eventually...

    max_so_far = 0
    plan = Plan(lines)
    conns = extract_connections(plan)
    for path in dfs_connections(plan, conns):
        length = sum(conns[k].distance + 1 for k in  pairwise(path)) - 1
        if length > max_so_far:
            max_so_far = length
            if show_progress:
                print(f'best: {max_so_far}')
    return max_so_far

def main():
    with open('aoc23/data/day23input.txt') as fd:
        lines = list(fd)
    print(f'Day 23a: {day23a(lines)}')
    print(f'Day 23b: {day23b(lines)}')

if __name__ == '__main__':
    main()
