# venom imports
from venom2.blueprint.tokenizer import Token

TOKENS = frozenset([
  # Scope
  Token('(', 'LPAREN'),
  Token(')', 'RPAREN'),
  Token('[', 'LSQBRACKET'),
  Token(']', 'RSQBRACKET'),
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
  # Name
  Token(r'[a-zA-Z_][a-zA-Z0-9_]*', 'NAME', regex=True),
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
  Token('bool', 'BOOLEAN')
])

RULES = frozenset([
  
])
