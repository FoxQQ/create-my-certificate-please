#!/usr/bin/python

import sys, os
import subprocess

debug=True
try:
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    APP_HOME = os.path.join(SPLUNK_HOME, 'etc/apps/create-my-certificate-please')
    certpath = os.path.join(APP_HOME, 'certs')
except Exception as e:
    with open('debug.log','a') as fh:
        fh.write(str(e)+"\n")
finally:
    with open('debug.log','a') as fh:
        fh.write(certpath+"\n")

def noconf():
    print("nothing done, all args already in argdict")

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
        with open("debug.log", "a") as fh:
            fh.write(str(e)+"\n")

    
    with open("debug.log", "a") as fh:
        fh.write(str(argdict)+"\n")
    
with open("debug.log", "a") as fh:
    fh.write('---------------------------------------\n')
    fh.write(str(sys.argv)+"\n")

argdict= {}
for arg in sys.argv[1:]:
    args=(arg.split("=", 1))
    argdict[args[0]]=args[1]

if(argdict['cbconf']=="1"):
    useconf()
else:
    noconf()

argdict['caprivatekey'] = argdict['caname'] + '.key'
#run the openssl command to get a new private key
process = subprocess.Popen([os.path.join(os.environ['SPLUNK_HOME'],'bin/splunk'),
            'cmd','openssl','genrsa','-aes256','-out',os.path.join(certpath,argdict['caprivatekey']),
            '-passout','pass:'+argdict['capw'],'2048'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
if (debug): 
    with open("debug.log", "a") as fh:
        fh.write("private key\n")
        fh.write(str(stderr)+"\n")
    print(stderr)
#run openssl and create .rnd file in user home
process = subprocess.Popen([os.path.join(os.environ['SPLUNK_HOME'],'bin/splunk'),'cmd','openssl',
            'rand','-out',os.path.join(os.environ['HOME'],'.rnd'),'-hex','256'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
if (debug): 
    with open("debug.log", "a") as fh:
        fh.write(".rnd file\n")
        fh.write(str(stderr)+"\n")
    print(stderr)
#run openssl and create *.csr
argdict['cacsr'] = argdict['caname'] + '.csr'
process = subprocess.Popen([
    os.path.join(os.environ['SPLUNK_HOME'],'bin/splunk'),
    'cmd',
    'openssl',
    'req',
    '-new',
    '-key',
    os.path.join(certpath,argdict['caprivatekey']),
    '-passin',
    'pass:'+argdict['capw'],
    '-out', 
    os.path.join(certpath,argdict['cacsr']), 
    '-subj', 
    argdict['subjstr']
    ],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
if (debug): 
    with open("debug.log", "a") as fh:
        fh.write(".csr file\n")
        fh.write(str(stderr)+"\n")
    print(stderr)
#finally build ca pem
argdict['capem'] = argdict['caname'] + '.pem'
process = subprocess.Popen([
    os.path.join(os.environ['SPLUNK_HOME'],'bin/splunk'),
    'cmd',
    'openssl',
    'x509',
    '-req',
    '-in',os.path.join(certpath,argdict['cacsr']),
    '-sha512',
    '-signkey',os.path.join(certpath,argdict['caprivatekey']),
    '-passin', 'pass:'+argdict['capw'],
    '-CAcreateserial',
    '-out',os.path.join(certpath,argdict['capem']),
    '-days','1095'
    ],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
if (debug): 
    with open("debug.log", "a") as fh:
        fh.write(".pem file\n")
        fh.write(str(stderr)+"\n")
    print(stderr)


