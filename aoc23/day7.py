from collections import Counter
from operator import mul

TEST_INPUT = ['32T3K 765', 'T55J5 684', 'KK677 28', 'KTJJT 220', 'QQQJA 483']

val_map_a = dict((v, k) for k, v in enumerate('23456789TJQKA'))
val_map_b = dict((v, k) for k, v in enumerate('J23456789TQKA'))


def type_key_a(text):
    return list(reversed(sorted(Counter(text).values())))


def boost(text):
    if counter := Counter(text.replace('J', '')):
        highest_freq = max(counter.values())
        mode = [v for v, n in counter.most_common() if n == highest_freq]
        best = max(mode, key=lambda c: val_map_b[c])
        return text.replace('J', best)
    else:
        return text


def type_key_b(text):
    return type_key_a(boost(text))


class Hand:
    def __init__(self, text, val_map=val_map_a, type_key_fn=type_key_a):
        self.text = text
        self.tie_break_vals = [val_map[c] for c in self.text]
        self.type_key = type_key_fn(self.text)

    def __lt__(self, other):
        return self.type_key < other.type_key or (
            self.type_key == other.type_key
            and self.tie_break_vals < other.tie_break_vals
        )

    @staticmethod
    def b(text):
        return Hand(text, val_map=val_map_b, type_key_fn=type_key_b)

    def __eq__(self, other):
        return self.text == other.text

    def __repr__(self):
        return f'{self.text}'

    def __hash__(self):
        return hash(self.text)


def parse_a(lines):
    return [(Hand(h), int(b)) for h, b in map(lambda l: l.split(), lines)]


def parse_b(lines):
    return [(Hand.b(h), int(b)) for h, b in map(lambda l: l.split(), lines)]


def day7a(lines):
    """
    >>> day7a(TEST_INPUT)
    6440
    """
    return sum(
        map(
            lambda t: (t[0] + 1) * t[1],
            enumerate(bid for _, bid in sorted(parse_a(lines), key=lambda t: t[0])),
        )
    )


def day7b(lines):
    """
    >>> day7b(TEST_INPUT)
    5905
    """
    return sum(
        map(
            lambda t: (t[0] + 1) * t[1],
            enumerate(bid for _, bid in sorted(parse_b(lines), key=lambda t: t[0])),
        )
    )


def main():
    with open('aoc23/data/day7input.txt') as fd:
        lines = list(fd)
    print(f'Day 7a: {day7a(lines)}')
    print(f'Day 7b: {day7b(lines)}')


if __name__ == '__main__':
    main()
