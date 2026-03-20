import sys
import os

# PythonAnywhere uchun path
project_home = '/home/SIZNING_USERNAME/zomin-market'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application
