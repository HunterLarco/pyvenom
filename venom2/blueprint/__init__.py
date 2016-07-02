__all__ = [
  'tokenizer', 'grammer'
]

import tokenizer
import grammer


def main():
  example = '''
  APIRequest:
    required string username
    required int userid
    required bool requires_adult
    optional int age [default = 1]
      enforce age > 0
      enforce age < 100
      enforce age >= 18 when requires_adult is true
          or environment.testing

  APIResponse:
    required long longitude
    required long latitude

  REQUEST:
    encoding [json, xml, rpc]
    container [location_request]

  RESPONSE:
    encoding [auto]
    container [location_response]
  '''
  foo = tokenizer.Tokenizer(example, tokens=grammer.TOKENS)
  print foo
  for item in foo:
    print item


if __name__ == '__main__':
  main()