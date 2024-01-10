import heapq, functools
from typing import NamedTuple
from enum import Enum
from dataclasses import dataclass
from itertools import count

TEST_INPUT = [
    '2413432311323',
    '3215453535623',
    '3255245654254',
    '3446585845452',
    '4546657867536',
    '1438598798454',
    '4457876987766',
    '3637877979653',
    '4654967986887',
    '4564679986453',
    '1224686865563',
    '2546548887735',
    '4322674655533',
]

class Pos(NamedTuple):
    x: int
    y: int

    def move_n(self, m):
        d, n = m
        dx, dy = d.value
        return Pos(self.x + n * dx, self.y + n * dy)

class Dir(Enum):
    N = (0, -1)
    S = (0, +1)
    E = (+1, 0)
    W = (-1, 0)

    def reverse(self):
        x, y = self.value
        return Dir((-x, -y))

    def __repr__(self):
        return self.name

class Move(NamedTuple):
    direction: Dir
    count: int

    def with_intermediates(self):
        return [Move(self.direction, n) for n in range(1,self.count + 1)]

    def __repr__(self):
        return f'{self.direction.name}({self.count})'

class Plan:

    def __init__(self, lines):
        self.rows = [list(map(int, list(line.strip()))) for line in lines]
        self.width = len(self.rows[0])
        self.height = len(self.rows)
        self.end = Pos(self.width - 1, self.height - 1)

    def __getitem__(self, pos):
        x, y = pos
        return self.rows[y][x]

    def in_bounds(self, pos):
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def a_star(self, min_travel=1, max_travel=3, show_progress=False):
        route0 = Route.blank(self)
        frontier = route0.options(Pos(0,0), min_travel=min_travel, max_travel=max_travel)
        heapq.heapify(frontier)
        seen = {}
        for n in count(start=1):
            route = heapq.heappop(frontier)
            if show_progress and n % 10000 == 0:
                print(f'Frontier size: {len(frontier)}')
                print(f'Best: {route.estimated_cost}')
            if route.pos == self.end:
                return route
            for r in route.options(min_travel=min_travel, max_travel=max_travel):
                if r.key in seen:
                    if seen[r.key] <= r.estimated_cost:
                        continue
                seen[r.key] = r.estimated_cost
                heapq.heappush(frontier, r)

@dataclass
class Route:

    plan: Plan
    sequence: list[Move]
    pos_sequence: list[Pos]
    costs_incurred: list[int]

    @classmethod
    def blank(cls, plan: Plan):
        return Route(plan, [], [], [])

    @functools.cached_property
    def pos(self):
        return self.pos_sequence[-1]

    @functools.cached_property
    def path(self):
        return ''.join(repr(s) for s in self.sequence)

    @functools.cached_property
    def heuristic(self):
        x, y = self.pos
        return (self.plan.width - x - 1) + (self.plan.height - y - 1)

    @functools.cached_property
    def estimated_cost(self):
        return self.realised_cost + self.heuristic

    @functools.cached_property
    def realised_cost(self):
        return sum(self.costs_incurred)

    def __lt__(self, other):
        return self.estimated_cost < other.estimated_cost

    @functools.cached_property
    def key(self):
        return (self.sequence[-1].direction, self.pos)

    def options(self, pos = None, min_travel = 1, max_travel = 3):

        start_pos = pos or self.pos
        disallowed = set()
        if self.sequence:
            disallowed.add(self.sequence[-1].direction)
            disallowed.add(self.sequence[-1].direction.reverse())
        directions = [d for d in Dir if d not in disallowed]
        moves = sum(([Move(d, n) for n in range(min_travel, max_travel+1)] for d in directions), [])

        next_routes = []
        for m in moves:
            p = start_pos.move_n(m)
            if self.plan.in_bounds(p):
                cost = sum(self.plan[start_pos.move_n(mm)] for mm in m.with_intermediates())
                next_routes.append(Route(self.plan,
                                          self.sequence + [m],
                                          self.pos_sequence + [p],
                                          self.costs_incurred + [cost]))

        return next_routes

def day17a(lines):
    """
    >>> day17a(TEST_INPUT)
    102
    """
    return Plan(lines).a_star().realised_cost

def day17b(lines):
    """
    >>> day17b(TEST_INPUT)
    94
    """
    return Plan(lines).a_star(min_travel=4, max_travel=10).realised_cost

def main():
    with open('aoc23/data/day17input.txt') as fd:
        lines = list(fd)
    print(f'Day 17a: {day17a(lines)}')
    print(f'Day 17b: {day17b(lines)}')

if __name__ == '__main__':
    main()
