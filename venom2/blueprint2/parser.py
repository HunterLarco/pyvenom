# venom import
from venom2.blueprint import formula

# PSL imports
import string
import re


__all__ = [
  'Rule',
  'BuiltRule',
  'RuleBuilder',
  'Parser'
]


def Rule(symbol, formula):
  return RuleBuilder(symbol, formula)


class BuiltRule(object):
  def __init__(self, name, tokens):
    self.name = name
    self.tokens = tokens
  
  def pretty_print(self, indent=0):
    if indent > 0: print '  '*indent,
    print "BuiltRule('{}',".format(self.name)
    for token in self.tokens:
      token.pretty_print(indent=indent + 1)
    if indent > 0: print '  '*indent,
    print ")"
  
  def __repr__(self):
    return "BuiltRule('{}', {})".format(self.name, self.tokens)


class RuleBuilder(object):
  MODIFIERS = frozenset('+*|')
  
  def __init__(self, symbol, formula_text):
    self.symbol = symbol
    self.formula = formula.FormulaParser(formula_text)
  
  def matches(self, tokens):
    return self.formula.matches(tokens)
  
  def build(self, tokens):
    return BuiltRule(self.symbol, tokens)
  
  def __repr__(self):
    return "RuleBuilder('{}', '{}')".format(self.symbol, self.formula)


class ParserScope(object):
  def __init__(self, iterable):
    self.scope = {}
    for rule in iterable:
      self.add(rule)
  
  @property
  def types(self):
    return self.scope.keys()
  
  def add(self, rule):
    name = rule.name
    if name in self.scope:
      self.scope[name] += 1
    else:
      self.scope[name] = 1

  def remove(self, rule):
    name = rule.name
    if name in self.scope:
      if self.scope[name] == 1:
        del self.scope[name]
      else:
        self.scope[name] -= 1
  
  def __repr__(self):
    return repr(self.types)
  

class Parser(object):
  RULES = frozenset()
  
  def __init__(self, tokenizer, rules=None):
    if rules: self.RULES = frozenset(rules)
    self.tokenizer = tokenizer
    self.validate_rules(self.RULES)
    self.tokens = list(tokenizer)
    self.scope = ParserScope(self.tokens)
  
  @staticmethod
  def validate_rules(rules):
    for rule in rules:
      if rule.symbol == 'main':
        break
    else:
      raise ValueError("Parser rules must include a main' symbol")

  def parse(self):
    candidates = list(self.get_layer_candidates())
    for rule in candidates:
      self.tokens = list(self.parse_rule(rule))
    return self.tokens
  
  def get_layer_candidates(self):
    for rule in self.RULES:
      if rule.formula.can_match_types(self.scope.types):
        yield rule
  
  def parse_rule(self, rule):
    index = 0
    tokens = self.tokens
    while index < len(tokens):
      for tokens_end in range(len(tokens), index, -1):
        subsect = tokens[index:tokens_end]
        subsect_string = ' '.join([token.name for token in subsect])
        if rule.matches(subsect_string):
          index += len(subsect)
          
          built_rule = rule.build(subsect)
          for token in subsect:
            self.scope.remove(token)
          self.scope.add(built_rule)
          yield built_rule
          break
      else:
        yield tokens[index]
        index += 1
  
  def __repr__(self):
    return 'Parser({} Rules, {:.2f}% Progress)'.format(
        len(self.RULES), 0)
