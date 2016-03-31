import json
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, tostring


class Protocol(object):
  def __init__(self, headers=None):
    self.headers = headers if headers else {}
  
  def read(self, string):
    pass
  
  def write(self, webapp2_response, error):
    webapp2_response.headers = self.headers
    webapp2_response.clear()


class TextProtocol(Protocol):
  def __init__(self, data, headers=None):
    super(TextProtocol, self).__init__(headers)
    self.data = data
  
  def read(self, string):
    super(TextProtocol, self).read(string)
    return string
  
  def write(self, webapp2_response, error):
    super(TextProtocol, self).write(webapp2_response, error)
    webapp2_response.write(str(self.data))


class JSONProtocol(Protocol):
  def __init__(self, data, headers=None):
    super(JSONProtocol, self).__init__(headers)
    self.headers['Content-Type'] = 'application/json'
    self.data = data
  
  def read(self, string):
    super(JSONProtocol, self).read(string)
    return json.loads(string)
  
  def write(self, webapp2_response, error):
    super(JSONProtocol, self).write(webapp2_response, error)
    webapp2_response.write(json.dumps(self.data, indent=2))


class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})


class XMLProtocol(Protocol):
  def __init__(self, data, headers=None):
    super(XMLProtocol, self).__init__(headers)
    self.headers['Content-Type'] = 'application/xml'
    self.data = data
  
  def xml_to_dict(self, xmlstring):
    root = ElementTree.XML(xmlstring)
    xmldict = XmlDictConfig(root)
    return xmldict
  
  def dict_to_xml(self, d, root=None):
    root = root if root is not None else []
    for key, value in d.items():
      child = Element(key)
      if isinstance(value, dict):
        self.dict_to_xml(value, root=child)
      elif isinstance(value, list):
        for item in value:
          self.dict_to_xml(item, root=child)
      else:
        child.text = str(value)
      root.append(child)
    return root
  
  def xml_to_string(self, xml):
    if isinstance(xml, list):
      xml = map(lambda x: self.xml_to_string(x), xml)
      return '\n'.join(xml)
    rough_string = tostring(xml)
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ')
  
  def read(self, string):
    super(XMLProtocol, self).read(string)
    return self.xml_to_dict(string)
  
  def write(self, webapp2_response, error):
    super(XMLProtocol, self).write(webapp2_response, error)
    xml = self.dict_to_xml(self.data)
    xml_str = self.xml_to_string(xml)
    webapp2_response.write(xml_str)

    
