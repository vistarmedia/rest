# -*- coding: utf-8 -*-
from StringIO import StringIO

from flask import Flask
from flask.ext.testing import TestCase
from json import loads
from nose.plugins.skip import SkipTest

import rest

from test import ViewTestCase

from rest.schema import Schema


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


class TestCSVUpload(TestCase):
  def setUp(self):
    self.seen_dog_names = []

    self.csv_headers = {
      'content-type': 'multipart/form-data'
    }

    class CSVSchema(Schema):
      dog_type = rest.String(validators=[rest.nonempty])
      food     = rest.String(validators=[rest.nonempty])
      pounds   = rest.Int()


    @self.app.route('/csv', methods=['POST'])
    @rest.csv_upload(CSVSchema)
    def csv(rows):
      for schema in rows:
        self.seen_dog_names.append(schema.dog_type.get())
      return rest.created({'csv': 'created'})

  def create_app(self):
    self.app = Flask('TestCSVUpload')
    return self.app

  def test_csv_upload_with_empty_request_body(self):
    """
    it should 400 if no expecting csv but got empty body
    """
    resp = self.client.post('/csv', headers=self.csv_headers)

    self.assert400(resp)

  def test_csv_upload_with_invalid_data(self):
    """
    it should 400 if data being upload violates schema, returning errors by
    column name
    """
    data = "dog_type,food,pounds\n" \
      "great dane,cured meats,200\n" \
      "cerberus,,1500\n" \
      "shibe,doge food,20\n" \
      "'strodog,kibble,65"

    resp = self.client.post('/csv', data={
      'file': (StringIO(data), 'test.csv')}, headers=self.csv_headers)

    self.assert400(resp)
    body = loads(resp.data)

    self.assertIn('cannot be empty', body['food'])

  def test_csv_upload_with_valid_data(self):
    data = "dog_type,food,pounds\n" \
      "great dane,cured meats,200\n" \
      "cerberus,souls,1500\n" \
      "shibe,doge food,20\n" \
      "'strodog,kibble,65"

    resp = self.client.post('/csv', data={
      'file': (StringIO(data), 'test.csv')}, headers=self.csv_headers)

    self.assert_status(resp, 201)

  def test_csv_upload_with_valid_data_gives_view_rows_generator(self):
    """
    it should give the view function a rows generator object which yields one
    rest.Schema for each row
    """
    data = "dog_type,food,pounds\n" \
      "great dane,cured meats,200\n" \
      "cerberus,live meat ONLY,1500\n" \
      "shibe,doge food,20\n" \
      "'strodog,kibble,65\n"

    resp = self.client.post('/csv', data={
      'file': (StringIO(data), 'test.csv')}, headers=self.csv_headers)

    self.assert_status(resp, 201)

    expected_dog_names = ('great dane', 'cerberus', 'shibe', "'strodog")
    self.assertEqual(4, len(self.seen_dog_names))

    for name in self.seen_dog_names:
      self.assertIn(name, expected_dog_names)

  def test_csv_upload_with_unicode_body(self):
    """
    it should not raise an exception on receiving unicode chars
    """
    data = "dog_type,food,pounds\n" \
      "foxes,cured meats,3200\n" \
      "H\xc3\xa4nsel,pies,1500\n" \
      "ni\xc3\xb1o,foods,43\n"

    resp = self.client.post('/csv',
      data={'file': (StringIO(data), 'test.csv')},
      headers=self.csv_headers)

    self.assert_status(resp, 201)
    self.assertIn(u'Hänsel', self.seen_dog_names)
    self.assertIn(u'niño', self.seen_dog_names)
    self.assertIn(u'foxes', self.seen_dog_names)
