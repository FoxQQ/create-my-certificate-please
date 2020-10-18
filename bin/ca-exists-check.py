#!/usr/bin/env python
# coding=utf-8

import os,sys
import time

splunkhome = os.environ['SPLUNK_HOME']
import splunk.Intersplunk

apppath = os.path.join(splunkhome, 'etc', 'apps', 'create-my-certificate-please')
certpath = os.path.join(apppath,'certs')

results = []

files = [f for f in os.listdir(certpath) if 'CA' in f and f.endswith('pem')]
for f in files:
    results.append({"file":f[:-4]})

if(not len(results)): results.append({"file":"none"})

splunk.Intersplunk.outputResults(results)
