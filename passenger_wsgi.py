
import os
import sys


sys.path.insert(0, os.path.dirname(__file__))


def application_this(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    message = 'It works!\n'
    version = 'Python %s\n' % sys.version.split()[0]
    response = '\n'.join([message, version])
    return [response.encode()]


from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_parts.settings")

application = get_wsgi_application()


