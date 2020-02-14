#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2015 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

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