from unittest import TestCase
from nose.exc import SkipTest

class TestModel(TestCase):
  def test_model(self):
    raise SkipTest("not implemented")

# from vistar.model import Advertiser
# from vistar.model import User
# from vistar.model import db
# from vistar.views import rest
# 
# 
# class AdvertiserSchema(rest.Schema):
#   advertiser = rest.Model(Advertiser)
# 
#   id      = rest.ReadOnly(rest.String(advertiser.id))
#   name    = rest.String(advertiser.name)
# 
# class UserSchema(rest.Schema):
#   user = rest.Model(User)
# 
#   id    = rest.ReadOnly(rest.String(user.id))
#   email = rest.String(user.email)
# 
# class TestModel(ViewTestCase):
# 
#   def test_simple_set(self):
#     user = self.create_user(email='user@test.com')
#     db.session.commit()
# 
#     schema = UserSchema(user=user)
#     self.assertEquals('user@test.com', schema.email.get())
#     self.assertTrue(schema.id.get())
# 
#   def test_set(self):
#     advertiser = self.create_advertiser(
#       name   = 'Tester',
#       client = self.user)
# 
#     schema = AdvertiserSchema(advertiser = advertiser)
# 
#     self.assertEquals('Tester', schema.name.get())
#     self.assertTrue(schema({'name': 'Busy!'}))
#     self.assertEquals('Busy!', schema.name.get())
