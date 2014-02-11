from flask import request


def allow_cors(app):
  @app.after_request
  def _allow(response):
    return _add_cors_headers(response)

def allow_cors_domains(app, domains):
  @app.after_request
  def _allow(response):
    if request.headers.get('Origin', '') in domains:
      return _add_cors_headers(response)
    return response

def _add_cors_headers(response):
  origin = request.headers.get('Origin', '*')
  response.headers['Access-Control-Allow-Origin'] = origin
  response.headers['Access-Control-Allow-Credentials'] = 'true'
  response.headers['Access-Control-Allow-Headers'] = \
    'Content-Type, Pragma, Cache-Control, *'
  response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
  return response
