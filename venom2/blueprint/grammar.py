# venom imports
from venom2.blueprint.tokenizer import Token
from venom2.blueprint.parser import Rule


__all__ = ['TOKENS', 'RULES']


TOKENS = frozenset([
  # Scope
  Token('(', 'LPAREN'),
  Token(')', 'RPAREN'),
  Token('[', 'LSQBRACKET'),
  Token(']', 'RSQBRACKET'),
  # Comments
  Token(r'#[^\n]*', 'COMMENT', regex=True),
  Token(r'//[^\n]*', 'COMMENT', regex=True),
  # Separator
  Token(':', 'SEMICOLON'),
  Token(',', 'COMMA'),
  Token('.', 'PERIOD'),
  # Assignment
  Token('=', 'ASSIGN'),
  # Comparison
  Token('==', 'EQ'),
  Token('<', 'LT'),
  Token('<=', 'LE'),
  Token('>', 'GT'),
  Token('>=', 'GE'),
  Token('!=', 'NE'),
  Token('<>', 'NE'),
  Token('!', 'NOT'),
  # Structures
  Token('enum', 'ENUM'),
  # Logical statements
  Token('enforce', 'ENFORCE'),
  Token('when', 'WHEN'),
  Token('and', 'AND'),
  Token('or', 'OR'),
  Token('not', 'NOT'),
  # Field types
  Token('required', 'REQUIRED'),
  Token('optional', 'OPTIONAL'),
  # Data types
  Token('string', 'STRING'),
  Token('str', 'STRING'),
  Token('integer', 'INT'),
  Token('int', 'INT'),
  Token('float', 'FLOAT'),
  Token('number', 'NUMBER'),
  Token('boolean', 'BOOLEAN'),
  Token('bool', 'BOOLEAN'),
  # Values
  Token(r'[0-9]+(\.[0-9]+)?', 'NUMBERLITERAL', regex=True),
  Token(r'[a-zA-Z_][a-zA-Z0-9_]*', 'NAME', regex=True),
])

RULES = frozenset([
  Rule('main'       , r'group+'),
  
  Rule('group'      , r'groupheader fieldorconditional+'),
  Rule('groupheader', r'NAME SEMICOLON'),
  # nested or clause
  Rule('fieldorconditional', r'field|conditional'),
  Rule('conditional', r'field condition+'),
  Rule('field'      , r'REQUIRED|OPTIONAL type NAME'),
  Rule('type'       , r'STRING|INT|FLOAT|NUMBER|BOOLEAN'),
  
  Rule('condition'  , r'ENFORCE comparison'),
  Rule('comparison' , r'lcomparison|rcomparison'),
  # cannot duplicate name because of catalog collision
  Rule('lcomparison' , r'NUMBERLITERAL operator NAME'),
  Rule('rcomparison' , r'NAME operator NUMBERLITERAL'),
  Rule('operator'   , r'EQ|LT|LE|GT|GE|NE|NE|NOT'),
  
  Rule('comment'    , r'COMMENT')
])
