import argparse, importlib

parser = argparse.ArgumentParser(
    prog='aoc',
    description='Run advent of code programs')
parser.add_argument('day', metavar='N', type=int, nargs = '?', help = 'day to run')

def day(n):

    try:
        module = importlib.import_module(f'aoc23.day{n}')
        module.main()
    except:
        pass

if __name__ == '__main__':
    opts = parser.parse_args()
    if n := opts.day:
        day(n)
    else:
        for n in range(0, 26):
            day(n)
