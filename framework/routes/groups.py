import venom

from app import app
from models import User


class GroupsHandler(venom.RequestHandler):
  def get(self):
    tag = self.url.get('tag')
    if tag == 'children':
      return { 'users': User.children() }
    elif tag == 'adults':
      return { 'users': User.adults() }
    elif tag == 'seniors':
      return { 'users': User.seniors() }
    elif tag == 'discounted':
      return { 'users': User.discounted() }
    return { 'users': User.teenagers() }


app.GET('/groups/:tag', GroupsHandler).url({
  'tag': venom.Parameters.String(choices=[
    'children', 'adults', 'teenagers', 'seniors', 'discounted'
  ])
})
