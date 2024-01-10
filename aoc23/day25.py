from dataclasses import dataclass
from itertools import pairwise
from functools import reduce
from typing import List, Optional

TEST_INPUT = [
    'jqt: rhn xhk nvd',
    'rsh: frs pzl lsr',
    'xhk: hfx',
    'cmg: qnr nvd lhk bvb',
    'rhn: xhk bvb hfx',
    'bvb: xhk hfx',
    'pzl: lsr hfx nvd',
    'qnr: nvd',
    'ntq: jqt hfx bvb xhk',
    'nvd: lhk',
    'lsr: lhk',
    'rzs: qnr cmg lsr rsh',
    'frs: qnr lhk lsr',
]


@dataclass
class G:
    edges: set[tuple[str, str]]
    vertices: set[str]

    def neighbours(self, v):
        return set(d for s, d in self.edges if s == v) | set(s for s, d in self.edges if d == v)

    def without(self, edges):
        es = edges + [(d, s) for s, d in edges]
        return G(self.edges.difference(es), self.vertices)

    @staticmethod
    def parse(lines):
        g = G(set(), set())
        for line in lines:
            source, targets = line.split(':')
            source = source.strip()
            g.vertices.add(source)
            for t in targets.split():
                g.edges.add((source, t.strip()))
        return g

    def bfs_gather(self, v):
        visited = set()
        queue = [v]
        while queue:
            n = queue.pop(0)
            for nn in self.neighbours(n):
                if nn not in visited:
                    visited.add(nn)
                    queue.append(nn)
        return visited

    def bfs_shortest_path_to_furthest_node(self, u) -> Optional[List[str]]:
        visited = set()
        queue = [[u]]
        last_path = None
        while queue:
            path = queue.pop(0)
            last_path = path
            neighbours = self.neighbours(path[-1])
            for nn in neighbours:
                if nn not in visited:
                    visited.add(nn)
                    queue.append(path + [nn])
        return last_path

    def bfs_next_augmenting_path_to(self, u: str, dest, used_paths) -> Optional[List[str]]:
        visited = set()
        queue = [[u]]
        out_of_bounds = reduce(lambda a, e: a.union(e), (set(p) for p in used_paths)).difference({dest})
        while queue:
            path = queue.pop(0)
            if path[-1] == dest:
                return path
            neighbours = [o for o in self.neighbours(path[-1]) if o not in out_of_bounds]
            for nn in neighbours:
                if nn not in visited:
                    visited.add(nn)
                    queue.append(path + [nn])


    def components(self):
        vs = set(self.vertices)
        cs = []
        while vs:
            n = next(iter(vs))
            component = self.bfs_gather(n)
            cs.append(component)
            vs.difference_update(component)
        return cs


def day25a(lines):
    """
    >>> day25a(TEST_INPUT)
    54
    """
    g = G.parse(lines)

    # Use variation on max-flow min-cut... repeated bfs to find
    # shortest path to end which doesn't use nodes already at
    # capacity. If capacity is just one, the min-flow aspect
    # identifies three paths which will block remaining flow at some
    # point. So there is a cut of each path at one point which will
    # partition the graph. We then find it by testing which
    # combinations of links from each path will do it.
    #
    # To find a 'source' and 'sink', pick a random node and the
    # furthest other node from it. This might be a bad choice but
    # works first time on the problem data.

    path_1 = g.bfs_shortest_path_to_furthest_node(next(iter(g.vertices)))
    assert path_1
    start, end = path_1[0], path_1[-1]
    path_2 = g.bfs_next_augmenting_path_to(start, end, [path_1])
    path_3 = g.bfs_next_augmenting_path_to(start, end, [path_1, path_2])

    assert path_2
    assert path_3
    assert g.bfs_next_augmenting_path_to(start, end, [path_1, path_2, path_3]) == None

    solution = []
    for edge in pairwise(path_3):
        augmenting_path = g.without([tuple(edge)]).bfs_next_augmenting_path_to(start, end, [path_1, path_2])
        if augmenting_path == None:
            solution.append(edge)
            break

    for edge in pairwise(path_2):
        augmenting_path = g.without([tuple(edge)]).bfs_next_augmenting_path_to(start, end, [path_1, path_3])
        if augmenting_path == None:
            solution.append(edge)
            break

    for edge in pairwise(path_1):
        augmenting_path = g.without([tuple(edge)]).bfs_next_augmenting_path_to(start, end, [path_2, path_3])
        if augmenting_path == None:
            solution.append(edge)
            break

    a, b = [len(c) for c in g.without(solution).components()]

    return a * b

def main():
    with open('aoc23/data/day25input.txt') as fd:
        lines = list(fd)
    print(f'Day 25a: {day25a(lines)}')

if __name__ == '__main__':
    main()
