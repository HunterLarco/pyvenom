import venom



app = venom.Application()

app.GET('/test/:thing/and/:thing2', venom.RequestHandler).url({
  'thing': venom.Parameters.String(pattern='[^asd]+')
})
