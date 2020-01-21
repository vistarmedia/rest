from __future__ import absolute_import
import json
import unittest

from flask import Flask
from flask import request
from flask_testing import TestCase
from werkzeug.datastructures import Headers

import rest


class TestXmlEncoding(unittest.TestCase):
  def setUp(self):
    super(TestXmlEncoding, self).setUp()
    self.codec = rest.encoding.XmlEncoding('body')

  def test_basic_decode(self):
    body = '<x><hello>world</hello></x>'
    self.assertEquals({'hello': 'world'}, self.codec._decode_str(body))

  def test_multi_root(self):
    body = '''
      <xml-rules>
        <hello>world</hello>
        <goodbye>yellowbrick road</goodbye>
      </xml-rules>
    '''
    d = self.codec._decode_str(body)
    self.assertEquals(2, len(d))
    self.assertEquals('world', d['hello'])
    self.assertEquals('yellowbrick road', d['goodbye'])

  # http://en.wikipedia.org/wiki/Huey_Long
  def test_every_man_a_string(self):
    body = '''
      <xml>
        <string>hi</string>
        <number>12</number>
      </xml>
    '''
    d = self.codec._decode_str(body)
    self.assertEquals(2, len(d))
    self.assertEquals('hi', d['string'])
    self.assertEquals('12', d['number'])

  def test_list_value(self):
    xml = self.codec.encode({
      'age':      23,
      'name':     'steve',
      'friends':  ['bob', 'frank']
    })

    self.assertTrue('<friends>bob</friends>' in xml)
    self.assertTrue('<friends>frank</friends>' in xml)
    self.assertTrue('<name>steve</name>' in xml)

  def test_none_value(self):
    xml = self.codec.encode({
      'name':     'steve',
      'income':   None,
    })

    self.assertTrue('None' not in xml)
    self.assertTrue('<name>steve</name>' in xml)
    self.assertTrue('<income />' in xml)

  def test_boolean_value(self):
    xml = self.codec.encode({'cool': True})
    self.assertTrue('<cool>true</cool>' in xml)

  def test_json_excludes_namespace(self):
    codec = rest.encoding.JsonEncoding('ns')
    dct = {
      'name':           'Steve',
      '__namespace__':  'Buds',
    }
    self.assertEquals('{"name": "Steve"}', codec.encode(dct))


class TestEncoding(TestCase):
  def setUp(self):
    self.last_payload = None
    self.last_request = None

    @self.app.route('/echo', methods=['POST'])
    @rest.view
    def echo(data):
      self.last_request = request
      self.last_payload = data
      return dict(data)

    @self.app.route('/error')
    @rest.view
    def error():
      return rest.error({
        'name':           ['field is required'],
        'motown_philly':  ['too hard', 'too soft'],
      })

  def create_app(self):
    self.app = Flask('TestEncoding')
    self.app.debug = True
    return self.app

  def test_simple_json_echo(self):
    resp = self.client.post('/echo', data=json.dumps({'hello': 'world'}))

    self.assertEquals({'hello': 'world'}, self.last_payload)
    self.assertEquals('{"hello": "world"}', resp.get_data(as_text=True))

  def test_simple_xml_echo(self):
    resp = self.client.post('/echo',
      data    = '''
        <body>
          <hello>world</hello>
        </body>
      ''',
      headers = self._accept('text/xml'))

    xml = resp.get_data(as_text=True).split('\n')[1]
    self.assert200(resp)
    self.assertEquals({'hello': 'world'}, self.last_payload)
    self.assertEquals('<body><hello>world</hello></body>', xml)

  def test_xml_preamble(self):
    resp = self.client.post('/echo',
      data = '''
        <body>
          <hello>world</hello>
        </body>
      ''',
      headers = self._accept('text/xml'))
    preamble = resp.get_data(as_text=True).split('\n')[0]
    self.assertEquals("<?xml version='1.0' encoding='unicode'?>", preamble)

  def test_schema_name_returned_for_xml(self):
    class UserSchema(rest.Schema):
      id      = rest.String()
      name    = rest.String()

    @self.app.route('/userz')
    @rest.view
    def users():
      return UserSchema(id='12', name='Frank')

    resp = self.client.get('/userz', headers=self._accept('text/xml'))
    xml = resp.get_data(as_text=True).split('\n')[1]
    self.assertTrue(xml.startswith('<User>'))
    self.assertTrue(xml.endswith('</User>'))

  def test_errors_in_json(self):
    resp = self.client.get('/error')
    self.assert400(resp)
    body = json.loads(resp.get_data(as_text=True))
    self.assertEquals(['too hard', 'too soft'], body['motown_philly'])
    self.assertEquals(['field is required'], body['name'])

  def test_errors_in_xml(self):
    resp = self.client.get('/error', headers=self._accept('text/xml'))
    self.assert400(resp)
    xml = resp.get_data(as_text=True).split('\n')[1]
    self.assertTrue(xml.startswith('<errors>'))
    self.assertTrue(xml.endswith('</errors>'))
    self.assertTrue('<motown_philly>too hard</motown_philly>' in xml)
    self.assertTrue('<motown_philly>too soft</motown_philly>' in xml)
    self.assertTrue('<name>field is required</name>' in xml)

  def _accept(self, accept):
    headers = Headers()
    headers.add('Accept', accept)
    return headers
