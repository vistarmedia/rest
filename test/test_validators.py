from unittest import TestCase

from rest.validators import required
from rest.validators import non_falsy_list


class TestValidators(TestCase):

  def test_required(self):
    self.assertIn('is required', required(None))
    self.assertIsNone(required('a little something'))

  def test_non_falsy_list(self):
    self.assertIn('list must contain values', non_falsy_list(['']))
    self.assertIn('list must contain values', non_falsy_list([u'', u'']))
    self.assertIn('list must contain values', non_falsy_list([u'', u'bugs']))
    self.assertIn('list must contain values', non_falsy_list([None]))
    self.assertIn('list must contain values', non_falsy_list([False]))

    self.assertIsNone(non_falsy_list([u'long hots']))

  def test_non_falsy_list_on_empty_list(self):
    self.assertIn('cannot be empty', non_falsy_list([]))
