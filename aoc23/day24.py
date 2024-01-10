from dataclasses import dataclass
from typing import NamedTuple, Optional
from itertools import combinations, groupby
import math

TEST_INPUT = [
    '19, 13, 30 @ -2,  1, -2',
    '18, 19, 22 @ -1, -1, -2',
    '20, 25, 34 @ -2, -2, -4',
    '12, 31, 28 @ -1, -2, -1',
    '20, 19, 15 @  1, -5, -3',
]


class Vector3(NamedTuple):
    x: int | float
    y: int | float
    z: int | float

    def dot(self, other):
        return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)

    def cross(self, other):
        return Vector3(self.y * other.z - self.z * other.y,
                       self.z * other.x - self.x * other.z,
                       self.x * other.y - self.y * other.x)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def in_bounds_xy(self, min_bound, max_bound):
        return min_bound <= self.x <= max_bound and min_bound <= self.y <= max_bound


@dataclass
class Trajectory:

    p0: Vector3
    v: Vector3

    def t_of(self, pos):
        return (pos.x - self.p0.x) / self.v.x

    def at(self, t):
        return Vector3(self.p0.x + t*self.v.x, self.p0.y + t*self.v.y, self.p0.z + t * self.v.z)

    def path_equation(self):
        # x-component, y-component, = r
        return [self.v.y, -self.v.x, self.v.y * self.p0.x - self.v.x * self.p0.y]

    def in_future(self, pos):
        return self.t_of(pos) > 0

    def gradient(self):
        norm = math.hypot(*self.v)
        return Vector3(self.v.x / norm, self.v.y / norm, self.v.z / norm)

    def xy_gradient(self):
        norm = math.hypot(*self.v)
        return Vector3(self.v.x / norm, self.v.y / norm, self.v.z / norm)

    def xyz_intersects(self, other):
        xy_isec = solve_xy(self, other)
        if xy_isec:
            self_z = self.p0.z + (((xy_isec.x - self.p0.x) / self.v.x) * self.v.z)
            other_z = other.p0.z + (((xy_isec.x - other.p0.x) / other.v.x) * other.v.z)
            return self_z == other_z
        else:
            return False

    @staticmethod
    def parse(line):
        p, v = line.split('@')
        pos = Vector3(*(int(c.strip()) for c in p.split(',')))
        vel = Vector3(*(int(c.strip()) for c in v.split(',')))
        return Trajectory(pos, vel)

def solve_xy(a: Trajectory, b: Trajectory):

    # parametric
    [A11, A12, B1] = a.path_equation()
    [A21, A22, B2] = b.path_equation()

    # invert A
    determinant = (A11 * A22) - (A12 * A21)
    if determinant == 0:
        return None
    c = (1/determinant)

    Ainv1 = [c * A22, -c * A12]
    Ainv2 = [-c * A21, c * A11]

    C1 = (Ainv1[0] * B1) + (Ainv1[1] * B2)
    C2 = (Ainv2[0] * B1) + (Ainv2[1] * B2)

    result = Vector3(C1, C2, 0)

    if a.in_future(result) and b.in_future(result):
        return Vector3(C1, C2, 0)

def day24a(lines, min_bound = 200000000000000, max_bound = 400000000000000):
    """
    >>> day24a(TEST_INPUT, min_bound = 7, max_bound = 27)
    2
    """
    trajectories = [Trajectory.parse(line) for line in lines]
    solutions = (solve_xy(a, b) for (a, b) in combinations(trajectories, 2) if a is not b)
    return len(list(s for s in solutions if s is not None and s.in_bounds_xy(min_bound, max_bound)))

def day24b(lines):
    """
    >>> day24b(TEST_INPUT)
    """
    trajectories = [Trajectory.parse(line) for line in lines]

    # cheat! in the data there are two stones that are identical on
    # the x axis... find them and any two other stones
    a1: Optional[Trajectory] = None
    a2: Optional[Trajectory] = None
    c: Optional[Trajectory] = None
    d: Optional[Trajectory] = None
    for (a, b) in combinations(trajectories, 2):
        if a.p0.x == b.p0.x and a.v.x == b.v.x:
            a1 = a
            a2 = b
        if a1:
            if a.p0.x != a1.p0.x and b.p0.x != a1.p0.x:
                c = a
                d = b
                break

    assert a1
    assert a2
    assert c
    assert d

    # So we know our projectiles starting x and x velocity
    x0, dx = a1.p0.x, a1.v.x

    # Work out when it has to hit stones c and d
    tc = (c.p0.x - x0) / (dx - c.v.x)
    td = (d.p0.x - x0) / (dx - d.v.x)

    # Calculate the y and z values to travel between stones c and d at
    # times tc and td
    dy = (d.at(td).y - c.at(tc).y) / (td - tc)
    dz = (d.at(td).z - c.at(tc).z) / (td - tc)
    y0 = (d.at(td).y - (td * dy))
    z0 = (d.at(td).z - (td * dz))

    # Validate the solution
    solution = Trajectory(Vector3(x0, y0, z0), Vector3(dx, dy, dz))
    assert solution.at(tc) == c.at(tc)
    assert solution.at(td) == d.at(td)

    return x0 + y0 + z0

def main():
    with open('aoc23/data/day24input.txt') as fd:
        lines = list(fd)
    print(f'Day 24a: {day24a(lines)}')
    print(f'Day 24b: {day24b(lines)}')

if __name__ == '__main__':
    main()
