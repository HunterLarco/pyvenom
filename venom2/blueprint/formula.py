# venom import
from venom2.base import abstract
from venom2.base import exportutil
from venom2.base import generators
from venom2.base.collections import enum

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
    TokenGroup,
    RepeatedToken,
    OrTokenClause,
    BasicToken
  ]
  for token_type in TOKEN_TYPES:
    token = token_type.parse(token_literal)
    if token: return token
  raise ValueError("Token literal '{}' has no known parser"
      .format(token_literal))


export('MatcherResponseEnum')
MatcherResponseEnum = enum.Enum('MatcherResponseEnum', [
  # Matcher currently matches, but requires more tokens
  # to make a full decision
  'COULD_MATCH',
  # Matcher currently matches the full formula definition
  # but can accomodate more tokens
  'MATCHES_EXACTLY',
  # Matcher has fully failed given the provided tokens
  'DOES_NOT_MATCH',
  # Matcher has successfully matched the tokens at some point
  # in the past, but now does not or is no longer applicable.
  'MATCHER_EXHAUSTED'
])


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
  def build_matcher(self):
    '''
    ' PURPOSE
    '   Returns a bi-directional generator used
    '   to determine if a token stream matches
    '   exactly, will match, or does not match
    '   a formula.
    '
    ' RETURNS
    '   >>> matcher = formula.build_matcher()
    '   >>> matcher.send(next_token)
    '   < EnumValue of type MatcherResponseEnum
    '   < StopIteration exception (matcher no longer useful)
    '''
    # TODO(hunterlarco)
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
  
  def build_matcher(self):
    token_literal = yield MatcherResponseEnum.COULD_MATCH
    if token_literal == self.token_literal:
      yield MatcherResponseEnum.MATCHES_EXACTLY
    else:
      yield MatcherResponseEnum.DOES_NOT_MATCH
    while True: yield MatcherResponseEnum.MATCHER_EXHAUSTED
  
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
  
  def build_matcher(self):
    # HUGE Edge case...
    # (foo bar)+ foo baz
    # against foo bar foo baz
    # we would not know where to backtrack to... Unless we
    # tracked tokens sent to the candidate in the idling
    # phase and pass them back.
    if self.min_count == 0:
      token_literal = yield MatcherResponseEnum.MATCHES_EXACTLY
    else:
      token_literal = yield MatcherResponseEnum.COULD_MATCH

    index = 0
    while self.max_count is None or index < self.max_count:
      # Build candidate
      candidate = self.token.build_matcher()
      candidate.send(None)
      # Idle
      while True:
        # Begin investigating candidate
        candidate_response = candidate.send(token_literal)
        if candidate_response == MatcherResponseEnum.DOES_NOT_MATCH:
          if index < self.min_count:
            # Forever will not match
            while True: yield MatcherResponseEnum.DOES_NOT_MATCH
          else:
            # We've fully matches this candidate
            while True: yield MatcherResponseEnum.MATCHER_EXHAUSTED
        elif candidate_response == MatcherResponseEnum.COULD_MATCH:
          token_literal = yield MatcherResponseEnum.COULD_MATCH
        elif candidate_response == MatcherResponseEnum.MATCHES_EXACTLY:
          if self.min_count <= index + 1:
            token_literal = yield MatcherResponseEnum.MATCHES_EXACTLY
          else:
            token_literal = yield MatcherResponseEnum.COULD_MATCH
        elif candidate_response == MatcherResponseEnum.MATCHER_EXHAUSTED:
          break
      index += 1
        
    while True: yield MatcherResponseEnum.MATCHER_EXHAUSTED
  
  @classmethod
  def has_presidence(cls, formula_literal):
    '''
    ' PURPOSE
    '   The RepeatedToken syntax sometimes is preemptively
    '   applied. Take the following examples...
    '   (1) foo|bar+
    '   (2) (foo|bar)+
    '   In (1), the repeated token should be 'bar' and
    '   in (2), 'foo|bar' should be repeated. Here we make
    '   a specific check that in the case of (1) we do not
    '   apply the repeated token to an OrClause.
    '''
    token = convert_token_literal(formula_literal)
    if isinstance(token, OrTokenClause):
      return False
    return True
  
  @classmethod
  def parse(cls, formula_literal):
    if formula_literal.endswith('*'):
      if not cls.has_presidence(formula_literal[:-1]): return None
      return cls(formula_literal[:-1], 0, None)
    elif formula_literal.endswith('+'):
      if not cls.has_presidence(formula_literal[:-1]): return None
      return cls(formula_literal[:-1], 1, None)
    elif formula_literal.endswith('?'):
      if not cls.has_presidence(formula_literal[:-1]): return None
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
  
  def build_matcher(self):
    token_literal = yield MatcherResponseEnum.COULD_MATCH
    
    for token in self.tokens:
      # Initialized candidate matcher
      candidate = token.build_matcher()
      candidate.send(None)
      # Idle on current candidate
      while True:
        # Begin investigating candidate
        candidate_response = candidate.send(token_literal)
        if candidate_response == MatcherResponseEnum.DOES_NOT_MATCH:
          break
        elif candidate_response == MatcherResponseEnum.COULD_MATCH:
          token_literal = yield MatcherResponseEnum.COULD_MATCH
        elif candidate_response == MatcherResponseEnum.MATCHES_EXACTLY:
          token_literal = yield MatcherResponseEnum.MATCHES_EXACTLY
        elif candidate_response == MatcherResponseEnum.MATCHER_EXHAUSTED:
          # We've fully matches this candidate, thus the entire Or Clause.
          while True: yield MatcherResponseEnum.MATCHER_EXHAUSTED
    
    while True: yield MatcherResponseEnum.DOES_NOT_MATCH
  
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
class TokenGroup(FormulaParserBase):
  def __init__(self, token_literals):
    self.token_literals = list(token_literals)
    self.tokens = [
      convert_token_literal(token_literal)
      for token_literal in self.token_literals
    ]
  
  def print_matching_tree(self, indent=0):
    print '  '*indent + 'TokenGroup('
    for token in self.tokens:
      token.print_matching_tree(indent+1)
    print '  '*indent + ')'
  
  def build_matcher(self):
    '''
    ' PURPOSE
    '   Build a bi-directional matcher for a Token
    '   group.
    '
    ' DESIGN
    '   (1) Given a token feed it to the current
    '       candidate matcher.
    '   > (DOES_NOT_MATCH) Move to next candidate
    '     if it exists, otherwise return DOES_NOT_MATCH.
    '   > (COULD_MATCH) Yield for more tokens
    '   > (MATCHES_EXACTLY) Yield for more tokens,
    '     if next token fails, execute MATCHER_EXHAUSTED case
    '     and resume using provided tokens.
    '   > (MATCHER_EXHAUSTED) Continue to next matcher
    '     if it exists, otherwise return MATCHER_EXHAUSTED.
    '''
    token_literal = yield MatcherResponseEnum.COULD_MATCH
    
    for i, token in enumerate(self.tokens):
      # Initialized candidate matcher
      candidate = token.build_matcher()
      candidate.send(None)
      # Idle on current candidate
      while True:
        # Begin investigating candidate
        candidate_response = candidate.send(token_literal)
        if candidate_response == MatcherResponseEnum.DOES_NOT_MATCH:
          # Forever will not match
          while True: yield MatcherResponseEnum.DOES_NOT_MATCH
        elif candidate_response == MatcherResponseEnum.COULD_MATCH:
          # Continue idling
          token_literal = yield MatcherResponseEnum.COULD_MATCH
        elif candidate_response == MatcherResponseEnum.MATCHES_EXACTLY:
          # If each following token can match nothing, then MATCHES_EXACTLY:
          for j in range(i+1, len(self.tokens)):
            next_token = self.tokens[j]
            next_matcher = next_token.build_matcher()
            if not next_matcher.send(None) == MatcherResponseEnum.MATCHES_EXACTLY:
              break
          else:
            token_literal = yield MatcherResponseEnum.MATCHES_EXACTLY
            continue
          token_literal = yield MatcherResponseEnum.COULD_MATCH
        elif candidate_response == MatcherResponseEnum.MATCHER_EXHAUSTED:
          # We've fully matches this candidate, exit and reuse token
          break
    
    while True: yield MatcherResponseEnum.MATCHER_EXHAUSTED
  
  @classmethod
  def _parse(cls, formula_literal):
    token_literals = extract_token_literals(formula_literal)
    formula_token_group = cls(token_literals)
    return formula_token_group
  
  @classmethod
  def parse(cls, formula_literal, implicit_group=False):
    # print formula_literal
    if formula_literal.startswith('(') and formula_literal.endswith(')'):
      return cls.parse(formula_literal[1:-1], implicit_group=True)
    if implicit_group:
      # This indicates that we want to match the group regardless
      # of whether or not it actually was wrapped in parentheses.
      # we check this after the normal check to ensure that both
      # forms will work as expected.
      return cls._parse(formula_literal)
    return None
  
  def __repr__(self):
    return 'parser.TokenGroup({!r})'.format(self.token_literals)
