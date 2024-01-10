from typing import NamedTuple, Mapping
from dataclasses import dataclass
from graphlib import TopologicalSorter
from collections import defaultdict

TEST_INPUT = [
    '1,0,1~1,2,1',
    '0,0,2~2,0,2',
    '0,2,3~2,2,3',
    '0,0,4~0,2,4',
    '2,0,5~2,2,5',
    '0,1,6~2,1,6',
    '1,1,8~1,1,9',
]

class Pos(NamedTuple):
    x: int
    y: int
    z: int

@dataclass
class Brick:
    id: int
    start: Pos
    end: Pos

    @property
    def min_z(self):
        return min(self.start.z, self.end.z)

    @property
    def max_z(self):
        return max(self.start.z, self.end.z)

    @property
    def height(self):
        return self.max_z - self.min_z + 1

    def xy_intersects(self, other):
        o_l = min(other.start.x, other.end.x)
        o_r = max(other.start.x, other.end.x)
        s_l = min(self.start.x, self.end.x)
        s_r = max(self.start.x, self.end.x)
        o_u = min(other.start.y, other.end.y)
        o_d = max(other.start.y, other.end.y)
        s_u = min(self.start.y, self.end.y)
        s_d = max(self.start.y, self.end.y)
        return ((o_l <= s_l <= o_r) or (s_l <= o_l <= s_r)) and ((o_u <= s_u <= o_d) or (s_u <= o_u <= s_d))

    def in_layer(self, z):
        return self.min_z <= z <= self.max_z

    def to_layer(self, z):
        drop = self.min_z - z
        self.start = Pos(self.start.x, self.start.y, self.start.z - drop)
        self.end = Pos(self.end.x, self.end.y, self.end.z - drop)

    @staticmethod
    def parse(i, line):
        start, end = line.strip().split('~')
        id = i
        start = Pos(*(int(i) for i in start.split(',')))
        end = Pos(*(int(i) for i in end.split(',')))
        return Brick(id, start, end)

def condense(bricks):
    # bricks are lying flat
    bricks.sort(key = lambda b: b.min_z)
    max_z = max(b.max_z for b in bricks)
    for layer in range(1, max_z + 1):
        current = [b for b in bricks if b.in_layer(layer)]

        ceiling = []
        for pending_layer in range(layer+1, max_z+1):
            ceiling = [b for b in bricks if b.min_z == pending_layer]
            if ceiling:
                break

        for cb in ceiling:
            for supporting_layer in range(layer, 0, -1):
                supports = [b for b in bricks if b.in_layer(supporting_layer)]
                intersecting_bricks = [b for b in supports if cb.xy_intersects(b)]
                if intersecting_bricks:
                    blocked_to_layer = max(b.max_z for b in intersecting_bricks)
                    cb.to_layer(blocked_to_layer + 1)
                    break
                else:
                    cb.to_layer(supporting_layer)

    return bricks

def number_of_supports(s, bricks):
    return len([t for t in bricks if t.in_layer(s.min_z - 1) and t.xy_intersects(s)])

def unburdened(bricks):

    count_unburdened = 0
    for b in bricks:
        supported_bricks = (u for u in bricks if u.in_layer(b.max_z + 1) and u.xy_intersects(b))
        supporting = any(s for s in supported_bricks if number_of_supports(s, bricks) == 1)
        if not supporting:
            count_unburdened += 1

    return count_unburdened


@dataclass
class BrickNode:
    id: int
    supporters: list[int]
    supporteds: list[int]
    path_matrix: Mapping[tuple[int, int], int]
    tags: set

def to_nodes(condensed_bricks):
    nodes = []
    for b in condensed_bricks:
        supporters = [s.id for s in condensed_bricks if s.in_layer(b.min_z - 1) and s.xy_intersects(b)]
        supporteds = [s.id for s in condensed_bricks if s.in_layer(b.max_z + 1) and s.xy_intersects(b)]
        nodes.append(BrickNode(b.id, supporters, supporteds, {}, set()))
    return sorted(nodes, key = lambda n: n.id)

def tag_dependents(i, nodes):

    """BFS to tag reachable nodes from a base brick."""

    queue = [nodes[i]]
    while queue:
        node = queue.pop()
        if node.id == i or all(i in nodes[s].tags for s in node.supporters):
            node.tags.add(i)
            for s in node.supporteds:
                queue.append(nodes[s])
    if i in nodes[i].tags:
        nodes[i].tags.remove(i)

def direct(nodes):

    """This replaces one hundred lines of complex graph-theoretic
    nonsense. Sometimes, even in AoC, the easy thing works."""

    for i in range(0, len(nodes)):
        tag_dependents(i, nodes)
    counts = list(sum(1 for n in nodes if i in n.tags) for i in range(0, len(nodes)))
    return counts

def day22a(lines):
    """
    >>> day22a(lines)
    5
    """
    return unburdened(condense([Brick.parse(i, line) for i, line in enumerate(lines)]))

def day22b(lines, n = 26501365):
    """
    >>> day22b(lines)
    7
    """
    return sum(direct(to_nodes(condense([Brick.parse(i, line) for i, line in enumerate(lines)]))))

def main():
    with open('aoc23/data/day22input.txt') as fd:
        lines = list(fd)
    print(f'Day 22a: {day22a(lines)}')
    print(f'Day 22b: {day22b(lines)}')

if __name__ == '__main__':
    main()
