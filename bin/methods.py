import os, sys
from shutil import copyfile

def writeDebugLog(input):
     with open("debug.log", "a") as fh:
         fh.write(str(input)+"\n")


def parseArgs(sysargs, display=False):
    argdict= {}
    if(len(sysargs) <=1):
        sys.exit(1)
    for arg in sysargs[1:]:
        args=(arg.split("=", 1))
        argdict[args[0]]=args[1]
    if(display):
        writeDebugLog(argdict)
    return argdict

def useconf(argdict, display=False):
    argdict['confpath'] = argdict['confpath'].replace('$SPLUNK_HOME', argdict['SPLUNK_HOME'])
    try:
        with open(argdict['confpath'], "r") as fh:
            argdict['subjstr'] = ""
            for line in fh:
                args = line.replace("\n","").replace("\r","").split('=', 1)
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
                elif(args[0]=='' or args[0].startswith('#')):
                    continue
                argdict[args[0]] = args[1]
    except Exception as e:
        if(display): writeDebugLog(e)
    finally:
        if(display): writeDebugLog(argdict)
        return argdict

class App():
    argdict = {}
    def __init__(self, argdict):
        if (not bool(argdict)):
            writeDebugLog("is empty")
            return
        else:
            writeDebugLog("ok")
        self.argdict = argdict
        if(self.argdict['apptype'] == 'sender'):
            self.mkemptyApp(os.path.join(self.argdict['appspath'], self.argdict['servername'] + '_outputs_app'))
            self.mkInputs()            
        elif(self.argdict['apptype'] == 'receiver'):
            self.mkemptyApp(os.path.join(self.argdict['appspath'], self.argdict['servername'] + '_inputs_app'))
            self.mkOutputs()
        self.mkServer()
        self.pullCerts()

    def pullCerts(self):
        capem_src = os.path.join(self.argdict['APP_HOME'], 'certs',self.argdict['caname']+'.pem')
        serverpem_src = os.path.join(self.argdict['APP_HOME'], 'certs',self.argdict['servername']+'_final.pem')
        capem_dest = os.path.join(self.argdict['certs'], self.argdict['caname']+'.pem')
        serverpem_dest = os.path.join(self.argdict['certs'],self.argdict['servername']+'_final.pem')
        copyfile(capem_src, capem_dest)
        copyfile(serverpem_src, serverpem_dest)

    def mkemptyApp(self, path):
        if(path == ""):
            return 1
        if(not os.path.exists(path)):
            os.mkdir(path)
        if(not os.path.exists(os.path.join(path, 'local'))):
            os.mkdir(os.path.join(path, 'local'))
        if(not os.path.exists(os.path.join(path, 'certs'))):
            os.mkdir(os.path.join(path, 'certs'))
        self.argdict['local'] = os.path.join(path, 'local')
        self.argdict['certs'] = os.path.join(path, 'certs')

    def mkInputs(self):
        with open(os.path.join(self.argdict['local'], 'inputs.conf'), 'w') as fh:
            fh.write("[splunktcp-ssl:9997]\n")
            fh.write("disabled = 0\n\n")
            fh.write("[splunktcp-ssl:9997]")
            fh.write("serverCert = {}\n".format(self.argdict['certs']))
            fh.write("sslPassword = {}\n".format(self.argdict['pw']))
            fh.write("requireClientCert = false\n")

    def mkOutputs(self):
        with open(os.path.join(self.argdict['local'], 'outputs.conf'), 'w') as fh:
            fh.write("[tcpout]\n")
            fh.write("defaultGroup = splunkssl\n\n")
            fh.write("[tcpout:splunkssl]")
            fh.write("server = hostname:9997\n")
            fh.write("clientCert = {}\n".format(self.argdict['certs']))
            fh.write("sslPassword = {}\n".format(self.argdict['pw']))
            fh.write("useClientSSLCompression = true\n")

    def mkServer(self):
        with open(os.path.join(self.argdict['local'], 'server.conf'), 'w') as fh:
            fh.write("[sslConfig]\n")
            fh.write("sslRootCAPath = {}\n".format(self.argdict['certs']))

    def buildSenderApp(self, path):
        mkemptyApp(path)

    def buildReceiverApp(self, path):
        mkemptyApp(path)
        

