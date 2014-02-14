from distutils.core import setup

setup(
  name      = 'rest',
  version   = '0.0.0',
  packages  = ['rest'],

  install_requires = [
    'Flask         == 0.9',
  ],

  tests_require = [
    '-e git+https://github.com/jarus/flask-testing.git@7bf34b039cb93b5447073c12243f9f4debc14a6c#egg=Flask-Testing',
    'Flask-Testing == 0.4',
    'nose          == 1.3.0',
  ],
)
