from helper import smart_assert, BasicTestCase
from venom.internal.hybrid_model import HybridSearchDocument
import venom

from google.appengine.api import search


class HybridSearchDocumentTests(BasicTestCase):
  index = search.Index('HybridSearchDocumentTests')
  default_fields = [
    search.TextField(name='username', value='test_account'),
    search.NumberField(name='age', value=20.3)
  ]
  new_fields = [
    search.NumberField(name='age', value=89)
  ]
  changed_fields = [
    search.TextField(name='username', value='updated'),
    search.NumberField(name='age', value=12)
  ]
  
  def _create_search_document(self, fields=None):
    document = search.Document(fields=fields if fields else self.default_fields)
    result = self.index.put(document)[0]
    document._doc_id = result.id
    return document
  
  def test_given_no_document(self):
    hybridsearch = HybridSearchDocument(self.index)
    
    assert hybridsearch.has_diff(self.default_fields) == True
    
    assert hybridsearch._loaded_document == False
    assert hybridsearch.get_document() == None
    
    update_document = hybridsearch.get_update_document(self.default_fields)
    assert update_document != None
    assert update_document.doc_id == None
    
    save_result = self.index.put(update_document)[0]
    hybridsearch.register_update(update_document, save_result)
    
    assert hybridsearch._loaded_document == True
    assert hybridsearch.get_document() != None
    assert hybridsearch.has_diff(self.default_fields) == False
  
  def test_given_document(self):
    document = self._create_search_document()
    hybridsearch = HybridSearchDocument(self.index, document=document)
    
    assert hybridsearch._loaded_document == True
    assert hybridsearch.get_document() != None
    
    assert hybridsearch.has_diff(self.default_fields) == False
    assert hybridsearch.has_diff(self.new_fields) == True
    assert hybridsearch.has_diff(self.changed_fields) == True
    
    update_document = hybridsearch.get_update_document(self.new_fields)
    assert update_document != None
    assert update_document.doc_id == hybridsearch.document_id
    
    save_result = self.index.put(update_document)[0]
    hybridsearch.register_update(update_document, save_result)
    
    assert hybridsearch._loaded_document == True
    assert hybridsearch.get_document() != None
    assert hybridsearch.has_diff(self.default_fields) == True
    assert hybridsearch.has_diff(self.new_fields) == False
  
  def test_given_document_id(self):
    document = self._create_search_document()
    hybridsearch = HybridSearchDocument(self.index, document_id=document.doc_id)
    
    assert hybridsearch._loaded_document == False
    assert hybridsearch.get_document() != None
    assert hybridsearch._loaded_document == True
    
    hybridsearch = HybridSearchDocument(self.index, document_id=document.doc_id)
    
    assert hybridsearch.has_diff(self.default_fields) == False
    assert hybridsearch.has_diff(self.new_fields) == True
    assert hybridsearch.has_diff(self.changed_fields) == True
  
  def test_given_bad_document_id(self):
    hybridsearch = HybridSearchDocument(self.index, document_id='foobar')
  
    assert hybridsearch._loaded_document == False
    assert hybridsearch.get_document() == None
    assert hybridsearch._loaded_document == True
    
    assert hybridsearch.has_diff(self.default_fields) == True
    assert hybridsearch.has_diff(self.new_fields) == True
    assert hybridsearch.has_diff(self.changed_fields) == True
    