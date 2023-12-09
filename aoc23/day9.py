from itertools import pairwise

TEST_INPUT = ['0 3 6 9 12 15', '1 3 6 10 15 21', '10 13 16 21 30 45']

def compute_next(nums):

    """
    >>> compute_next([0, 3, 6, 9, 12, 15])
    18
    >>> compute_next([1, 3, 6, 10, 15, 21])
    28
    """
    nums = list(nums)
    if not any(nums):
        return 0
    else:
        return nums[-1] + compute_next(j - i for i, j in pairwise(nums))



def day9a(lines):
    """
    >>> day9a(TEST_INPUT)
    114
    """
    return sum(compute_next(int(c) for c in line.split()) for line in lines)


def day9b(lines):
    """
    >>> day9b(TEST_INPUT)
    2
    """
    return sum(compute_next(int(c) for c in reversed(line.split())) for line in lines)


def main():
    with open('aoc23/data/day9input.txt') as fd:
        lines = list(fd)
    print(f'Day 9a: {day9a(lines)}')
    print(f'Day 9b: {day9b(lines)}')


if __name__ == '__main__':
    main()
