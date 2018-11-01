#!/usr/bin/env python
import sys, os, pwd, grp, signal, time
from resource_management import *
from subprocess import call
from common import *

def setup_dremio():
    import params
    import status_params
    Logger.info("Configure Dremio Service")
