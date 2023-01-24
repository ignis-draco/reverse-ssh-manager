#!/bin/bash 


DIR=/run/systemd/system
if [[ !  -d "$DIR" ]]; then 
	echo "Only 'systemd' systems are allowed"
	return -1
fi	

APT_GET_CMD=$(which apt-get)

if [[  -z $APT_GET_CMD ]]; then
    echo "only 'apt' systems ar allowed"
fi


sudo apt-get update 
sudo apt-get install autossh 


####TODO: 

##0) check if alle Files are pressend

if test -f "$name"; then 
	echo "key file not pressend"
	return -1
fi 

if test -f "known_hosts"; then 
	echo "known_hosts file not pressend"
	return -1
fi 


##1) Create user 
sudo useradd  -m -s /sbin/nologin --system autossh

##2) Copy key and config file to dir 
sudo mkdir /home/autossh/.ssh

sudo cp $name /home/autossh/.ssh/
sudo cp known_hosts /home/autossh/.ssh/

sudo chown -R autossh:autossh /home/autossh/.ssh

sudo chmod 700 /home/autossh/.ssh
sudo chmod 600 /home/autossh/.ssh/$name
suod cmod 644 /home/autossh/known_hosts


##5) copy systemd unit 
sudo cp autossh_$name.service /etc/systemd/system/. 
sudo systemctl daemon-reload


##6) enable and start unit 
sudo systemctl start autossh_$name.service
sudo systemctl enable autossh_$name.service





