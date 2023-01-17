#!/usr/bin/python3

import argparse
from string import Template
import subprocess
import os
import glob
import time
import configparser
from prettytable import PrettyTable

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
    config.write(open(os.path.join(PATH, globel[NODENAME]+".conf"),"w"))


PATH="nodes"
if (not os.path.isdir(PATH)):
    os.mkdir(PATH)

NodeList = []

fileList = glob.glob(PATH + "/*.conf")

print(fileList)
for i in fileList:
    NodeList.append(readConfig(i))    


## functions 


def existNode(nodename):
    for i in NodeList:
        if nodename == i[NODENAME]:
            return True
    return False



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

    file = os.path.join(PATH, nodename + ".conf")

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
    


if (args.list):
    #TODO: Check connection state 
    printnodes(NodeList)
elif (args.create):
    #TODO: opt. parameter Port, timeout 
    #TODO: auto port to next free port 
    create({NODENAME:args.create, PORT:10012, TIMEOUT:5000})
elif(args.remove):
    remove(args.remove)
elif(args.autossh):
    print("auto ssh config")
else: 
    print("no cmd")