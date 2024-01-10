import re
from functools import reduce
import operator

TEST_INPUT = [
    '???.### 1,1,3',
    '.??..??...?##. 1,1,3',
    '?#?#?#?#?#?#?#? 1,3,1,6',
    '????.#...#... 4,1,1',
    '????.######..#####. 1,6,5',
    '?###???????? 3,2,1',
]

# - Gruesome -
#
# There is an easier way...
#

class Pattern:

    """A regular expression-like pattern matcher to represent the
    placement of hashes represented by counts.

    For instance, the counts 3, 2, 1 are equivalent to the regex
       `.*` `###` `.+` `##` `.+` `#` `.*`.

    (Neither the first nor last chunk need necessarily be anchored to
    the edge, hence the `.*`.)

    Once we're dealing with repeated instances of the pattern (part b)
    sometimes they do need to be anchored because they 'continue' into
    a sequence that is at least partially in the border character
    (represented below by counts (3, '-') which means three hashes up
    against the right hand border. Or we might require a dot at the
    border (e.g. (2, 0, '-')) to delimit a sequence which extends into
    but terminates in the border character.

    In both these cases we omit the '.+' matcher.
    """

    def __init__(self, counts):
        soft_lead = True
        soft_tail = True
        if counts and counts[0] == '-':
            counts = counts[1:]
            soft_lead = False
        if counts and counts[-1] == '-':
            counts = counts[:-1]
            soft_tail = False
        self.expr = sum([[n * '#', '.+'] for n in counts], [])[:-1]
        if soft_lead:
            self.expr = ['.*'] + self.expr
        if soft_tail:
            self.expr = self.expr + ['.*']
        self.expr = tuple(x for x in self.expr if x != '')
        if self.expr == ('.*', '.*'):
            self.expr = ('.*',)

    def __repr__(self):
        return f'<Pattern: {self.expr}>'

    def matches(self, plan):
        """
        >>> list(Pattern(()).matches('?'))
        ['.']
        >>> list(Pattern(()).matches('#'))
        []
        >>> list(Pattern(()).matches('.'))
        ['.']
        >>> list(Pattern((1, 1)).matches('???'))
        ['#.#']
        >>> list(Pattern((1, 1, '-')).matches('???'))
        ['#.#']
        >>> list(Pattern((1, '-')).matches('???'))
        ['..#']
        >>> list(Pattern(('-', 1)).matches('???'))
        ['#..']
        >>> sorted(Pattern((2,)).matches('???'))
        ['##.', '.##']
        """
        return matches(plan, list(self.expr), '')

    def __eq__(self, other):
        return self.expr == other.expr

    def __hash__(self):
        return hash(self.expr)

class FloorPlan:

    """(Degraded) floorplan of one unit of the hot spring (consisting
    of '.', '#', '?).

    Also caches results of pattern matches against the plan to track
    number of ways that a given pattern can match against this plan.
    """

    def __init__(self, text):
        self.text = text
        self.ways = {}

    def accommodations(self, counts) -> int:
        """
        >>> FloorPlan('???').accommodations(('-', 0))
        1
        >>> FloorPlan('???').accommodations((0, '-'))
        1
        """
        if counts not in self.ways:
            self.ways[counts] = len(list(Pattern(counts).matches(self.text)))
        return self.ways[counts]

    def __repr__(self):
        return f'<FloorPlan {self.text}>'

def matches(plan: str, pattern: list[str], prefix: str):

    """
    Generates all the ways a pattern can match a floorplan.

    `plan` - sequence of `.`, `#`, `?`
    `pattern` - sequence of `.*`, `.+`, `#...`
    `prefix` - matched so far
    """

    if not plan:
        match pattern:
            case []: yield prefix
            case ['.*']: yield from matches(plan, pattern[1:], prefix)
    elif pattern and plan:
        match pattern[0]:
            case '.*':
                match plan[0]:
                    case '.':
                        yield from matches(plan[1:], pattern, prefix + '.')
                    case '#': yield from matches(plan, pattern[1:], prefix)
                    case '?':
                        yield from matches(plan[1:], pattern, prefix + '.')
                        yield from matches(plan, pattern[1:], prefix)
            case '.+':
                match plan[0]:
                    case '#': return
                    case _: yield from matches(plan[1:], ['.*'] + pattern[1:], prefix + '.')
            case h:
                if n := len(h):
                    #optimisation
                    if n > len(plan):
                        return

                    match plan[0]:
                        case '.': return
                        case _:
                            if n > 1:
                                yield from matches(plan[1:], [(n-1) * '#'] + pattern[1:], prefix + '#')
                            else:
                                yield from matches(plan[1:], pattern[1:], prefix + '#')


def partitions(counts, filled, remaining: list[FloorPlan]):

    """Generates all the ways we can split the counts we have to
    apportion between the (five) floorplans available.

    Takes into account that some of the sequence extend into or
    straddle the gap, so a partition across the five identical
    floorplans might look like, for instance:

    ((2,), (1, '-'), ('-', 0, 2), (1, '-'), ('-', 0, 2))

    which is five sequences of ## but two crossing the boundary `?`
    between floorplans.

    Once we have these, we already have the number of ways each of
    these might be realised (`FloorPlan.accommodations()`) and given
    that the `remaining` parameter is actually five instances of *the
    same* FloorPlan which is where the cache is, it's pretty quick to
    multiply the counts out...

    """

    if not remaining:
        if not counts:
            yield tuple(filled)
    else:
        plan = remaining[0]

        r_min = 2 if (counts and counts[0] == '-') else 0
        r_max = len(counts) + 1

        for i in range(r_min, r_max):
            chunk = tuple(counts[0:i])

            # non overlapping
            if plan.accommodations(chunk) > 0:
                yield from partitions(counts[i:], filled + [chunk], remaining[1:])

            # pulling forward part of the next count as an overlap
            if len(counts) > i and len(remaining) >= 1:
                for n in range(0, counts[i]):
                    overlapping_chunk = tuple(list(chunk) + [n, '-'])
                    cont = ['-', counts[i] - n - 1] + list(counts[i+1:])
                    if plan.accommodations(overlapping_chunk) > 0:
                        yield from partitions(cont, filled + [overlapping_chunk], remaining[1:])

class SimpleRow:

    def __init__(self, plan, counts):
        self.plan = plan
        self.expr = Pattern(counts)

    def solutions(self):
        return set(self.expr.matches(self.plan))

    def __repr__(self):
        return f'<SimpleRow {self.plan} {self.expr}>'

    @staticmethod
    def parse(line):
        plan, counts = line.split()
        return SimpleRow(plan, [int(n) for n in counts.split(',')])

class UnfoldedRow:

    def __init__(self, plan, counts):
        self.plan = FloorPlan(plan)
        self.counts = counts * 5

    def partitions(self):
        """
        >>> UnfoldedRow('??', (2,)).partitions()
        [((2,), (2,), (2,), (2,), (2,))]
        """
        return list(partitions(self.counts, [], [self.plan] * 5))

    def possibilities(self):
        """
        >>> UnfoldedRow.parse('.??..??...?##. 1,1,3').possibilities()
        16384
        >>> UnfoldedRow.parse('????.#...#... 4,1,1').possibilities()
        16
        >>> UnfoldedRow.parse('?###???????? 3,2,1').possibilities()
        506250
        """
        return sum(reduce(operator.mul, [self.plan.accommodations(chunk) for chunk in partition], 1) for partition in self.partitions())

    def verify(self):
        """Exploit symmetry to look for any missing partitions.
        Calculate with everything flipped, then flip the results and
        ensure the partitions we generate each way are identical.
        """
        backward_partitions =  partitions(self.counts[::-1], [], [FloorPlan(self.plan.text[::-1])] * 5)
        rpartitions = [tuple(reversed([tuple(reversed(segment)) for segment in p])) for p in backward_partitions]
        forward = sorted(self.partitions())
        backward = sorted(rpartitions)
        assert forward == backward

    @staticmethod
    def parse(line):
        plan, counts = line.split()
        return UnfoldedRow(plan, [int(n) for n in counts.split(',')])


def day12a(lines):
    """
    >>> day12a(TEST_INPUT)
    21
    """
    return sum(len(SimpleRow.parse(line).solutions()) for line in lines)


def day12b(lines):
    """
    >>> day12b(TEST_INPUT)
    525152
    """
    # This one takes a long time but does return... there were better
    # ways to do it
    return sum(UnfoldedRow.parse(line).possibilities() for line in lines)


def main():
    with open('aoc23/data/day12input.txt') as fd:
        lines = list(fd)
    print(f'Day 12a: {day12a(lines)}')
    print(f'Day 12b: {day12b(lines)}')


if __name__ == '__main__':
    main()
