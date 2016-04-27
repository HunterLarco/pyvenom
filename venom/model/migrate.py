# system imports
import datetime

# package imports
from ..internal.search_yaml import update_search_yaml
from ..internal.search_yaml import load_search_schema
from model import Model

from google.appengine.ext import ndb


__all__ = ['VenomMigrationRecord', 'Migration']


class VenomMigrationRecord(ndb.Model):
  started = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
  finished = ndb.DateTimeProperty(indexed=True)
  schema = ndb.JsonProperty(indexed=False)


class Migration(object):
  records_model = VenomMigrationRecord
  
  def __init__(self):
    self._last_migration = self._get_last_migration()
    self._current_migration = None
    
    self._current_schema = load_search_schema().yaml
    self._last_schema = self._last_migration.schema if self._last_migration else None
    
    if self._requires_migration():
      self._current_migration = self._start_new_migration()
  
  def _requires_migration(self):
    return bool(self._get_added_properties())
  
  def _get_last_migration(self):
    # TODO: also store current migration in memcache
    query = self.records_model.query().order(-self.records_model.started)
    migration = query.get()
    if not migration:
      return None
    if migration.finished == None:
      raise Exception('Migration in progress, cannot instantiate another')
    return migration

  def _start_new_migration(self):
    search_yaml = load_search_schema()
    migration = self.records_model(schema=search_yaml.yaml)
    migration.put()
    return migration
  
  def _extract_kinds(self, schema):
    if not schema: return {}
    kinds = {}
    for kind_obj in schema['indexes']:
      kind = kind_obj['kind']
      kinds[kind] = [ prop['name'] for prop in kind_obj['properties'] ]
    return kinds
  
  def _get_added_properties(self):
    old_kinds = self._extract_kinds(self._last_schema)
    current_kinds = self._extract_kinds(self._current_schema)
    added = {}
    for kind, properties in current_kinds.items():
      if kind in old_kinds:
        old_properties = old_kinds[kind]
        new_properties = list(set(properties) - set(old_properties))
        if new_properties:
          added[kind] = new_properties
      else:
        added[kind] = properties
    return added
  
  def _finish(self):
    self._current_migration.finished = datetime.datetime.now()
    self._current_migration.put()
  
  def run(self, batch_size=200):
    if not self._current_migration:
      return 0
    kinds_updated = 0
    kinds = self._get_added_properties()
    for kind in kinds:
      if kind in Model.kinds:
        model = Model.kinds[kind]
        entities = model.all()
        for i in range(0, len(entities), batch_size):
          group = entities[i: i + batch_size]
          model.save_multi(group)
        kinds_updated += 1
    self._finish()
    return kinds_updated
