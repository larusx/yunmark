import os, sys, sae
root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(root, 'site-packages'))
from sae.ext.shell import ShellMiddleware

from myapp import app
application = sae.create_wsgi_app(app)
