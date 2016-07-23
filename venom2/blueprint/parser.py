# venom import
from venom2.base import abstract
from venom2.base import exportutil

# PSL imports
import string


__all__ = []
export = exportutil.Exporter(__all__)


@export
def extract_token_literals(token_string):
  '''
  ' PURPOSE
  '   Simple helper method that extracts tokens
  '   from a formula token string. Note that the
  '   tokens extracted are not done recursively,
  '   only at the top level.
  '
  ' EXAMPLE
  '   >>> extract_token_literals('foo (bar|(baz+)|(one two))? foo*')
  '   < generator(['foo', '(bar|(baz+)|(one two))?', 'foo*'])
  '
  ' RAISES
  '   ValueError - Token string contains unexpected characters
  '''
  RESERVED_CHARACTERS = '|*+?() '
  ACCEPTABLE_CHARACTERS = frozenset(
      string.lowercase + string.uppercase + RESERVED_CHARACTERS)
  parentheses_depth = 0
  accumulator = ''
  for char in token_string:
    if not char in ACCEPTABLE_CHARACTERS:
      raise ValueError("Formula token string contains unexpected character '{}'"
          .format(char))
    if char == ' ' and parentheses_depth == 0:
      if accumulator:
         yield accumulator
      accumulator = ''
      continue
    if char == '(':
      parentheses_depth += 1
    elif char == ')':
      parentheses_depth -= 1
    accumulator += char
  if accumulator:
    yield accumulator


@export
def convert_token_literal(token_literal):
  TOKEN_TYPES = [
    # The order of operations matters.
    FormulaTokenGroup,
    OrTokenClause,
    RepeatedToken,
    BasicToken
  ]
  for token_type in TOKEN_TYPES:
    token = token_type.parse(token_literal)
    if token: return token
  raise ValueError("Token literal '{}' has no known parser"
      .format(token_literal))


@export
class FormulaParserBase(object):
  '''
  ' PURPOSE
  '   Used simply as an abstract base class for
  '   formula components. This defines a clear
  '   contract so that components can easily be
  '   nested and parsed.
  '''
  @abstract.NotImplemented
  def matches_exactly(self, token_string):
    '''
    ' PURPOSE
    '   Returns True if and only if this parser
    '   matches the provided token string exactly.
    '''
    pass
  
  @abstract.NotImplemented
  def could_match(self, token_string):
    '''
    ' PURPOSE
    '   Returns True if and only if this parser
    '   could match the provided token string, this
    '   includes valid, but partial matches. This
    '   function is used as a "look-ahead" function
    '   for the recursive decent parser.
    '
    ' EXAMPLES
    '   >>> cls('foo bar baz|foo').could_match('foo')
    '   < True
    '   >>> cls('foo bar baz|foo').could_match('bar')
    '   < False
    '''
    pass

  @abstract.NotImplemented
  def print_matching_tree(cls, indent=0):
    '''
    ' PURPOSE
    '   Prints out a tree representing the logic
    '   required to parse this parser and all children
    '   parsing logic.
    '
    ' EXAMPLES
    '   >>> cls('foo bar (baz|foo)').print_matching_tree()
    '   < BasicToken('foo')
    '   < BasicToken('bar')
    '   < TokenGroup(
    '   <   TokenOrClause(
    '   <     BasicToken('baz')
    '   <     BasicToken('foo')
    '   <   )
    '   < )
    '''
    pass

  @classmethod
  @abstract.NotImplemented
  def parse(cls, formula_literal):
    '''
    ' PURPOSE
    '   Given a formula literal, returns a instance of
    '   this class if it can parse the literal, otherwise
    '   None is returned.
    '
    ' RETURNS
    '   None or cls(...)
    '''
    pass


@export
class BasicToken(FormulaParserBase):
  def __init__(self, token_literal):
    self.token_literal = token_literal
  
  def print_matching_tree(self, indent=0):
    print '  '*indent + 'BasicToken({!r})'.format(self.token_literal)
  
  @classmethod
  def parse(cls, formula_literal):
    if formula_literal and not ' ' in formula_literal:
      return cls(formula_literal)
    return None
  
  def __repr__(self):
    return 'parser.BasicToken({!r})'.format(self.token_literal)


@export
class RepeatedToken(FormulaParserBase):
  def __init__(self, token_literal, min_count, max_count):
    self.token_literal = token_literal
    self.token = convert_token_literal(token_literal)
    self.min_count = min_count
    self.max_count = max_count
  
  def print_matching_tree(self, indent=0):
    print '  '*indent + 'RepeatedToken('
    self.token.print_matching_tree(indent+1)
    print '  '*indent + ', min_count={}, max_count={})'.format(
            self.min_count, self.max_count)
  
  @classmethod
  def parse(cls, formula_literal):
    if formula_literal.endswith('*'):
      return cls(formula_literal[:-1], 0, None)
    elif formula_literal.endswith('+'):
      return cls(formula_literal[:-1], 1, None)
    elif formula_literal.endswith('?'):
      return cls(formula_literal[:-1], 0, 1)
    return None
  
  def __repr__(self):
    return 'parser.RepeatedToken({!r})'.format(self.token_literal)


@export
class OrTokenClause(FormulaParserBase):
  def __init__(self, token_literals):
    self.token_literals = list(token_literals)
    self.tokens = [
      convert_token_literal(token_literal)
      for token_literal in self.token_literals
    ]
  
  def print_matching_tree(self, indent=0):
    print '  '*indent + 'OrTokenClause('
    for token in self.tokens:
      token.print_matching_tree(indent+1)
    print '  '*indent + ')'
  
  @classmethod
  def parse(cls, formula_literal):
    if (not formula_literal.startswith('|') and
        not formula_literal.endswith('|') and
        '|' in formula_literal):
      return cls(formula_literal.split('|'))
    return None
  
  def __repr__(self):
    return 'parser.OrTokenClause({!r})'.format(self.tokens)


@export
class FormulaTokenGroup(FormulaParserBase):
  def __init__(self, token_literals):
    self.token_literals = list(token_literals)
    self.tokens = [
      convert_token_literal(token_literal)
      for token_literal in self.token_literals
    ]
  
  def print_matching_tree(self, indent=0):
    print '  '*indent + 'FormulaTokenGroup('
    for token in self.tokens:
      token.print_matching_tree(indent+1)
    print '  '*indent + ')'
  
  @classmethod
  def parse(cls, formula_literal, implicit_group=False):
    if formula_literal.startswith('(') and formula_literal.endswith(')'):
      recurring_group = cls.parse(formula_literal[1:-1])
      if recurring_group: return recurring_group
      token_literals = extract_token_literals(formula_literal[1:-1])
      formula_token_group = cls(token_literals)
      if len(formula_token_group.tokens) == 1:
        return formula_token_group.tokens[0]
      return formula_token_group
    if implicit_group:
      # This indicates that we want to match the group regardless
      # of whether or not it actually was wrapped in parentheses.
      # we check this after the normal check to ensure that both
      # forms will work as expected.
      recurring_group = cls.parse(formula_literal)
      if recurring_group: return recurring_group
      token_literals = extract_token_literals(formula_literal)
      formula_token_group = cls(token_literals)
      if len(formula_token_group.tokens) == 1:
        return formula_token_group.tokens[0]
      return formula_token_group
    return None
  
  def __repr__(self):
    return 'parser.FormulaTokenGroup({!r})'.format(self.token_literals)


@export
class Formula(object):
  def __init__(self, formula_literal):
    super(Formula, self).__init__()
    self.literal = formula_literal
    self.matching_tree = None
  
  def __repr__(self):
    return 'parser.Formula({!r})'.format(self.literal)
