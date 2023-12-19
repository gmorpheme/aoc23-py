import re
from typing import NamedTuple
from typing import Any
import operator
from itertools import takewhile
from copy import deepcopy

TEST_INPUT = [
    'px{a<2006:qkq,m>2090:A,rfg}',
    'pv{a>1716:R,A}',
    'lnx{m>1548:A,A}',
    'rfg{s<537:gd,x>2440:R,A}',
    'qs{s>3448:A,lnx}',
    'qkq{x<1416:A,crn}',
    'crn{x>2662:A,R}',
    'in{s<1351:px,qqz}',
    'qqz{s>2770:qs,m<1801:hdj,R}',
    'gd{a>3333:R,R}',
    'hdj{m>838:A,pv}',
    ' ',
    '{x=787,m=2655,a=1222,s=2876}',
    '{x=1679,m=44,a=2067,s=496}',
    '{x=2036,m=264,a=79,s=2244}',
    '{x=2461,m=1339,a=466,s=291}',
    '{x=2127,m=1623,a=2188,s=1013}',
]

class Part(NamedTuple):
    x: int
    m: int
    a: int
    s: int

    def total(self):
        return sum(self)

    @staticmethod
    def parse(text):
        part_re = re.compile(r'\{x=(\d+),m=(\d+),a=(\d+),s=(\d+)\}')
        return Part(*[int(i) for i in part_re.match(text).groups()])

class PartRange(NamedTuple):
    x: Any
    m: Any
    a: Any
    s: Any

    def count(self):
        x, m, a, s = self
        return len(x) * len(m) * len(a) * len(s)

    @staticmethod
    def fresh():
        return PartRange(range(1, 4001),range(1, 4001),range(1, 4001),range(1, 4001))

    def split(self, condition):
        lv, op, rv, cs = condition
        rng = getattr(self, lv)
        if op == operator.lt:
            if rng.stop <= rv:
                return (None, self)
            elif rng.start < rv <= rng.stop:
                return (PartRange(**(self._asdict() | {lv: range(rng.start, rv)})),
                        PartRange(**(self._asdict() | {lv: range(rv, rng.stop)})))
            else:
                return (self, self)
        if op == operator.gt:
            if rv < rng.start:
                return (None, self)
            elif rng.start <= rv < rng.stop-1:
                return (PartRange(**(self._asdict() | {lv: range(rv + 1, rng.stop)})),
                        PartRange(**(self._asdict() | {lv: range(rng.start, rv + 1)})))
                return new
            else:
                return (self, self)


class Clause(NamedTuple):
    lv: str
    op: Any
    rv: int
    cs: str

    def evaluate(self, part:Part):
        if self.op(getattr(part, self.lv), self.rv):
            return self.cs
        else:
            return False

    @staticmethod
    def parse(text):
        cond_re = re.compile(r'([xmas])([><])(\d+):(\w+)')
        l, o, r, c = cond_re.match(text).groups()
        if o == '<':
            return Clause(l, operator.lt, int(r), c)
        else:
            return Clause(l, operator.gt, int(r), c)



class Workflow:

    def __init__(self, text):
        wf_re = re.compile(r'(\w+)\{(.*)\}')
        name, definition = wf_re.match(text.strip()).groups()
        clauses = definition.split(',')
        self.name = name
        self.fallback = clauses.pop()
        self.clauses = [Clause.parse(c) for c in clauses]

    def evaluate(self, part: Part):
        for c in self.clauses:
            consequence = c.evaluate(part)
            if consequence:
                return consequence
        return self.fallback

    def analyse(self, part_range):
        result = []
        for c in self.clauses:
            t, f = part_range.split(c)
            if t:
                result.append((t, c.cs))
            part_range = f
        result.append((part_range, self.fallback))
        return result

class Program:

    def __init__(self, workflows):
        self.workflows = {w.name:w for w in workflows}

    def evaluate(self, part):
        current = 'in'

        while True:
            current = self.workflows[current].evaluate(part)
            if current in ('A', 'R'):
                return current

    def analyse(self):
        worlds = [(PartRange.fresh(), 'in')]
        accept = []
        while worlds:
            c, wf = worlds.pop(0)
            if wf == 'A':
                accept.append(c)
            elif wf != 'R':
                worlds.extend(self.workflows[wf].analyse(c))
        return accept

def parse_puzzle(lines):
    i = iter(lines)
    program = Program(list(Workflow(line.strip()) for line in takewhile(lambda x: x.strip(), i)))
    takewhile(lambda x: not x.strip(), i)
    parts = [Part.parse(line.strip()) for line in list(i)]
    return (program, parts)

def day19a(lines):
    """
    >>> day19a(TEST_INPUT)
    19114
    """
    program, parts = parse_puzzle(lines)
    return sum(p.total() for p in parts if program.evaluate(p) == 'A')

def day19b(lines, n = 1_000_000):
    """
    >>> day19b(TEST_INPUT)
    167409079868000
    """
    program, _ = parse_puzzle(lines)
    return sum(p.count() for p in program.analyse())


def main():
    with open('aoc23/data/day19input.txt') as fd:
        lines = list(fd)
    print(f'Day 19a: {day19a(lines)}')
    print(f'Day 19b: {day19b(lines)}')


if __name__ == '__main__':
    main()
