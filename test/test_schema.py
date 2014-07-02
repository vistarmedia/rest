from datetime import datetime
from unittest import TestCase

import rest


class FriendSchema(rest.Schema):
  name  = rest.String()
  age   = rest.Int()


class TestSchema(TestCase):

  def test_copy_fields_from_static_to_instance(self):
    class NameSchema(rest.Schema):
      first_name = rest.String()
      last_name  = rest.String()

    name_one = NameSchema()
    self.assertEquals(None, name_one.first_name.get())
    name_one.first_name.set('Firsty')
    name_one.last_name.set('Lasterson')

    name_two = NameSchema()
    self.assertEquals(None, name_two.first_name.get())

  def test_simple_validators(self):
    class CoolSchema(rest.Schema):
      name  = rest.String(validators = [
        rest.required
      ])

    schema = CoolSchema()
    self.assertFalse(schema({}))
    self.assertEquals(1, len(schema._errors))
    self.assertEquals(['is required'], schema._errors['name'])

  def test_length_validator(self):
    class LengthSchema(rest.Schema):
      min_field = rest.String(validators=[rest.length(min=4)])
      max_field = rest.String(validators=[rest.length(max=2)])

    schema = LengthSchema()
    self.assertFalse(schema({'min_field': '123', 'max_field': '321'}))
    self.assertEquals(2, len(schema._errors))
    self.assertEquals('cannot be less than 4 characters',
      schema._errors['min_field'][0])
    self.assertEquals('cannot be greater than 2 characters',
      schema._errors['max_field'][0])

  def test_regex_validator(self):
    class RegexSchema(rest.Schema):
      zip_code = rest.String(validators=[
        rest.regex('[0-9]{5}', 'not a valid Zip')
      ])

      state = rest.String(validators=[
        rest.regex('[A-Z]{2}', 'not a valid State')
      ])

    schema = RegexSchema()
    self.assertFalse(schema({'zip_code': 'BAD', 'state': 'PA'}))
    self.assertEquals(1, len(schema._errors))
    self.assertEquals(['not a valid Zip'], schema._errors['zip_code'])

  def test_serialized_set(self):
    schema = FriendSchema()

    self.assertFalse(schema.name.get(), 'unexpected %r' % schema.name.get())
    self.assertFalse(schema.age.get())

    self.assertTrue(schema({'age': '23'}))
    self.assertEquals(23, schema.age.get())

  def test_serialization_error(self):
    schema = FriendSchema()
    self.assertFalse(schema({'age': 'pants'}))
    errors = schema._errors

    age_errors = errors.get('age')
    self.assertEquals(["Invalid integer"], age_errors)

  def test_extra_population_params(self):
    schema = FriendSchema()
    self.assertTrue(schema({'name': 'Bob', 'unused': 'Seriously'}))

  def test_complex_serialized_set(self):
    class PersonSchema(rest.Schema):
      first_name = rest.String()
      last_name  = rest.String()
      dob        = rest.DateTime()

    schema = PersonSchema()
    self.assertTrue(schema({'first_name': 'Mike'}))
    self.assertTrue(schema({'last_name':  'Rotch'}))
    self.assertTrue(schema({'dob': '2012-04-20T16:20:01.101000Z'}))

    self.assertEquals(datetime(2012, 4, 20, 16, 20, 1, 0),
                      schema.dob.get())

    self.assertEquals({'first_name':    'Mike',
                       'last_name':     'Rotch',
                       'dob':           '2012-04-20T16:20:01.000000Z',
                       '__namespace__': 'Person'},
                      schema._get())

  def test_defaults(self):
    class PersonSchema(rest.Schema):
      first_name = rest.String(default='John')
      last_name  = rest.String(default='Doe')
      money      = rest.Dollars(default='10')

    schema = PersonSchema()
    schema()
    self.assertEquals({'first_name':    'John',
                       'last_name':     'Doe',
                       'money':         '10.00',
                       '__namespace__': 'Person'},
                      schema._get())

    schema = PersonSchema()
    schema({'first_name': 'Bob'})
    self.assertEquals({'first_name':    'Bob',
                       'last_name':     'Doe',
                       'money':         '10.00',
                       '__namespace__': 'Person'},
                      schema._get())

  def test_implied_name(self):
    class PantsSchema(rest.Schema):
      pass
    self.assertEquals('Pants', PantsSchema().get_namespace())

  def test_overridden_name(self):
    class PantsSchema(rest.Schema):
      __namespace__ = 'Shorts'
    self.assertEquals('Shorts', PantsSchema().get_namespace())
