from distutils.core import setup

setup(
  name      = 'rest',
  version   = '0.0.1',
  packages  = ['rest'],

  install_requires = [
    'Flask         == 0.10',
  ],

  tests_require = [
    'Flask-Testing == 0.4',
    'nose          == 1.3.0',
  ],
)
