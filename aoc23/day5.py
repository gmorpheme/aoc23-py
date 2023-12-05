import re
from dataclasses import dataclass
from functools import reduce
from itertools import batched, chain, count

TEST_INPUT = [
    'seeds: 79 14 55 13',
    '',
    'seed-to-soil map:',
    '50 98 2',
    '52 50 48',
    '',
    'soil-to-fertilizer map:',
    '0 15 37',
    '37 52 2',
    '39 0 15',
    '',
    'fertilizer-to-water map:',
    '49 53 8',
    '0 11 42',
    '42 0 7',
    '57 7 4',
    '',
    'water-to-light map:',
    '88 18 7',
    '18 25 70',
    '',
    'light-to-temperature map:',
    '45 77 23',
    '81 45 19',
    '68 64 13',
    '',
    'temperature-to-humidity map:',
    '0 69 1',
    '1 0 69',
    '',
    'humidity-to-location map:',
    '60 56 37',
    '56 93 4    ',
]


def range_overlap(x, y):
    return range(max(x.start, y.start), min(x.stop, y.stop))


class RangePerturbation:

    """
    >>> RangePerturbation(0, 70, 3).range_impacts(range(2, 4))
    ([range(3, 4)], [range(72, 73)])
    """

    def __init__(self, fr, to, n):
        self.range = range(fr, fr + n)
        self.perturbation = to - fr

    def __call__(self, v):
        if v in self.range:
            return v + self.perturbation
        else:
            return v

    def applies(self, r):
        return range_overlap(self.range, r)

    def range_impacts(self, r):
        if o := range_overlap(self.range, r):
            unaffected_rs = [
                range
                for range in [
                    range(r.start, max(r.start, o.start)),
                    range(o.stop, max(o.stop, r.stop)),
                ]
                if range
            ]
            perturbed = range(o.start + self.perturbation, o.stop + self.perturbation)
            return (unaffected_rs, [perturbed])
        else:
            return ([r], [])


class RangeMapping:
    def __init__(self, perturbations):
        self.perturbations = perturbations

    def __call__(self, input) -> int:
        """
        >>> RangeMapping(iter(['50 98 2', '52 50 48', '']))(79)
        81
        """
        for p in self.perturbations:
            if input in p.range:
                return p(input)
        else:
            return input

    def apply_to_range(self, r):
        unaffected = [r]
        perturbed = []
        for p in self.perturbations:
            for r in unaffected[:]:
                if p.applies(r):
                    (us, ps) = p.range_impacts(r)
                    perturbed.extend(ps)
                    unaffected.remove(r)
                    unaffected.extend(us)
        return unaffected + perturbed

    def apply_to_ranges(self, ranges):
        return sum(map(lambda r: self.apply_to_range(r), ranges), [])


@dataclass
class PuzzleA:
    seeds: list[int]
    mappings: list[RangeMapping]

    def find_location(self, seed: int) -> int:
        return reduce(lambda x, f: f(x), self.mappings, seed)

    def seed_locations(self):
        return (self.find_location(s) for s in self.seeds)


@dataclass
class PuzzleB:
    seed_ranges: list[range]
    mappings: list[RangeMapping]

    def seed_location_ranges(self):
        return reduce(
            lambda rs, m: m.apply_to_ranges(rs), self.mappings, self.seed_ranges
        )


def parse_mapping(line_iter) -> RangeMapping:
    perturbations = []
    for line in line_iter:
        if line.strip():
            (to, fr, n) = map(int, line.split())
            perturbations.append(RangePerturbation(fr, to, n))
        else:
            break
    return RangeMapping(perturbations)


def parse_mappings(line_iter) -> list[RangeMapping]:
    mappings = []
    try:
        while True:
            next(line_iter)  # title
            mappings.append(parse_mapping(line_iter))
    except StopIteration:
        pass

    return mappings


seeds_re = re.compile(r'seeds: (.*)')


def parse_seeds(line_iter) -> list[int]:
    if m := seeds_re.match(next(line_iter)):
        return list(map(int, m.group(1).split()))
    else:
        return []


def parse_seed_ranges(line_iter) -> list[range]:
    if m := seeds_re.match(next(line_iter)):
        return list(
            map(
                lambda p: range(p[0], p[0] + p[1]),
                iter(batched(map(int, m.group(1).split()), 2)),
            )
        )
    else:
        return []


def parse_puzzle_a(lines):
    it = iter(lines)
    seeds = parse_seeds(it)
    next(it)
    mappings = parse_mappings(it)
    return PuzzleA(seeds, mappings)


def parse_puzzle_b(lines):
    it = iter(lines)
    seed_ranges = parse_seed_ranges(it)
    next(it)
    mappings = parse_mappings(it)
    return PuzzleB(seed_ranges, mappings)


def day5a(lines):
    """
    >>> day5a(TEST_INPUT)
    35
    """
    return min(parse_puzzle_a(lines).seed_locations())


def day5b(lines):
    """
    >>> day5b(TEST_INPUT)
    46
    """
    return min(map(lambda x: x.start, parse_puzzle_b(lines).seed_location_ranges()))


def main():
    with open('aoc23/data/day5input.txt') as f:
        lines = list(f)
    print(f'Day 5a: {day5a(lines)}')
    print(f'Day 5b: {day5b(lines)}')


if __name__ == '__main__':
    main()
