from setuptools import setup

setup(
  name      = 'rest',
  version   = '0.0.4',
  packages  = ['rest'],

  install_requires = [
    'Flask         == 0.10',
    'unicodecsv    == 0.9.4',
  ],

  test_suite = 'nose.collector',

  tests_require = [
    'Flask-Testing == 0.4.1',
    'nose          == 1.3.0',
  ]
)
