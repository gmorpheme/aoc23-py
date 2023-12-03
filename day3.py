import re
from functools import partial
from operator import mul
from typing import NamedTuple
from collections import defaultdict

TEST_LINES = ["467..114..",
    "...*......",
    "..35..633.",
    "......#...",
    "617*......",
    ".....+.58.",
    "..592.....",
    "......755.",
    "...$.*....",
    ".664.598.."]


class Pos(NamedTuple):
    x: int
    y: int

class Part:

    def __init__(self, row, match):
        self.left = Pos(match.start(0), row)
        self.right = Pos(match.end(0) - 1, row)
        self.value = int(match.group(0))
        upper = set(Pos(x, self.left.y - 1) for x in range(self.left.x - 1, self.right.x + 2))
        lower = set(Pos(x, self.left.y + 1) for x in range(self.left.x - 1, self.right.x + 2))
        sides = {Pos(self.left.x - 1, self.left.y), Pos(self.right.x + 1, self.right. y)}
        self.halo = upper | lower | sides

    def __repr__(self):
        return f'<Part: {self.left}-{self.right}: {self.value}>'

def to_parts(row, line):
    return list(map(partial(Part, row), re.finditer(r'\d+', line)))

class Spigot:

    def __init__(self, row, match):
        self.pos = Pos(match.start(0), row)
        self.value = match.group(0)

    def __repr__(self):
        return f'<Spigot: {self.pos}: {self.value}>'

def to_spigots(row, line):
    return list(map(partial(Spigot, row), re.finditer(r'[^0-9.]', line)))


class Schematic:

    def __init__(self, lines):
        self.parts = sum(list(map(lambda t: to_parts(*t), enumerate(lines))), [])
        self.spigots = sum(list(map(lambda t: to_spigots(*t), enumerate(lines))), [])
        self.spigot_positions = set(s.pos for s in self.spigots)

    def candidate_parts(self):
        return filter(lambda part: part.halo & self.spigot_positions, self.parts)
    
    def identify_geared_pairs(self):
        stars = filter(lambda s: s.value == '*', self.spigots)
        adjacency_map = defaultdict(set)
        for part in self.parts:
            for h in part.halo:
                adjacency_map[h].add((part))
        star_adjencencies = [adjacency_map[star.pos] for star in stars]
        return [pair for pair in star_adjencencies if len(pair) == 2]
    
def day3a(lines):
    """
    >>> day3a(TEST_LINES)
    4361
    """
    return sum(map(lambda p: p.value, Schematic(lines).candidate_parts()))

def day3b(lines):
    """
    >>> day3b(TEST_LINES)
    467835
    """
    return sum(mul(*map(lambda p: p.value, pair)) for pair in Schematic(lines).identify_geared_pairs())


def main():
    lines = list(open('data/day3input.txt'))
    print(f'Day 3a: {day3a(lines)}')
    print(f'Day 3b: {day3b(lines)}')

if __name__ == '__main__':
    main()