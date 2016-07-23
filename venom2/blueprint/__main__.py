import parser

def main():
  foo = parser.FormulaTokenGroup.parse('foo (bar|baz+|(one two))? foo*  foo|bar+',
      implicit_group=True)
  print foo
  foo.print_matching_tree()
  # foo.matches_exactly('asd')
  
  # foo = parser.Formula('foo (bar|baz)* foo{1:3} bar? baz')
  # print foo
  # print foo.matching_tree
  # print foo.matches_exactly('foo bar foo foo foo baz')
  # print foo.could_match('foo bar')
  

if __name__ == '__main__':
  main()
