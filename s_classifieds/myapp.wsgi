import sys
import os
#s_classifieds_path = "/var/www/html/s_classifieds/s_classifieds"
application_path = os.path.dirname(os.path.realpath(__file__))
if not application_path in sys.path:
    sys.path.insert(0, application_path)

from main import app as application
