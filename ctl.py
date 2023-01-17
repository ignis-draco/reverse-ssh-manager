#!/usr/bin/python3

import argparse
from string import Template
import subprocess
import os
import glob

parser = argparse.ArgumentParser()

parser.add_argument("--list", help="List all configure Nodes",  action="store_true")
parser.add_argument("-c", "--create", help="create a new Node")
parser.add_argument("-r", "--remove", help="remove a Node")
parser.add_argument("-a", "--autossh", help="autossh config for Node")



##Files

nodetemplate = Template("""nodename=$name 
port=$port
key=$key
timeout=$timeout
""")


PATH="nodes"
if (not os.path.isdir(PATH)):
    os.mkdir(PATH)


args = parser.parse_args()


def create(nodename, port, timeout):
    
    nodeList = glob.glob(PATH + "/*.conf")
    for i in nodeList:
        if (nodename + ".conf") in i:
            print("name already in use")
            return
    
    cmd = ["useradd --system -g nogroup -G remoteNodes --no-create-home $name", "usermod -s /bin/true $name"
    """ sudo -u $name bash -c "ssh-keygen -t ecdsa -b 256 -f /etc/ssh/authorized-keys/$name -q -N ''" """]

    for i in cmd:
        temp = Template(i).substitute(name=nodename)
        result = subprocess.run(temp, shell=True)

        if result.returncode != 0:
            print("something went wrong")
            return
    key = "".join(open(Template("/etc/ssh/authorized-keys/$name").substitute(name=nodename)).readlines())

    open(os.path.join(PATH,nodename + ".conf"),"w").writelines(nodetemplate.substitute(name=nodename, port=port, timeout=timeout, key="\n"+key[:-1]))
    print(nodetemplate.substitute(name=nodename, port=port, timeout=timeout, key="\n" + key[:-1]))



def remove(nodename):

    nodeList = glob.glob(PATH + "/*.conf")
    file = ""
    for i in nodeList:
        if (nodename + ".conf") in i:
            file = i

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
        
    
    
    

if (args.list):
    print("list")
elif (args.create):
    create(args.create, 10012, 5000)
elif(args.remove):
    remove(args.remove)
elif(args.autossh):
    print("auto ssh config")
else: 
    print("no cmd")