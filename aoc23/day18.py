import re
from typing import NamedTuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
from functools import cached_property
from itertools import pairwise


TEST_INPUT = [
    'R 6 (#70c710)',
    'D 5 (#0dc571)',
    'L 2 (#5713f0)',
    'D 2 (#d2c081)',
    'R 2 (#59c680)',
    'D 2 (#411b91)',
    'L 5 (#8ceee2)',
    'U 2 (#caa173)',
    'L 1 (#1b58a2)',
    'U 2 (#caa171)',
    'R 2 (#7807d2)',
    'U 3 (#a77fa3)',
    'L 2 (#015232)',
    'U 2 (#7a21e3)',
]


class Pos(NamedTuple):
    x: int
    y: int


class Dir(Enum):
    R = (+1, 0)
    D = (0, +1)
    L = (-1, 0)
    U = (0, -1)

    def reflect(self):
        dx, dy = self.value
        return Dir((-dx, -dy))


step_re = re.compile(r'(R|D|L|U) (\d+) .*')
step_b_re = re.compile(r'(?:R|D|L|U) (?:\d+) \(#([0-9a-f]{5})([0-3])\)')


class Step(NamedTuple):
    d: Dir
    n: int

    @staticmethod
    def parse(line):
        d, n = step_re.match(line).groups()
        return Step(Dir[d], int(n))

    @staticmethod
    def parse_b(line):
        n, d = step_b_re.match(line).groups()
        return Step(list(iter(Dir))[int(d)], int(n, 16))


class Path(NamedTuple):
    start: Pos
    end: Pos

    @staticmethod
    def from_step(pos, step):
        dx, dy = step.d.value
        end = Pos(pos.x + step.n * dx, pos.y + step.n * dy)
        return Path(pos, end)

    def orientation(self):
        if self.start.x == self.end.x:
            if self.start.y > self.end.y:
                return Dir.U
            else:
                return Dir.D
        else:
            if self.start.x > self.end.x:
                return Dir.L
            else:
                return Dir.R

    def intersects(self, other):
        o_l = min(other.start.x, other.end.x)
        o_r = max(other.start.x, other.end.x)
        s_l = min(self.start.x, self.end.x)
        s_r = max(self.start.x, self.end.x)
        o_u = min(other.start.y, other.end.y)
        o_d = max(other.start.y, other.end.y)
        s_u = min(self.start.y, self.end.y)
        s_d = max(self.start.y, self.end.y)
        if ((o_l <= s_l <= o_r) or (s_l <= o_l <= s_r)) and (
            (o_u <= s_u <= o_d) or (s_u <= o_u <= s_d)
        ):
            return Path(
                Pos(max(o_l, s_l), max(o_u, s_u)), Pos(min(o_r, s_r), min(o_d, s_d))
            )


@dataclass
class DigPlan:
    steps: list[tuple]

    def dig(self):
        pos = Pos(0, 0)
        paths = []
        for step in self.steps:
            path = Path.from_step(pos, step)
            paths.append(path)
            pos = path.end
        return DigPaths(paths)

    @classmethod
    def parse(cls, lines):
        return DigPlan([Step.parse(line.strip()) for line in lines])

    @classmethod
    def parse_b(cls, lines):
        return DigPlan([Step.parse_b(line.strip()) for line in lines])


@dataclass
class DigPaths:
    paths: list[Path]

    @cached_property
    def bounds(self):
        cs = self.corners.keys()
        x_min = min(pos.x for pos in cs)
        x_max = max(pos.x for pos in cs)
        y_min = min(pos.y for pos in cs)
        y_max = max(pos.y for pos in cs)
        return (x_min, y_min, x_max, y_max)

    def intersections(self, path):
        return filter(lambda x: x is not None, [p.intersects(path) for p in self.paths])

    @cached_property
    def corners(self):
        corners = defaultdict(set)
        for path in self.paths:
            corners[path.start].add(path.orientation())
            corners[path.end].add(path.orientation().reflect())
        return corners

    def raycast_interior(self):
        x_min, y_min, x_max, y_max = self.bounds
        interior_size = 0

        # only consider rows we need to measure
        rows_of_interest = set(c.y for c in self.corners)
        rows_of_interest |= set(map(lambda x: x + 1, rows_of_interest))
        rows_of_interest = sorted(rows_of_interest)
        run_lengths = list((j - i) for (i, j) in pairwise(rows_of_interest))
        calculation_plan = list(zip(run_lengths, rows_of_interest))

        for rpt, ray_y in calculation_plan:
            ray = Path(Pos(x_min, ray_y), Pos(x_max, ray_y))
            intersection_ends = sum(([p.start, p.end] for p in self.intersections(ray)), [])
            ray_hits = set(pos for pos in intersection_ends if pos.y == ray_y)
            ray_corners_classified = sorted(
                [(c, self.corners[c]) for c in ray_hits],
                key=lambda c: c[0].x,
            )
            interior_size += rpt * count_interior(ray_corners_classified)
        return interior_size


def count_interior(ray_corners_classified):
    OUT, IN = 'o', 'i'
    state = [(Pos(0, 0), OUT)]
    count = 0

    for corner, corner_type in ray_corners_classified:
        # joining path of horizontal wall
        if corner_type & {Dir.R}:
            state.append((corner, corner_type))

        # leaving path of horizontal wall
        elif corner_type & {Dir.L}:
            wall_start_corner, wall_start_type = state.pop()
            region_start, region_type = state[-1]
            if corner_type & wall_start_type:  # u-turn wall
                if region_type == OUT:
                    # wall impinging on exterior, count wall
                    count += (corner.x - wall_start_corner.x) + 1
            else:  # transition wall
                if region_type == OUT:
                    # heading inside, count wall
                    count += (corner.x - wall_start_corner.x) + 1
                    state[-1] = (corner, IN)
                elif region_type == IN:
                    # heading outside count wall and interior
                    count += corner.x - region_start.x
                    state[-1] = (corner, OUT)

        # crossing wall at right angles
        else:
            region_start, region_type = state[-1]
            if region_type == IN:
                # heading outside, count wall and interior
                state[-1] = (corner, OUT)
                count += corner.x - region_start.x
            else:
                # heading inside, count wall
                state[-1] = (corner, IN)
                count += 1

    return count


def day18a(lines):
    """
    >>> day18a(TEST_INPUT)
    62
    """
    return DigPlan.parse(lines).dig().raycast_interior()


def day18b(lines):
    """
    >>> day18b(TEST_INPUT)
    952408144115
    """
    return DigPlan.parse_b(lines).dig().raycast_interior()


def main():
    with open('aoc23/data/day18input.txt') as fd:
        lines = list(fd)
    print(f'Day 18a: {day18a(lines)}')
    print(f'Day 18b: {day18b(lines)}')


if __name__ == '__main__':
    main()
