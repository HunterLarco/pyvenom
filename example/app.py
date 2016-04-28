import venom
import user


app = venom.Application(packages=user)#, default_auth='X-Authorization')


class TodoList(venom.Model):
  name = venom.Properties.String(min=1)

class Todo(venom.Model):
  name = venom.Properties.String(min=1)
  belongs_to = TodoList


app.CRUD('/lists', TodoList)#.auth(venom.User)
app.CRUD('/lists/:todolist/todo', Todo, domain='todolist')#.auth(venom.User)
