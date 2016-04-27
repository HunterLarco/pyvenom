__all__ = ['ui']


class ui(object):
  def __init__(self, route, guid):
    self.route = route
    self.guid = guid
    self.set_guid(route, guid)
  
  @staticmethod
  def set_guid(obj, guid):
    setattr(obj, 'ui.guid', guid)
  
  @staticmethod
  def get_guid(obj):
    if not hasattr(obj, 'ui.guid'):
      return None
    return getattr(obj, 'ui.guid')