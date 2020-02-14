#!/usr/bin/python

import sys, os
import subprocess
import splunk.Intersplunk
from methods import *


debug=False
try:
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    APP_HOME = os.path.join(SPLUNK_HOME, 'etc/apps/create-my-certificate-please')
    SPLUNK_BIN = os.path.join(SPLUNK_HOME, 'bin/splunk')
    certpath = os.path.join(APP_HOME, 'certs')
    if(not os.path.exists(certpath)):
        os.mkdir(certpath)
    appspath = os.path.join(APP_HOME, 'apps')
    if(not os.path.exists(appspath)):
        os.mkdir(appspath)
except Exception as e:
    if(debug): writeDebugLog(e+"\n")
    sys.exit(1)

argdict = parseArgs(sys.argv, display=True)
argdict['SPLUNK_HOME'] = SPLUNK_HOME
argdict['appspath'] = appspath
argdict['APP_HOME'] = APP_HOME
argdict = useconf(argdict, display=True)
app = App(argdict)