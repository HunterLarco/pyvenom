# venom imports
from venom2.base.collections import enum

# PSL imports
import re


__all__ = []


def Token(value, name, regex=False):
  return TokenBuilder(value, name, regex=regex)


class BuiltToken(object):
  def __init__(self, token, value):
    self.token = token
    self.value = value
  
  def __iter__(self):
    return (token, value)
  
  def __eq__(self, other):
    assert isinstance(other, self.__class__)
    return (self.token == other.token and
            self.value == other.value)
  
  def __repr__(self):
    return 'BuiltToken({}, "{}")'.format(self.token, self.value)


class TokenBuilder(object):
  def __init__(self, value, name, regex=False):
    self.value = value
    self.name = name
    self._regex = regex
  
  def match_distance(self, string):
    if self._regex:
      pattern = '^{}'.format(self.value)
      match = re.search(pattern, string)
      if not match: return ''
      return match.group()
    elif string.startswith(self.value):
      return self.value
    return ''
  
  def build(self, value):
    return BuiltToken(self, value)
  
  def __iter__(self):
    return (value, name)
  
  def __eq__(self, other):
    assert isinstance(other, self.__class__)
    return (self.value == other.value and
            self.name == other.name)
  
  def __repr__(self):
    return 'TokenBuilder({}"{}", "{}")'.format(
        'r' if self._regex else '', self.value, self.name)


class Tokenizer(object):
  TOKENS = frozenset()
  
  def __init__(self, text, tokens=None):
    if tokens: self.TOKENS = frozenset(tokens)
    self.text = text
    self.index = 0
    self.progress = 0
  
  def __iter__(self):
    return self
  
  def __next__(self):
    if self.index >= len(self.text):
      raise StopIteration()
    candidates = self.TOKENS
    substring = self.text[self.index:]
    refined_candidates = self.refine_candidates(substring, candidates)
    sorted_candidates = sorted(refined_candidates, key=lambda x: x[1])
    if sorted_candidates:
      token, match_distance, matched_value = sorted_candidates[0]
      self.index += match_distance
      return token.build(matched_value)
    self.index += 1
    return self.__next__()
  
  def refine_candidates(self, substring, candidates):
    for token in candidates:
      matched_value = token.match_distance(substring)
      match_distance = len(matched_value)
      if match_distance > 0:
        yield (token, match_distance, matched_value)
  
  # Python 2.7 support
  next = __next__
  
  def __repr__(self):
    return 'Tokenizer({} Tokens, {:.2f}% Progress)'.format(
        len(self.TOKENS), self.progress)
