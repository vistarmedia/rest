from setuptools import setup

setup(
  name      = 'rest',
  version   = '0.0.4',
  packages  = ['rest'],

  install_requires = [
    'Flask         == 1.0.4',
    'unicodecsv    == 0.14.1',
  ],

  test_suite = 'nose.collector',

  tests_require = [
    'Flask-Testing == 0.7.1',
    'nose          == 1.3.7',
  ]
)
