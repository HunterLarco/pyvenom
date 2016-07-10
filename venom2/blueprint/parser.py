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


class Parser(object):
  RULES = frozenset()
  
  def __init__(self, tokenizer, rules=None):
    if rules: self.RULES = frozenset(rules)
    self.tokenizer = tokenizer
    self.validate_rules(self.RULES)
    self.rule_catalog = {
      rule.symbol: rule
      for rule in self.RULES
    }
    self.token_catalog = {
      token.name: token
      for token in self.tokenizer.TOKENS
    }
  
  @staticmethod
  def validate_rules(rules):
    for rule in rules:
      if rule.symbol == 'main':
        break
    else:
      raise ValueError("Parser rules must include a main' symbol")

  def parse(self):
    tokens = list(self.tokenizer)
    
    # for item in self.get_dependency_mro('main'):
    #   print item
    # return
    
    for rule in self.get_dependency_mro('main'):
      tokens = list(self.parse_rule(rule, tokens))
    for token in tokens:
      token.pretty_print()
  
  def parse_rule(self, rule, tokens):
    index = 0
    while index < len(tokens):
      for tokens_end in range(len(tokens), index, -1):
        subsect = tokens[index:tokens_end]
        subsect_string = ' '.join([
          token.name for token in subsect])
        if rule.matches(subsect_string):
          index += len(subsect)
          yield rule.build(subsect)
          break
      else:
        yield tokens[index]
        index += 1
  
  def get_dependency_mro(self, symbol, used=None):
    if used is None: used = []
    if not symbol in self.rule_catalog:
      if symbol in self.token_catalog:
        return
      raise ValueError("Unknown symbol '{}'".format(symbol))
    rule = self.rule_catalog[symbol]
    sub_rules = rule.formula.types
    for sub_rule in sub_rules:
      for dependency in self.get_dependency_mro(sub_rule, used=used):
        yield dependency
    if not rule.symbol in used:
      used.append(rule.symbol)
      yield rule
  
  def __repr__(self):
    return 'Parser({} Rules, {:.2f}% Progress)'.format(
        len(self.RULES), 0)
