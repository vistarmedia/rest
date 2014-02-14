from distutils.core import setup

setup(
  name      = 'rest',
  version   = '0.0.0',
  packages  = ['rest'],

  install_requires = [
    'Flask         == 0.9',
  ],

  tests_require = [
    'Flask-Testing == 0.4',
    'nose          == 1.3.0',
  ],
)
