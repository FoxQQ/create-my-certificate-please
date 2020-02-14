#!/usr/bin/python

import sys, os
import subprocess
import splunk.Intersplunk
from methods import *

def writeDebugLog(input):
     with open("debug.log", "a") as fh:
         fh.write(str(input)+"\n")

debug=False
try:
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    APP_HOME = os.path.join(SPLUNK_HOME, 'etc/apps/create-my-certificate-please')
    SPLUNK_BIN = os.path.join(SPLUNK_HOME, 'bin/splunk')
    certpath = os.path.join(APP_HOME, 'certs')
    if(not os.path.exists(certpath)):
        os.mkdir(certpath)
except Exception as e:
    if(debug): writeDebugLog(e+"\n")
    sys.exit(1)
finally:
    if(debug): writeDebugLog(certpath)

# we need for certificate creation:
#   CAprivate.key
#   CApublic.pem
#   server.key, .csr & .pem
#   new filename for the stacked cert.pem
# |script generate-server-certs cbconf=0 servername=${caname} pw=${pw} subjstr=/C=${C}/ST=${ST}/L=${L}/O=${O}/OU=${OU}/CN=${CN} email=${email} capw=${pw} caname=${caname}


def noconf():
    if(debug): writeDebugLog("nothing done, all args already in argdict")

if(debug): 
    writeDebugLog("---------------------------------------")
    writeDebugLog(sys.argv)


argdict = parseArgs(sys.argv, display=True)
argdict['SPLUNK_HOME'] = SPLUNK_HOME
argdict['APP_HOME'] = APP_HOME


if(argdict['cbconf']=="1"):
    argdict = useconf(argdict, display=True)
else:
    noconf()

# generate private key for server certs
argdict['caprivatekey'] = argdict['caname'] +'.key'
argdict['capem'] = argdict['caname'] + '.pem'
argdict['serverprivatekey'] = argdict['servername'] + '.key'
if(debug): writeDebugLog(os.path.join(certpath, argdict['serverprivatekey']))
process = subprocess.Popen([
        SPLUNK_BIN,
        'cmd',
        'openssl',
        'genrsa',
        '-aes256',
        '-out',
        os.path.join(certpath, argdict['serverprivatekey']),
        '-passout',
        'pass:'+argdict['pw'],
        '2048'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
if(debug):
    writeDebugLog("private key:")
    writeDebugLog(stderr)

# remove password if cert is for splunkweb
if(argdict['cbsplunkweb'] == '1'):
    if(debug): writeDebugLog("cert for splunkweb")
    process = subprocess.Popen([
        SPLUNK_BIN,
        'cmd',
        'openssl',
        'rsa',
        '-in',
        os.path.join(certpath, argdict['serverprivatekey']),
        '-passin',
        'pass:'+argdict['pw'],
        '-out',
        os.path.join(certpath, argdict['serverprivatekey']),
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if(debug):
        writeDebugLog("removing key pw:")
        writeDebugLog(stderr)
        # logs the decrypted key
        """
        process = subprocess.Popen([
            SPLUNK_BIN,
            'cmd',
            'openssl',
            'rsa',
            '-in',
            os.path.join(certpath, argdict['serverprivatekey']),
            '-passin',
            'pass:'+argdict['pw'],
            '-text'
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        writeDebugLog("  ###  ###  ")
        writeDebugLog(stdout)
        """  
else:
    if(debug): writeDebugLog("cert not for splunkweb")

# create csr file
argdict['servercsr'] = argdict['servername'] + '.csr'
if(debug): writeDebugLog(os.path.join(certpath, argdict['servercsr']))

process = subprocess.Popen([
    SPLUNK_BIN,
    'cmd',
    'openssl',
    'req',
    '-new',
    '-key',
    os.path.join(certpath, argdict['serverprivatekey']),
    '-passin',
    'pass:'+argdict['pw'],
    '-out',
    os.path.join(certpath, argdict['servercsr']),
    '-subj', 
    argdict['subjstr']
    ],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
if(debug):
    writeDebugLog("csr:")
    writeDebugLog(stderr)

# create pem and sign it with out ca
argdict['serverpem'] = argdict['servername'] + '.pem'
process = subprocess.Popen([
    SPLUNK_BIN,
    'cmd',
    'openssl',
    'x509',
    '-req',
    '-in',
    os.path.join(certpath,argdict['servercsr']),
    '-sha512',
    '-CA',
    os.path.join(certpath, argdict['capem']),
    '-CAkey',
    os.path.join(certpath, argdict['caprivatekey']),
    '-passin',
    'pass:'+argdict['capw'],
    '-CAcreateserial',
    '-out',
    os.path.join(certpath,argdict['serverpem']),
    '-days',
    '1095'
    ],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
if(debug):
    writeDebugLog("server.pem:")
    writeDebugLog(stderr)
    writeDebugLog("stdout")
    writeDebugLog(stdout)

# pull it all together in one cert.pem
def getFileContent(fn):
    with open(fn, 'r') as fh:
        return fh.read()

serverpem = getFileContent(os.path.join(certpath, argdict['serverpem']))
serverpk = getFileContent(os.path.join(certpath, argdict['serverprivatekey']))
capem = getFileContent(os.path.join(certpath, argdict['capem']))
with open(os.path.join(certpath, argdict['servername']+'_final.pem'),'w') as fh:
    fh.write(serverpem)
    fh.write(serverpk)
    fh.write(capem)

final = getFileContent(os.path.join(certpath, argdict['servername']+'_final.pem'))

if(os.path.isfile(os.path.join(certpath, argdict['servername']+'_final.pem'))):
    splunk.Intersplunk.outputResults([{"result":os.path.join(certpath,argdict['servername']+'_final.pem')}])
    #splunk.Intersplunk.outputResults([{"content":final}])                                        
else:
    send_list.append({"result":"error"})
    splunk.Intersplunk.outputResults([{"result":"error"}])