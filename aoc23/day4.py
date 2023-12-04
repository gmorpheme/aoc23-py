import re

card_re = re.compile(r'Card\s+(\d+):\s+(.*)\s+\|\s+(.*)\s*$')


class Card:
    def __init__(self, line):
        if m := card_re.match(line):
            self.id = int(m.group(1))
            self.winners = set(int(s) for s in m.group(2).split())
            self.revealed = set(int(s) for s in m.group(3).split())

    def matches(self):
        return len(self.winners & self.revealed)

    def score(self):
        matches = self.matches()
        if matches:
            return 1 << (matches - 1)
        else:
            return 0

    def __repr__(self):
        return f'<Card: {self.id} {self.winners} {self.revealed}>'


TEST_LINES = [
    'Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53',
    'Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19',
    'Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1',
    'Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83',
    'Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36',
    'Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11',
]


def day4a(lines):
    """
    >>> day4a(TEST_LINES)
    13
    """
    return sum(Card(line).score() for line in lines)


def day4b(lines):
    """
    >>> day4b(TEST_LINES)
    30
    """
    counts = [1] * len(lines)
    for i in range(0, len(lines)):
        hits = Card(lines[i]).matches()
        if hits:
            for offset in range(1, hits + 1):
                if i + offset < len(lines):
                    counts[i + offset] += counts[i]
    return sum(counts)


def main():
    with open('data/day4input.txt') as f:
        lines = list(f)
    print(f'Day 4a: {day4a(lines)}')
    print(f'Day 4b: {day4b(lines)}')


if __name__ == '__main__':
    main()
