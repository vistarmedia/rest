from __future__ import absolute_import
from flask import Flask
from flask_testing import TestCase

app = Flask(__name__)


class ViewTestCase(TestCase):
  def create_app(self):
    return app
