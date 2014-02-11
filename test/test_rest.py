from flask import Flask
from flask.ext.testing import TestCase
from json import loads
from nose.plugins.skip import SkipTest

import rest

from test import ViewTestCase


class TestRest(ViewTestCase):

  def test_simple_serialize(self):
    self.assertEquals('{"simple": "json"}', rest._serialize({'simple': 'json'}))
    self.assertEquals('["a list", 1]', rest._serialize(["a list", 1]))

class TestSimpleApp(TestCase):
  def setUp(self):
    self.last_post = None

    @self.app.route('/post', methods=['POST'])
    @rest.view
    def post(data):
      self.last_post = data
      return dict(data)

  def create_app(self):
    self.app = Flask('TestSimpleApp')
    return self.app

  def test_utf8_body(self):
    body = '{"hi": "Nina\u2019s"}'
    resp = self.client.post('/post', data=body)
    self.assert200(resp)

    self.assertEquals(u'Nina\u2019s', loads(resp.data)['hi'])
    self.assertEquals(u'Nina\u2019s', self.last_post['hi'])

  def test_unicode_without_encoding_header(self):
    raise SkipTest
    body = u'{"hi": "L\u2019Acadie pour Elle"}'
    resp = self.client.post('/post', data=body)
    self.assertEquals(400, resp.status_code)
    body = loads(resp.data)
    self.assertEquals({
      'client': ['Expecting property name: line 1 column 1 (char 1)']
    }, body)
