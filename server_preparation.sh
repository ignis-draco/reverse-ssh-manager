#!/bin/bash 



sudo groupadd remoteNodes
sudo mkdir /etc/ssh/authorized-keys

sudo chgrp groupadd /etc/ssh/authorized-keys
sudo chmod 775 /etc/ssh/authorized-keys
