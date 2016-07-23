import tokenizer
import grammar
import parser

example1 = '''
  // Creating a group
  APIRequest:
    required string username
    required int userid
    required bool requires_adult
    optional int age
      enforce age > 0
      enforce age < 100
      enforce age >= 18 when requires_adult is true
          or environment.testing

  APIResponse:
    required number longitude
    required number latitude

  // Populating a group
  REQUEST:
    encoding [json, xml, rpc]
    container [location_request]

  RESPONSE:
    encoding [auto]
    container [location_response]
'''

example2 = '''
  APIRequest:
    required string username
    required int userid
    required bool requires_adult

  APIResponse:
    required number longitude
    required number latitude
'''

example3 = '''
  enforce age > 0
'''

def main():
  # for rule in grammar.RULES:
    # print rule.formula, rule.formula.can_match_types(['type', 'REQUIRED', 'NAME'])
  
  tokens = tokenizer.Tokenizer(example1, tokens=grammar.TOKENS)
  rules = parser.Parser(tokens, rules=grammar.RULES)
  print rules.scope
  blocks = rules.parse()
  blocks = rules.parse()
  blocks = rules.parse()
  blocks = rules.parse()
  blocks = rules.parse()
  print rules.scope
  
  for block in blocks:
    block.pretty_print()

if __name__ == '__main__':
  main()