__all__ = [
  'FormulaParser',
  'AnyParser', 'SomeParser', 'OrParser', 'PlainParser',
  'AbstractParser'
]


class AbstractParser(object):
  def __init__(self, token):
    self.token = token
  
  @property
  def MODIFIERS(self):
    raise NotImplementedException
  
  @classmethod
  def create_maybe(cls, token):
    raise NotImplementedException
  
  def matches(self, tokens, index):
    raise NotImplementedException
  
  def can_match_types(self, types):
    raise NotImplementedException


class PlainParser(AbstractParser):
  MODIFIERS = tuple()
  
  @classmethod
  def create_maybe(cls, token):
    return cls(token)
  
  def matches(self, tokens, index):
    if tokens[index] == self.token:
      return 1
  
  def can_match_types(self, types):
    return self.token in types


class AnyParser(AbstractParser):
  MODIFIERS = tuple('*')
  
  @classmethod
  def create_maybe(cls, token):
    if token.endswith('*'):
      return cls(token[:-1])
  
  def matches(self, tokens, index):
    count = 0
    while index + count < len(tokens) and tokens[index + count] == self.token:
      count += 1
    return count
  
  def can_match_types(self, types):
    return True


class SomeParser(AnyParser):
  MODIFIERS = tuple('+')
  
  @classmethod
  def create_maybe(cls, token):
    if token.endswith('+'):
      return cls(token[:-1])
  
  def matches(self, tokens, index):
    count = super(SomeParser, self).matches(tokens, index)
    if count > 0:
      return count
  
  def can_match_types(self, types):
    return self.token in types


class OrParser(AbstractParser):
  MODIFIERS = tuple('|')
  
  def __init__(self, tokens):
    self.tokens = tokens
  
  @classmethod
  def create_maybe(cls, token):
    if '|' in token and token[0] != '|' and token[-1] != '|':
      return cls(token.split('|'))
  
  def matches(self, tokens, index):
    for token in self.tokens:
      if token == tokens[index]:
        return 1
  
  def can_match_types(self, types):
    for token in self.tokens:
      if token in types:
        return True
    return False


class FormulaParser(object):
  PARSERS = tuple([
    # Order matters here
    AnyParser,
    SomeParser,
    OrParser,
    PlainParser
  ])
  
  def __init__(self, formula):
    self.MODIFIERS = tuple(self.get_modifiers())
    self.formula = formula
    self.tokens = self.tokenize(formula)
    self._parsers = tuple(self.form_parsers())
    self.types = frozenset(self.get_types())
  
  def can_match_types(self, types):
    types = frozenset(types)
    for parser in self._parsers:
      if not parser.can_match_types(types):
        return False
    return True
  
  def get_types(self):
    for parser in self._parsers:
      if isinstance(parser, OrParser):
        for token in parser.tokens:
          yield token
      else:
        yield parser.token
  
  def get_modifiers(self):
    for parser in self.PARSERS:
      for modifier in parser.MODIFIERS:
        yield modifier
  
  def form_parsers(self):
    for token in self.tokens:
      for parser in self.PARSERS:
        parser_instance = parser.create_maybe(token)
        if parser_instance:
          yield parser_instance
          break
      else:
        raise Exception("No parsers apply to token '{}'".format(token))
  
  @staticmethod
  def tokenize(formula):
    return formula.split(' ')
  
  def matches(self, formula):
    index = 0
    tokens = self.tokenize(formula)
    for parser in self._parsers:
      if index >= len(tokens):
        # Too few tokens
        return False
      count = parser.matches(tokens, index)
      if count is None:
        return False
      index += count
    if index < len(tokens):
      # Too many tokens
      return False
    return True
  
  def __repr__(self):
    return "FormulaParser('{}')".format(self.formula)
