import sys
import os
import urllib2
from urllib2 import URLError
import httplib
import socket
import time
from urlparse import urlparse
from copy import deepcopy
import re

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

import ssl
sys.path.append(os.path.dirname(__file__))
import js2py
