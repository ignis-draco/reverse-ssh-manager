# reverse-ssh-manager
Tool to manage reverse-ssh connections 


TODO: 

1. ctl :
  * add Node 
  * rm Node 
  * list Node 
2. unit:
  * list all conetcet Nodes 
  * inform if node is timeout 



# reverse-ssh-manager

This tool helps to set up and manage a reverse ssh server.  

## Description

To access computers in other networks via ssh, a reverse ssh tunnel can be set up so that the node establishes the connection to the server. 
Through this tunnel it is possible to connect to the node via the server (ssh jump host).



## Getting Started

### Dependencies

#### server 
   * ssh 
   * python3

#### Node
   * ssh    
   * autossh


### Installing

* clone from github
* run preparation.sh 

### Executing program

ctl.py

```
usage: ctl.py [-h] [--list] [-c CREATE] [-r REMOVE] [-a AUTOSSH]

optional arguments:
  -h, --help            show this help message and exit
  --list                List all configure Nodes
  -c CREATE, --create CREATE
                        create a new Node
  -r REMOVE, --remove REMOVE
                        remove a Node
  -a AUTOSSH, --autossh AUTOSSH
                        autossh config for Node
```

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details