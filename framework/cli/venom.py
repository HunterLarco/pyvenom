#!/usr/bin/env python


import argparse


def create_command_line_parser():
  parser = argparse.ArgumentParser()

  parser.add_argument('x', type=int, help='the base')
  parser.add_argument('y', type=int, help='the exponent')
  parser.add_argument('-v', '--verbosity', action='count', default=0)
  
  return parser


def main():
  parser = create_command_line_parser()
  args = parser.parse_args()
  
  answer = args.x ** args.y
  if args.verbosity >= 2:
    print '{} to the power {} equals {}'.format(args.x, args.y, answer)
  elif args.verbosity >= 1:
    print '{}^{} == {}'.format(args.x, args.y, answer)
  else:
    print answer


if __name__ == '__main__':
  main()
