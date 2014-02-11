from flask import Flask
from flask.ext.testing import TestCase

app = Flask(__name__)


class ViewTestCase(TestCase):
  def create_app(self):
    return app
