#!/usr/bin/python3

import argparse
from string import Template
import subprocess
import os
import glob
import time
import configparser
from prettytable import PrettyTable
import shutil
import tarfile

##Parameter 

parser = argparse.ArgumentParser()
parser.add_argument("--list", help="List all configure Nodes",  action="store_true")
parser.add_argument("-c", "--create", metavar="Nodename", help="create a new Node")
parser.add_argument("-r", "--remove", metavar="Nodename", help="remove a Node")
parser.add_argument("-a", "--autossh", metavar="Nodename", help="autossh config for Node")
args = parser.parse_args()

##Files & Config

## for configfile 
PORT = "port"
NODENAME = "nodename"
TIMEOUT = "timeout"
KEY = "key" 

## for intern uses 
CONNECTED = "connected"
LASTCONNECTED = "lastConnected"

## File Path
PATHCONFIG="nodes"
if (not os.path.isdir(PATHCONFIG)):
    os.mkdir(PATHCONFIG)

PATHINSTALL = "node_install"
if(not os.path.isdir(PATHINSTALL)):
    os.mkdir(PATHINSTALL)

PATHTEMPLATE="template"


def readConfig(filepath):
    config = configparser.ConfigParser()
    config.read(filepath)
    values = {}
    for i in config.sections():
        values.update(dict(config.items(i)))
    return values
    
def createConfig(globel, key):
    config = configparser.ConfigParser()
    config["Global"] = globel
    config["Key"] = {KEY:key}
    config.write(open(os.path.join(PATHCONFIG, globel[NODENAME]+".conf"),"w"))
##Files 


NodeList = []

fileList = glob.glob(PATHCONFIG + "/*.conf")

for i in fileList:
    NodeList.append(readConfig(i))    


config = configparser.ConfigParser()
config.read("ServerConfig.conf")
ServerConfig = {}
for i in config.sections():
    ServerConfig.update(dict(config.items(i)))


## functions 

def nextFreePort():
    if len(NodeList) == 0:
        return ServerConfig["startPort"]
    portlist = []
    for i in NodeList:
        portlist.append(i[PORT])
    print(portlist)
    return int(sorted(portlist)[-1]) + 1

def existNode(nodename):
    for i in NodeList:
        if nodename == i[NODENAME]:
            return True
    return False

def getNodeConfig(nodename):
    for i in NodeList:
        if(nodename == i[NODENAME]):
            return i
    return None



def create(globel):
    if(existNode(globel[NODENAME])):
        print("name already in use")
        return
    
    cmd = ["useradd --no-create-home -g remoteNodes -s /sbin/nologin --system $name",
    """ sudo -u $name bash -c "ssh-keygen -t ecdsa -b 256 -f /etc/ssh/authorized-keys/$name -q -N ''" """]
    for i in cmd:
        temp = Template(i).substitute(name=globel["nodename"])
        result = subprocess.run(temp, shell=True)

        if result.returncode != 0:
            print("something went wrong")
            return
        else:
            print(temp)
        time.sleep(1)
    key = "".join(open(Template("/etc/ssh/authorized-keys/$name").substitute(name=globel["nodename"])).readlines())

    createConfig(globel, key)


def remove(nodename):
    if(not existNode(nodename)):
        print("nodename not exists")
        return

    file = os.path.join(PATHCONFIG, nodename + ".conf")

    if (len(file) == 0):
        print("No node config file found")
        return
    cmd = ["deluser $name", "rm /etc/ssh/authorized-keys/$name*"]

    for i in cmd:
        temp = Template(i).substitute(name=nodename)
        result = subprocess.run(temp, shell=True)

        if result.returncode != 0:
            print("something went wrong")
            return

    result = subprocess.run("rm "+ file, shell=True)
    if result.returncode != 0:
        print("something went wrong")
        return
        
    

def printnodes(NodeList):
    tb = PrettyTable()
    #TODO: Sort name oder port
    tb.field_names = [NODENAME, PORT, CONNECTED, "last connected"]
    for i in NodeList:
        tb.add_row([i[NODENAME], i[PORT], "i[CONNECTED]", "i[LASTCONNECTED]" ])

    print(tb)    


def createInstall(nodename):

    #1) check config
    if(not existNode(nodename)):
        print("nodename not exists")
        return 

    #1.1) check if nodename is pressend    
    path = os.path.join(PATHINSTALL,nodename)
    
    if(os.path.isdir(path)):
        shutil.rmtree(path)
    
    if(os.path.exists(os.path.join(PATHINSTALL, nodename + ".tar.gz") )):
        os.remove(os.path.join(PATHINSTALL, nodename + ".tar.gz"))
    
    #2) create dir in /node_install/<Nodename>
    os.mkdir(path)
    
    #3) get host key (Known_keys) > in folder
    find_key = False
    hostkey = ""
    testcnt = 0
    while(not find_key): 
        o = subprocess.run("ssh-keyscan -H localhost", shell=True, capture_output=True, text=True)    
        testcnt += 1
        if (len(o.stdout) != 0):
            hostkey = o.stdout
            find_key = True
        if(testcnt > 100):
            print("not server key fingerprint!")
            return 
    
    
    f = open(os.path.join(path, "known_hosts"),"w")
    f.write(hostkey)
    f.close()
    
    nodeConfig = getNodeConfig(nodename)    
    
    #4) use autossh.service template > autossh_<Nodename>.service
    servicesTemp = Template( open( os.path.join(PATHTEMPLATE,"autossh.service" )).read())
    installTemp =  Template(open(os.path.join(PATHTEMPLATE,"client_install.sh")).read())
    
    
    service = servicesTemp.substitute(name=nodeConfig[NODENAME], port=nodeConfig[PORT],
                                      server=ServerConfig["server"],
                                      serverSSHPort=ServerConfig["serverSSHPort"] )

    with open(os.path.join(path, "autossh_"+nodeConfig[NODENAME]+".service" ),"w") as f:
        f.write(service)
    
    #5) user client_install.sh template > autossh 
    install = installTemp.safe_substitute(name=nodeConfig[NODENAME])
    with open(os.path.join(path, "client_install.sh"),"w") as f:
        f.write(install)

    #6) copy private key 
    with open(os.path.join(path, nodeConfig[NODENAME]),"w") as f:
        f.write(nodeConfig[KEY])

    #7) tar.gz alles 
    files = os.listdir(path)
    with tarfile.open(os.path.join(PATHINSTALL, nodename + ".tar.gz"), "w:gz") as tar:
        for name in files:
            tar.add(os.path.join(path,name),arcname=name )
    
    #8) [optional] create text file for std copy 
    with open( os.path.join(PATHINSTALL, nodename + ".copy"), "w") as f:
        f.write("echo $'" + service + "' > " + "autossh_"+nodeConfig[NODENAME]+".service\n")
        f.write("echo $'" + install + "' > " + "client_install.sh\n")
        f.write("echo $'" + nodeConfig[KEY] +"' > " + nodeConfig[NODENAME] + "\n")

               


if (args.list):
    #TODO: Check connection state
    printnodes(NodeList)
elif (args.create):
    #TODO: opt. parameter timeout     
    create({NODENAME:args.create, PORT:nextFreePort(), TIMEOUT:5000})
elif(args.remove):
    remove(args.remove)
elif(args.autossh):
    createInstall(args.autossh)
else: 
    print("no cmd")