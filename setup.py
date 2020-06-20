from setuptools import setup

setup(
  name      = 'rest',
  version   = '0.0.4',
  packages  = ['rest'],

  install_requires = [
    'Flask         == 1.0.2',
    'Werkzeug      == 0.16.1',
    'unicodecsv    == 0.14.1',
    'six           == 1.14.0'
  ],

  test_suite = 'nose.collector',

  tests_require = [
    'Flask-Testing == 0.7.1',
    'nose          == 1.3.7',
  ]
)
