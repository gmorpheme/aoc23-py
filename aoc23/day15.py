import re

TEST_INPUT = [
    'rn=1',
    'cm-',
    'qp=3',
    'cm=2',
    'qp-',
    'pc=4',
    'ot=9',
    'ab=5',
    'pc-',
    'pc=6',
    'ot=7',
]


def hash(step):
    """
    >>> hash('HASH')
    52
    """

    val = 0
    for c in step:
        val += ord(c)
        val *= 17
        val %= 256

    return val


op_re = re.compile(r'(.+?)(?:(-)|=(\d+))')


def parse(step):
    """
    >>> parse('rn=1')
    ('rn', 1)
    >>> parse('qp-')
    ('qp', '-')
    """
    k, pop, put = op_re.match(step).groups()
    return (k, pop or int(put))


class HashMap:
    def __init__(self):
        self.store = [[] for _ in range(256)]

    def find(self, k):
        bucket = self.store[hash(k)]
        index = next((n for n, (l, _) in enumerate(bucket) if k == l), None)
        return (bucket, index)

    def __setitem__(self, k, v):
        b, i = self.find(k)
        if i is None:
            b.append((k, v))
        else:
            b[i] = (k, v)

    def __delitem__(self, k):
        b, i = self.find(k)
        if i is not None:
            b.pop(i)

    def power(self):
        n = 0
        for i, b in enumerate(self.store):
            for j, (_, v) in enumerate(b):
                n += (i + 1) * (j + 1) * v
        return n


def day15a(steps):
    """
    >>> day15a(TEST_INPUT)
    1320
    """
    return sum(hash(step) for step in steps)


def day15b(steps):
    """
    >>> day15b(TEST_INPUT)
    145
    """
    m = HashMap()
    for s in steps:
        k, v = parse(s)
        if v == '-':
            del m[k]
        else:
            m[k] = v

    return m.power()


def main():
    with open('aoc23/data/day15input.txt') as fd:
        steps = [s.strip() for s in fd.read().split(',')]
    print(f'Day 15a: {day15a(steps)}')
    print(f'Day 15b: {day15b(steps)}')


if __name__ == '__main__':
    main()
