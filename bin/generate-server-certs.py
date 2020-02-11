#!/usr/bin/python

import sys, os
import subprocess
import splunk.Intersplunk


def writeDebugLog(input):
     with open("debug.log", "a") as fh:
         fh.write(str(input)+"\n")

debug=True
try:
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    APP_HOME = os.path.join(SPLUNK_HOME, 'etc/apps/create-my-certificate-please')
    SPLUNK_BIN = os.path.join(SPLUNK_HOME, 'bin/splunk')
    certpath = os.path.join(APP_HOME, 'certs')
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

def useconf():
    argdict['confpath'] = argdict['confpath'].replace('$SPLUNK_HOME', SPLUNK_HOME)
    try:
        with open(argdict['confpath'], "r") as fh:
            argdict['subjstr'] = ""
            for line in fh:
                args = line.replace("\n","").split('=', 1)
                if(args[0]=='C'):
                    argdict['subjstr'] += "/C=" + args[1]
                elif(args[0]=='ST'):
                    argdict['subjstr'] += "/ST=" +args[1]
                elif(args[0]=='L'):
                    argdict['subjstr'] += "/L=" +args[1]
                elif(args[0]=='O'):
                    argdict['subjstr'] += "/O=" +args[1]
                elif(args[0]=='OU'):
                    argdict['subjstr'] += "/OU=" + args[1]
                elif(args[0]=='CN'):
                    argdict['subjstr'] += "/CN=" + args[1]
                argdict[args[0]] = args[1]
    except Exception as e:
        if(debug): writeDebugLog(e)

if(debug): 
    writeDebugLog("---------------------------------------")
    writeDebugLog(sys.argv)

argdict= {}
if(len(sys.argv) <=1):
    sys.exit(1)
for arg in sys.argv[1:]:
    args=(arg.split("=", 1))
    argdict[args[0]]=args[1]

if(argdict['cbconf']=="1"):
    useconf()
else:
    noconf()

# generate private key for server certs
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
print(os.path.join(certpath, argdict['caname'][:-4]+'.key'))
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
    os.path.join(certpath, argdict['caname']),
    '-CAkey',
    os.path.join(certpath, argdict['caname'][:-4]+'.key'),
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

# pull it all together in one cert.pem
def getFileContent(fn):
    with open(fn, 'r') as fh:
        return fh.read()
serverpem = getFileContent(os.path.join(certpath, argdict['serverpem']))
serverpk = getFileContent(os.path.join(certpath, argdict['serverprivatekey']))
capem = getFileContent(os.path.join(certpath, argdict['caname']))
with open(os.path.join(certpath, argdict['servername']+'_final.pem'),'w') as fh:
    fh.write(serverpem)
    fh.write(serverpk)
    fh.write(capem)

final = getFileContent(os.path.join(certpath, argdict['servername']+'_final.pem'))

if(os.path.isfile(os.path.join(certpath, argdict['servername']+'_final.pem'))):
    splunk.Intersplunk.outputResults([{"result":os.path.join(certpath,argdict['servername']+'_final.pem')}])
    splunk.Intersplunk.outputResults([{"content":final}])                                        
else:
    send_list.append({"result":"error"})
    splunk.Intersplunk.outputResults([{"result":"error"}])