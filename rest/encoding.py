from __future__ import absolute_import
import sys
import json

from collections import defaultdict
from decimal import Decimal
from xml.etree import ElementTree
import six
from six.moves import map


# This class is for backwards compatability with Python 2.6
# and can be removed whenever that is no longer necessary.
class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return float(obj)
    return json.JSONEncoder.default(self, obj)


class JsonEncoding(object):
  def __init__(self, namespace):
    pass

  def decode(self, request):
    if request.data:
      return json.loads(request.get_data(as_text=True))
    else:
      return {}

  def encode(self, dct):
    cleaned = self._clean_namespace(dct)
    return json.dumps(cleaned, cls=DecimalEncoder)

  def _clean_namespace(self, el):
    if isinstance(el, list):
      return [self._clean_namespace(e) for e in el]
    elif isinstance(el, dict) and '__namespace__' in el:
      el.pop('__namespace__')
    return el


class XmlEncoding(object):
  def __init__(self, namespace):
    self.namespace = namespace

  def decode(self, request):
    return self._decode_str(request.data)

  def encode(self, dct):
    if isinstance(dct, dict):
      root = self.encode_dict(dct)
    elif hasattr(dct, '__iter__'):
      root = self.encode_list(dct)
    else:
      root = self.encode_dict(dct)
    if sys.version_info[0] >= 3:
      return b"<?xml version='1.0' encoding='UTF-8'?>\n" + \
          ElementTree.tostring(root, encoding='UTF-8')
    else:
      return ElementTree.tostring(root, encoding='UTF-8')

  def encode_dict(self, dct):
    return self.dict_to_element_tree(dct)

  def encode_list(self, lst):
    root = ElementTree.Element('items')
    for item in lst:
      root.append(self.dict_to_element_tree(item))
    return root

  def value_to_string(self, v):
    if v == True:
      return 'true'
    if v == False:
      return 'false'

    return str(v)

  def dict_to_element_tree(self, dct):
    if '__namespace__' in dct:
      namespace = dct.pop('__namespace__')
    else:
      namespace = self.namespace
    root = ElementTree.Element(namespace)
    for k, vs in dct.items():
      if not hasattr(vs, '__iter__') or isinstance(vs, str):
        vs = [vs]

      for v in vs:
        element = ElementTree.Element(k)
        if v is not None:
          element.text = self.value_to_string(v)
        root.append(element)
    return root

  def _decode_str(self, string):
    e = ElementTree.XML(string)
    d = dict()
    for values in self.etree_to_dict(e).values():
      d.update(values)
    return d

  def etree_to_dict(self, t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
      dd = defaultdict(list)
      for dc in map(self.etree_to_dict, children):
        for k, v in six.iteritems(dc):
          dd[k].append(v)

      values = {}
      for k, vs in six.iteritems(dd):
        values[k] = vs[0] if len(vs) == 1 else vs
      d = {t.tag: values}
    if t.attrib:
      d[t.tag].update(('@' + k, v) for k, v in six.iteritems(t.attrib))
    if t.text:
      text = t.text.strip()
      if children or t.attrib:
        if text:
          d[t.tag]['#text'] = text
      else:
        d[t.tag] = text
    return d


def encoder(request, namespace='body'):
  best = request.accept_mimetypes.best_match([
    'application/json',
    'text/xml'
  ])

  if best == 'text/xml':
    return XmlEncoding(namespace)
  else:
    return JsonEncoding(namespace)
