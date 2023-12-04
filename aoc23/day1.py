import re


def process_line_a(line):
    digits = list(filter(lambda c: c.isdigit(), line))

    first = int(digits[0])
    last = int(digits[-1])

    return first * 10 + last


def day1a(lines):
    """
    >>> day1a(['1abc2','pqr3stu8vwx','a1b2c3d4e5f','treb7uchet'])
    142
    """
    return sum([process_line_a(line) for line in lines])


digit_matcher = re.compile("one|two|three|four|five|six|seven|eight|nine|[0-9]")


def day1b_digit_strings(line):
    digit_matches = []
    for i in range(0, len(line)):
        m = digit_matcher.match(line[i:])
        if m:
            digit_matches.append(m.group(0))
    return digit_matches


def day1b_to_number(word):
    match word:
        case "one":
            return 1
        case "two":
            return 2
        case "three":
            return 3
        case "four":
            return 4
        case "five":
            return 5
        case "six":
            return 6
        case "seven":
            return 7
        case "eight":
            return 8
        case "nine":
            return 9
        case other:
            return int(other[0])


def process_line_b(line):
    digits = day1b_digit_strings(line)

    first = day1b_to_number(digits[0])
    last = day1b_to_number(digits[-1])

    return first * 10 + last


def day1b(lines):
    """
    >>> day1b(['two1nine','eightwothree','abcone2threexyz','xtwone3four','4nineeightseven2','zoneight234','7pqrstsixteen'])
    281
    """
    return sum([process_line_b(line) for line in lines])


def main():
    lines = list(open("data/day1input.txt"))
    print(f"Day 1a: {day1a(lines)}")
    print(f"Day 1b: {day1b(lines)}")


if __name__ == "__main__":
    main()
