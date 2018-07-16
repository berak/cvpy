"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""


# only nessecary for running on paas platforms like heroku, or openshift
def application(environ, start_response):
    data = "helo."
    start_response("200 OK", [
            ("Content-Type", "text/html"),
            ("Content-Length", str(len(data)))
            ])
    return iter([data])

#from wsgiref.simple_server import make_server
#httpd = make_server( '0.0.0.0', int(os.environ.get("PORT", 9000)), application )
#while True: httpd.handle_request()
