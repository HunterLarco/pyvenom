import venom


app = venom.Application()


import user

class TodoList(venom.Model):
  name = venom.Properties.String(min=1)
  created = venom.Properties.DateTime(set_on_creation=True)

class Todo(venom.Model):
  name = venom.Properties.String(min=1)


app.CRUD('/lists', TodoList).domain.headers({
  'User': user.UserAuthProperty()
})

app.CRUD('/lists/:list/todo', Todo).domain.url({
  'list': venom.Properties.Model(TodoList, required=True)
}).headers({
  'User': user.UserAuthProperty()
})
