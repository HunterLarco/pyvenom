from google.appengine.ext import ndb
import json
import hashlib


class User(ndb.Model):
  email = ndb.StringProperty()
  password = ndb.StringProperty()
  username = ndb.StringProperty()
  
  def toDict(self):
    return {
      'email': self.email,
      'password': self.password,
      'username': self.username,
      'key': self.key.urlsafe()
    }
  
  @staticmethod
  def hashPassword(password):
    return str(hashlib.sha256(password).hexdigest())
  
  @classmethod
  def signup(cls, email, username, password):
    user = cls(email=email, username=username)
    user.password = cls.hashPassword(password)
    user.put()
    return user
  
  @classmethod
  def login(cls, email, password):
    user = cls.query(cls.email == email).get()
    if not user.password == cls.hashPassword(password):
      return None
    return user

class Session(ndb.Model):
  user = ndb.KeyProperty(User)

class TodoList(ndb.Model):
  name = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
  user = ndb.KeyProperty(User)
  
  def toDict(self):
    return {
      'name': self.name,
      'created': str(self.created),
      'key': self.key.urlsafe()
    }

class Todo(ndb.Model):
  name = ndb.StringProperty()
  todo_list = ndb.KeyProperty(TodoList)
  user = ndb.KeyProperty(User)
  
  def toDict(self):
    return {
      'name': self.name,
      'key': self.key.urlsafe()
    }


class SignupHandler(webapp2.RequestHandler):
  def post(self):
    body = json.loads(self.body)
    user = User.signup(body['email'], body['username'], body['password'])
    self.response.write(json.dumps(user.toDict()))

class LoginHandler(webapp2.RequestHandler):
  def post(self):
    body = json.loads(self.body)
    user = User.login(body['email'], body['password'])
    if not user:
      self.response.write('{}')
    self.response.write(json.dumps(user.toDict())) 

class UserMeHandler(webapp2.RequestHandler):
  def get(self):
    user_key = self.headers['x-session']
    user_key = ndb.Key(urlsafe=user_key)
    user = user_key.get()
    self.response.write(json.dumps(user.toDict()))
  
  def delete(self):
    user_key = self.headers['x-session']
    user_key = ndb.Key(urlsafe=user_key)
    user_key.delete()

class ListsHandler(webapp2.RequestHandler):
  def post(self):
    user_key = self.headers['x-session']
    user_key = ndb.Key(urlsafe=user_key)
    user = user_key.get()
    body = json.loads(self.body)
    todo_list = TodoList(name=body['name'], user=user.key)
    todo_list.put()
    self.response.write(json.dumps(todo_list.toDict()))
  
  def get(self):
    user_key = self.headers['x-session']
    user_key = ndb.Key(urlsafe=user_key)
    self.response.write(json.dumps({
      'entities': map(
        lambda x: x.toDict(),
        TodoList.query(TodoList.user == user_key)
      )
    }))

class SpecificListsHandler(webapp2.RequestHandler):
  def get(self, list_key):
    list_key = ndb.Key(urlsafe=list_key)
    todo_list = list_key.get()
    user_key = self.headers['x-session']
    user_key = ndb.Key(urlsafe=user_key)
    user = user_key.get()
    if todo_list.key != user_key:
      self.error(404)
    self.response.write(json.dumps(todo_list.toDict()))
  
  def put(self, list_key):
    list_key = ndb.Key(urlsafe=list_key)
    todo_list = list_key.get()
    user_key = self.headers['x-session']
    user_key = ndb.Key(urlsafe=user_key)
    user = user_key.get()
    if todo_list.key != user_key:
      self.error(404)
    body = json.loads(self.body)
    todo_list.populate(**body)
    todo_list.put()
    self.response.write(json.dumps(todo_list.toDict()))
  
  def delete(self, list_key):
    list_key = ndb.Key(urlsafe=list_key)
    todo_list = list_key.get()
    user_key = self.headers['x-session']
    user_key = ndb.Key(urlsafe=user_key)
    user = user_key.get()
    if todo_list.key != user_key:
      self.error(404)
    list_key.delete()

class TodoHandler(webapp2.RequestHandler):
  def post(self, list_key):
    list_key = ndb.Key(urlsafe=list_key)
    todo_list = list_key.get()
    body = json.loads(self.body)
    todo = Todo(name=body['name'], todo_list=todo_list.key)
    todo.put()
    self.response.write(json.dumps(todo.toDict()))
  
  def get(self, list_key):
    list_key = ndb.Key(urlsafe=list_key)
    self.response.write(json.dumps({
      'entities': map(lambda x: x.toDict(), Todo.query(Todo.todo_list == list_key))
    }))

class SpecificTodoHandler(webapp2.RequestHandler):
  def get(self, list_key, todo_key):
    todo_key = ndb.Key(urlsafe=todo_key)
    todo = todo_key.get()
    list_key = ndb.Key(urlsafe=list_key)
    if todo.todo_list != list_key:
      self.error(404)
    self.respone.write(json.dumps(todo.toDict()))
  
  def delete(self, list_key, todo_key):
    todo_key = ndb.Key(urlsafe=todo_key)
    todo = todo_key.get()
    list_key = ndb.Key(urlsafe=list_key)
    if todo.todo_list != list_key:
      self.error(404)
    todo_key.delete()


app = webapp2.WSGIApplication([
  ('/users/signup', SignupHandler),
  ('/users/login', LoginHandler),
  ('/users/me', UserMeHandler),
  ('/lists', ListsHandler),
  ('/lists/(\d+)', SpecificListsHandler),
  ('/lists/(\d+)/todo', TodoHandler),
  ('/lists/(\d+)/todo/(\d+)', SpecificTodoHandler)  
], debug=True)
