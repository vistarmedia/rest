from __future__ import absolute_import
import locale

from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from nose.tools import raises
from nose.tools import assert_raises

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

  @raises(ValueError)
  def test_set_none_on_field(self):
    field = fields.ReadOnly(fields.String('hi'))

    field.set(None)

  @raises(Exception)
  def test_write_only(self):
    field = fields.WriteOnly(fields.String('hi'))

    self.assertFalse(field.serialize)
    field.get()

  def test_string_coercion(self):
    self.assertEquals('String', fields.String().coerce('String'))
    self.assertEquals('True', fields.String().coerce(True))
    self.assertEquals('None', fields.String().coerce(None))

  def test_string_coercion_with_unicode(self):
    self.assertEquals(u'H\xc3\xa4nsel',
        fields.String().coerce(u'H\xc3\xa4nsel'))

  def test_string_coercion_with_trim_to(self):
    self.assertEquals('19103', fields.String(trim_to=5).coerce('19103-1212'))

  def test_none_string_coercion_with_trim_to(self):
    self.assertEquals('666', fields.NoneString(trim_to=3).coerce('666123'))

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
    locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
    self.assertEquals(4, fields.Int().coerce(Decimal(4.2)))
    self.assertEquals(4, fields.Int().coerce(float(4.2)))
    self.assertEquals(4, fields.Int().coerce(4))
    self.assertEquals(4, fields.Int().coerce(u'4'))
    self.assertEquals(4, fields.Int().coerce('4'))
    self.assertEquals(0, fields.Int().coerce(''))
    self.assertEquals(1000000, fields.Int().coerce('1,000,000'))

  def test_none_int_coercion(self):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
    self.assertEquals(4, fields.NoneInt().coerce(Decimal(4.2)))
    self.assertEquals(4, fields.NoneInt().coerce(float(4.2)))
    self.assertEquals(4, fields.NoneInt().coerce(4))
    self.assertEquals(4, fields.NoneInt().coerce(u'4'))
    self.assertEquals(4, fields.NoneInt().coerce('4'))
    self.assertEquals(0, fields.NoneInt().coerce('0'))
    self.assertEquals(0, fields.NoneInt().coerce(0))
    self.assertEquals(None, fields.NoneInt().coerce(''))
    self.assertEquals(None, fields.NoneInt().coerce(None))
    self.assertEquals(1000000, fields.NoneInt().coerce('1,000,000'))

  def test_float_coercion(self):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
    self.assertEquals(4.02, fields.Float().coerce(Decimal(4.02)))
    self.assertEquals(4.02, fields.Float().coerce(float(4.02)))
    self.assertEquals(4.02, fields.Float().coerce(u'4.02'))
    self.assertEquals(4.02, fields.Float().coerce('4.02'))
    self.assertEquals(0, fields.Float().coerce(''))
    self.assertEquals(1000000.01, fields.Float().coerce('1,000,000.01'))

  def test_dollars_coercion(self):
    self.assertEquals(Decimal('1.10'), fields.Dollars().coerce('1.10'))
    self.assertEquals(Decimal('1.10'), fields.Dollars().coerce(1.10))

  def test_list_coercion(self):
    self.assertIn('1', fields.List().coerce(['1', '2', '3']))
    self.assertIn('2', fields.List().coerce(['1', '2', '3']))
    self.assertIn('3', fields.List().coerce(['1', '2', '3']))

  def test_list_coercion_with_options_list(self):
    list_coerce = fields.List(options=['bigdog', 'strodog']).coerce

    assert_raises(ValueError, list_coerce, ['smalldog'])
    assert_raises(ValueError, list_coerce, ['strodog', 'smalldog'])
    self.assertIn('strodog', list_coerce(['strodog', 'bigdog']))
    self.assertIn('bigdog', list_coerce(['strodog', 'bigdog']))

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

  def test_truthy_only_list(self):
    list_with_some_falsies = ['', 'dogs', 'food', '', 'crime', None, 5]
    self.assertEquals(4,
        len(fields.TruthyOnlyList().coerce(list_with_some_falsies)))

  def test_email_validation(self):
    error = ['must be a valid email']
    self.assertEquals(error, fields.Email('bademail').validate())
    self.assertEquals(error, fields.Email('noat.com').validate())
    self.assertEquals(error, fields.Email('notld@somewhere').validate())

    self.assertEquals([], fields.Email('valid@email.com').validate())
