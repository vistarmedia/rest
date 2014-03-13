from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from nose.tools import raises

from rest import fields


class FieldTest(TestCase):

  def test_basic_field(self):
    class BasicField(fields.Field):
      pass

    field = BasicField('value')
    self.assertEquals('value', field.get())
    field.set('another value')
    self.assertEquals('another value', field.get())

  def test_reset(self):
    field = fields.String()

    self.assertEquals(None, field.get())
    field.reset()
    self.assertEquals(None, field.get())

    field.set('set')
    self.assertEquals('set', field.get())
    field.reset()
    self.assertEquals(None, field.get())

  @raises(ValueError)
  def test_read_only(self):
    field = fields.ReadOnly(fields.String('hi'))
    self.assertEquals('hi', field.get())

    field.set('bye')

  @raises(Exception)
  def test_write_only(self):
    field = fields.WriteOnly(fields.String('hi'))

    self.assertFalse(field.serialize)
    field.get()

  def test_string_coercion(self):
    self.assertEquals('String', fields.String().coerce('String'))
    self.assertEquals('True', fields.String().coerce(True))
    self.assertEquals('None', fields.String().coerce(None))

  def test_boolean_coercion(self):
    self.assertTrue(fields.Bool().coerce(True))
    self.assertFalse(fields.Bool().coerce(False))

    self.assertTrue(fields.Bool().coerce(1))
    self.assertFalse(fields.Bool().coerce(0))

    self.assertTrue(fields.Bool().coerce('ok'))
    self.assertFalse(fields.Bool().coerce(''))

    self.assertTrue(fields.Bool().coerce(['ok']))
    self.assertFalse(fields.Bool().coerce([]))

    self.assertTrue(fields.Bool().coerce({'is': 'ok'}))
    self.assertFalse(fields.Bool().coerce({}))

  def test_string_boolean_coercion(self):
    self.assertTrue(fields.StringBool().coerce('True'))
    self.assertFalse(fields.StringBool().coerce('False'))

    self.assertTrue(fields.StringBool().coerce('tRue'))
    self.assertFalse(fields.StringBool().coerce('false'))

  @raises(ValueError)
  def test_string_boolean_coercion_empty_string(self):
    self.assertTrue(fields.StringBool().coerce(''))

  def test_int_coercion(self):
    self.assertEquals(4, fields.Int().coerce('4'))
    self.assertEquals(0, fields.Int().coerce(''))

  def test_dollars_coercion(self):
    self.assertEquals(Decimal('1.10'), fields.Dollars().coerce('1.10'))
    self.assertEquals(Decimal('1.10'), fields.Dollars().coerce(1.10))

  def test_datetime_coercion(self):
    self.assertEquals(datetime(2012, 4, 20, 16, 20, 0, 0),
                      fields.DateTime().coerce("2012-04-20T16:20:00.000Z"))

    self.assertEquals(datetime(2012, 4, 20, 16, 20, 1, 0),
                      fields.DateTime().coerce("2012-04-20T16:20:01.10100Z"))

    self.assertEquals(datetime(2012, 4, 20, 16, 20, 1, 0),
                      fields.DateTime().coerce("2012-04-20T16:20:01Z"))

  def test_simple_serialization(self):
    self.assertEquals('True', fields.String().simplify('True'))
    self.assertEquals(True, fields.Bool().simplify(True))
    self.assertEquals(10, fields.Int().simplify(10))

  def test_datetime_serialization(self):
    self.assertEquals("2012-04-20T16:20:01.101000Z",
                      fields.DateTime()
                      .simplify(datetime(2012, 4, 20, 16, 20, 1, 101000)))
    self.assertEquals("2012-04-20T16:20:01.101001Z",
                      fields.DateTime()
                      .simplify(datetime(2012, 4, 20, 16, 20, 1, 101001)))

  def test_decimal_serialization(self):
    self.assertEquals('1.00', fields.Dollars().simplify(Decimal('1.00')))
    self.assertEquals('1.00', fields.Dollars().simplify(Decimal('1')))
