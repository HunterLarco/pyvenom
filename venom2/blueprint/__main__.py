import formula

def main():
  foo = formula.TokenGroup.parse('foo (bar|baz+|(one two))? foo*  foo|bar+',
      implicit_group=True)
  print foo
  # foo.print_matching_tree()
  
  '''
  foo = formula.TokenGroup(['foo', 'bar', 'baz'])
  matcher = foo.build_matcher()
  matcher.send(None)
  print matcher.send('foo')
  print matcher.send('bar')
  print matcher.send('baz')
  print matcher.send('100')
  '''
  
  '''
  foo = formula.RepeatedToken('foo', 2, 5)
  matcher = foo.build_matcher()
  matcher.send(None)
  print matcher.send('foo')
  print matcher.send('foo')
  print matcher.send('foo')
  print matcher.send('foo')
  print matcher.send('foo')
  print matcher.send('foo')
  '''
  
  '''
  foo = formula.TokenGroup(['foo', 'bar+', 'foo*'])
  matcher = foo.build_matcher()
  matcher.send(None)
  print matcher.send('foo')
  print matcher.send('bar')
  print matcher.send('bar')
  print matcher.send('bar')
  print matcher.send('bar')
  print matcher.send('foo')
  '''
  
  foo = formula.OrTokenClause(['foo', 'bar', 'baz'])
  matcher = foo.build_matcher()
  matcher.send(None)
  print matcher.send('foo')
  print matcher.send('bar')
  print matcher.send('baz')
  print matcher.send('100')
  
  # foo.matches_exactly('asd')
  
  # foo = parser.Formula('foo (bar|baz)* foo{1:3} bar? baz')
  # print foo
  # print foo.matching_tree
  # print foo.matches_exactly('foo bar foo foo foo baz')
  # print foo.could_match('foo bar')
  

if __name__ == '__main__':
  main()
