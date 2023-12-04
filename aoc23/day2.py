from typing import NamedTuple
from functools import reduce
import re


class RGB(NamedTuple):
    red: int
    green: int
    blue: int

    def power(self) -> int:
        return self.red * self.green * self.blue


def upper(left_rgb, right_rgb) -> RGB:
    """Return an RGB with max of each component in left and right"""
    return RGB(
        red=max(left_rgb.red, right_rgb.red),
        green=max(left_rgb.green, right_rgb.green),
        blue=max(left_rgb.blue, right_rgb.blue),
    )


evidence_regex = re.compile(r'(\d+) (blue|green|red)')


def to_rgb(text) -> RGB:
    pairs = evidence_regex.findall(text)
    dictionary = {'red': 0, 'green': 0, 'blue': 0} | {
        colour: int(number) for (number, colour) in pairs
    }
    return RGB(**dictionary)


game_regex = re.compile(r'Game (\d+): (.*)')


class Game:
    def __init__(self, text):
        if m := game_regex.match(text):
            id, evidence = m.groups()
            self.id = id
            self.evidence = list(map(to_rgb, evidence.split(';')))
            self.minimums = reduce(upper, self.evidence)
        else:
            raise ValueError('bad game description')

    def __str__(self):
        return f'GAME: {self.id} MINIMUMS: {self.minimums}'

    def possible(self, rgb) -> bool:
        return (
            self.minimums.red <= rgb.red
            and self.minimums.green <= rgb.green
            and self.minimums.blue <= rgb.blue
        )


TEST_DATA = [
    "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green",
    "Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue",
    "Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red",
    "Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red",
    "Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green",
]

CANDIDATE = RGB(red=12, green=13, blue=14)


def day2a(lines):
    """
    >>> day2a(TEST_DATA)
    8
    """
    return sum(int(game.id) for game in map(Game, lines) if game.possible(CANDIDATE))


def day2b(lines):
    """
    >>> day2b(TEST_DATA)
    2286
    """
    return sum(Game(line).minimums.power() for line in lines)


def main():
    lines = list(open('data/day2input.txt'))
    print(f'Day 2a: {day2a(lines)}')
    print(f'Day 2b: {day2b(lines)}')


if __name__ == '__main__':
    main()
