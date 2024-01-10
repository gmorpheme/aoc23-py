import re
from dataclasses import dataclass, field
from collections import OrderedDict
from functools import reduce

TEST_INPUT_1 = [
    'broadcaster -> a, b, c',
    '%a -> b',
    '%b -> c',
    '%c -> inv',
    '&inv -> a',
]

TEST_INPUT_2 = [
    'broadcaster -> a',
    '%a -> inv, con',
    '&inv -> b',
    '%b -> con',
    '&con -> output',
]

LO, HI = True, False
OFF, ON = True, False

@dataclass
class Node:
    name: str
    ins: dict[str, bool] = field(default_factory=OrderedDict)
    outs: list[str] = field(default_factory=list)

    def connect_source(self, node):
        node.outs.append(self.name)
        self.ins[node.name] = LO

    def signal(self, bus, source: str, value):
        self.ins[source] = value

    def reset(self):
        for i in self.ins:
            self.ins[i] = LO

    def state(self):
        return sum(int(b) << i for i, b in enumerate(self.ins.values()))


class FlipFlop(Node):
    mem: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mem = LO

    def signal(self, bus, source, value):
        super().signal(bus, source, value)
        if value == LO:
            self.mem ^= LO
            for o in self.outs:
                bus.send(self, self.mem, o)

    def state(self):
        return int(self.mem)

    def reset(self):
        super().reset()
        self.mem = LO

class Conjunction(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def signal(self, bus, source, value):
        super().signal(bus, source, value)
        if all(t == HI for t in self.ins.values()):
            for o in self.outs:
                bus.send(self, LO, o)
        else:
            for o in self.outs:
                bus.send(self, HI, o)


class Broadcaster(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def signal(self, bus, source, value):
        super().signal(bus, source, value)
        for o in self.outs:
            bus.send(self, value, o)


def dump_component_state(components):
    for name, component in components.items():
        if isinstance(component, Conjunction) and len(component.ins) > 1:
            print(f'{name}: {component.state():>016b} ({component.state()})')

    b = 0
    for i, f in enumerate(f for f in components.values() if isinstance(f, FlipFlop)):
        b += f.state() << i
    print(f'FF: {b:>016b}')

COUNTERS = [('nl', 7), ('cr', 9), ('jx', 8), ('vj', 11)]

def counter_state(components):
    return tuple(components[n].state() for n, _ in COUNTERS)

def counter_diff(l, r):
    return tuple([(l[i] - r[i]) % (2 ** COUNTERS[i][1]) for i in range(len(l))])

def counter_sum(t, d):
    return tuple((t[i] + d[i]) % (2 ** COUNTERS[i][1]) for i in range(len(t)))

def counter_double(t):
    return tuple((t[i] * 2) % (2 ** COUNTERS[i][1]) for i in range(len(t)))

def flipper_state(components, keys):
    return sum(components[keys[i]].state() << i for i in range(len(keys)))

def reset(components):
    for c in components.values():
        c.reset()

def calculate(init, power_diffs):

    print(f'calculating up to {2 ** (len(power_diffs) + 1) - 1}')

    for possibility in range(0, 2 ** (len(power_diffs) + 1)):
        t = reduce(counter_sum, (power_diffs[i] for i in range(0, len(power_diffs)) if possibility & (1 << i)), init)
        if t == 0:
            return possibility

def nl_state(components):
    return flipper_state(components, ['db', 'ml', 'bn', 'hk', 'rs', 'hh', 'rg', 'hr', 'kf', 'xx', 'ff', 'ql'])

@dataclass
class EventBus:

    q: list = field(default_factory=list)

    def send(self, source, value, receiver):
        self.q.append((source.name, value, receiver))

    def push_button(self, components):
        self.q.append(('button', LO, 'broadcaster'))

    def pump(self, components):
        lo = hi = 0

        while self.q:
            source, value, receiver = self.q.pop(0)
            if value == LO:
                lo += 1
            else:
                hi += 1
            components[receiver].signal(self, source, value)

        # dump_component_state(components)
        return (lo, hi)

    def push_and_pump_n(self, components, n = None):
        total_lo = total_hi = 0
        presses = 0
        while (n is None or presses < n):
            self.push_button(components)
            lo, hi = self.pump(components)
            presses += 1
            total_lo += lo
            total_hi += hi
        return total_lo, total_hi, presses

comp_re = re.compile(r'([&%]?)(\w+) -> (.*)')

def wire(lines):
    components = OrderedDict()
    wires = []
    for line in lines:
        t, n, ws = comp_re.match(line.strip()).groups()
        if t == '&':
            t = Conjunction
        elif t == '%':
            t = FlipFlop
        else:
            t = Broadcaster

        components[n] = t(n)
        wires.append((n, [w.strip() for w in ws.split(',')]))

    cs = ['broadcaster']
    while cs and wires:
        c = cs.pop(0)
        # print(f'wiring {c}')
        ws = sum([ws for name, ws in wires if name == c], [])
        for w in ws:
            # print(f'to {w}')
            if w not in components:
                components[w] = Node(w)
            cs.append(w)
            components[w].connect_source(components[c])
        wires = [(name, w) for (name, w) in wires if name != c]

    return components

def day20a(lines):
    """
    >>> day20a(TEST_INPUT_1)
    32000000
    >>> day20a(TEST_INPUT_2)
    11687500
    """
    components = wire(lines)
    bus = EventBus()
    lo, hi, _ = bus.push_and_pump_n(components, 1000)
    return lo * hi

def day20b(lines):
    """
    This one was worked out manually by studying the graph...
    """
    pass

def main():
    with open('aoc23/data/day20input.txt') as fd:
        lines = list(fd)
    print(f'Day 20a: {day20a(lines)}')
    print(f'Day 20b: {day20b(lines)}')


if __name__ == '__main__':
    main()
