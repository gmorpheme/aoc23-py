from typing import NamedTuple
from enum import Enum
from functools import reduce
import hashlib
from collections import defaultdict
from dataclasses import dataclass

TEST_INPUT = [
    '...........',
    '.....###.#.',
    '.###.##..#.',
    '..#.#...#..',
    '....#.#....',
    '.##..S####.',
    '.##..#...#.',
    '.......##..',
    '.##.#.####.',
    '.##..##.##.',
    '...........',
]

class Pos(NamedTuple):
    x: int
    y: int

    def move(self, d):
        return Pos(self.x + d.value[0], self.y + d.value[1])

class Dir(Enum):
    N = (0, -1)
    S = (0, +1)
    E = (+1, 0)
    W = (-1, 0)

class Plan:

    def __init__(self, lines, bounded = True, start = None):
        self.bounded = bounded
        self.rows = [list(line.strip()) for line in lines]
        self.width = len(self.rows[0])
        self.height = len(self.rows)
        self.end = Pos(self.width - 1, self.height - 1)
        for y, row in enumerate(self.rows):
            for x, c in enumerate(row):
                if c == 'S':
                    self.start = Pos(x, y)
        self[self.start] = '.'
        self.start = start or self.start
        self.blank = self.subgrid_hash(Pos(0, 0), set())

    def __getitem__(self, pos):
        x, y = pos
        if self.bounded:
            return self.rows[y][x]
        else:
            return self.rows[y % self.height][x % self.width]

    def __setitem__(self, pos, c):
        x, y = pos
        if self.bounded:
            self.rows[y][x] = c
        else:
            self.rows[y % self.height][x % self.width] = c

    def subgrids(self, accessible):
        for y in range(min(p.y for p in accessible) // self.height - 1, max(p.y for p in accessible) // self.height + 2):
            for x in range(min(p.x for p in accessible) // self.width - 1, max(p.x for p in accessible) // self.width + 2):
                yield (x, y)

    def subgrid_hash(self, coord, accessible):
        m = hashlib.sha1()
        x, y = coord
        for yy in range(y * self.height, (y + 1) * self.height):
            for xx in range(x * self.width, (x + 1) * (self.width)):
                if Pos(xx, yy) in accessible:
                    m.update(b'O')
                else:
                    m.update(b'-')
        return m.digest()

    def dump(self, frontier):
        y_positions = range(self.height) if self.bounded else range(-self.height - 1, self.height + 1)
        for y in y_positions:
            x_positions = (Pos(x, y) for x in (range(self.width) if self.bounded else range(-self.width - 1, self.width + 1)))
            print(''.join('O' if p in frontier else 'S' if p == self.start else self[p] for p in x_positions))

    def in_bounds(self, pos):
        return self.bounded == False or (0<= pos.x < self.width and 0<= pos.y < self.height)

    def accessible_neighbours(self, pos):
        return set(p for p in [pos.move(d) for d in Dir] if self.in_bounds(p) and self[p] == '.')

    def step(self, n):
        accessible = {self.start}
        for i in range(1, n+1):
            accessible = reduce(lambda a, b: a.union(b), [self.accessible_neighbours(f) for f in accessible])
        return accessible

    def step_counts(self, n):
        accessible = {self.start}
        for i in range(1, n+1):
            accessible = reduce(lambda a, b: a.union(b), [self.accessible_neighbours(f) for f in accessible])
            yield len(accessible)

    def step_outward(self, n):
        last_frontier = set()
        frontier = {self.start}
        count = 1
        prior_count = 0
        yield count
        for i in range(1, n+1):
            last_frontier, frontier = frontier, reduce(lambda a, b: a.union(b), [self.accessible_neighbours(f) for f in frontier], set()) - last_frontier
            frontier_size = len(frontier)
            # print(f'{i:16}: {prior_count} + {frontier_size}')
            prior_count, count = count, (prior_count + frontier_size)
            # print(f'{i:16}:     -> {count}')
            yield count

def count_at_age(counts, n):
    if n >= len(counts):
        if n % 2 == 1:
            return counts[-2]
        else:
            return counts[-1]
    else:
        return counts[n-1]

class Solver:

    def __init__(self, lines):
        self.plan_centre = Plan(lines)
        self.w = self.plan_centre.width
        self.h = self.plan_centre.height
        self.plan_s = Plan(lines, start = Pos(self.plan_centre.start.x, 0))
        self.plan_sw = Plan(lines, start = Pos(self.plan_centre.width - 1, 0))
        self.plan_w = Plan(lines, start = Pos(self.plan_centre.width - 1, self.plan_centre.start.y))
        self.plan_nw = Plan(lines, start = Pos(self.plan_centre.width - 1, self.plan_centre.height - 1))
        self.plan_n = Plan(lines, start = Pos(self.plan_centre.start.x, self.plan_centre.height - 1))
        self.plan_ne = Plan(lines, start = Pos(0, self.plan_centre.height - 1))
        self.plan_e = Plan(lines, start = Pos(0, self.plan_centre.start.y))
        self.plan_se = Plan(lines, start = Pos(0, 0))

        self.counts_centre = list(self.plan_centre.step_outward(self.w))
        self.counts_n = list(self.plan_n.step_outward(self.w + self.h + 1))
        self.counts_ne = list(self.plan_ne.step_outward(self.w + self.h + 1))
        self.counts_e = list(self.plan_e.step_outward(self.w + self.h + 1))
        self.counts_se = list(self.plan_se.step_outward(self.w + self.h + 1))
        self.counts_s = list(self.plan_s.step_outward(self.w + self.h + 1))
        self.counts_sw = list(self.plan_sw.step_outward(self.w + self.h + 1))
        self.counts_w = list(self.plan_w.step_outward(self.w + self.h + 1))
        self.counts_nw = list(self.plan_nw.step_outward(self.w + self.h + 1))


    def solve(self, n):
        wq, wr = divmod(self.plan_centre.start.x + n + 1, self.w)
        axis_blocks = wq + int(wr > 0) - 1

        c_count = count_at_age(self.counts_centre, n+1) #centre has aged 1
        #already at start
        axis_ages = list(a for a in range(wr, wr+(wq*self.w), self.w) if a > 0)[0:axis_blocks+1]
        diag_ages = list(max(a - (self.h // 2) - 1, 0) for a in axis_ages)
        diag_ages = list(reversed([a for a in diag_ages if a > 0]))
        n_count = sum([count_at_age(self.counts_n, i) for i in axis_ages][:axis_blocks])
        s_count = sum([count_at_age(self.counts_s, i) for i in axis_ages][:axis_blocks])
        e_count = sum([count_at_age(self.counts_e, i) for i in axis_ages][:axis_blocks])
        w_count = sum([count_at_age(self.counts_w, i) for i in axis_ages][:axis_blocks])

        diagonal_fringe = len(diag_ages)

        ne_count = sum(count_at_age(self.counts_ne, a) * (n+1) for n, a in enumerate(diag_ages))
        se_count = sum(count_at_age(self.counts_se, a) * (n+1) for n, a in enumerate(diag_ages))
        sw_count = sum(count_at_age(self.counts_sw, a) * (n+1) for n, a in enumerate(diag_ages))
        nw_count = sum(count_at_age(self.counts_nw, a) * (n+1) for n, a in enumerate(diag_ages))
        total = c_count + n_count + s_count + e_count + w_count + ne_count + nw_count + se_count + sw_count

        # print(f'1 pre-aged centre block of age {n+1}: {c_count}')
        # print(f'{axis_blocks} north blocks of ages {axis_ages}: {n_count}')
        # print(f'{axis_blocks} south blocks of ages {axis_ages}: {s_count}')
        # print(f'{axis_blocks} east blocks of ages {axis_ages}: {e_count}')
        # print(f'{axis_blocks} west blocks of ages {axis_ages}: {w_count}')
        # print(f'plus diagonals with fringe {diagonal_fringe} of ages {diag_ages}')
        # print(f'ne {ne_count} ')
        # print(f'se {se_count} ')
        # print(f'nw {nw_count} ')
        # print(f'sw {sw_count} ')
        # print(f'TOTAL: {total}')

        return total


def day21a(lines, n = 64):
    """
    >>> day21a(TEST_INPUT, 6)
    16
    """
    plan = Plan(lines)
    return len(plan.step(n))


def day21b(lines, n = 26501365):

    # Extremely annoying. The general solution which works for the
    # test case is too slow for the real problem.
    #
    # The solutions for the real problem (which actually could be much
    # simpler if I'd made some extra assumptions) doesn't work for the
    # test case....

    # """
    # >>> day21b(TEST_INPUT, 6)
    # 16
    # >>> day21b(TEST_INPUT, 10)
    # 50
    # >>> day21b(TEST_INPUT, 50)
    # 1594
    # >>> day21b(TEST_INPUT, 100)
    # 6536
    # >>> day21b(TEST_INPUT, 500)
    # 167004
    # >>> day21b(TEST_INPUT, 1000)
    # 668697
    # >>> day21b(TEST_INPUT, 5000)
    # 16733044
    # """
    # plan = Plan(lines, bounded = False)
    # return list(plan.step_outward(n))[-1]
    return Solver(lines).solve(n)

def main():
    with open('aoc23/data/day21input.txt') as fd:
        lines = list(fd)
    print(f'Day 21a: {day21a(lines)}')
    print(f'Day 21b: {day21b(lines)}')

if __name__ == '__main__':
    main()
