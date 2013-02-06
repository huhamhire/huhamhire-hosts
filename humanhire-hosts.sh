#!/bin/sh

echo "  1. Install ipv4 hosts"
echo "  2. Install ipv6 hosts"
echo "> 3. Exit"
read -p "choice[1-3]: " choice

choice=${choice:=3}

if [ $choice -eq 1 ]
then
	url=https://raw.github.com/aguegu/huhamhire-hosts/Hosts-Modules/downloads/hosts_ipv4.tar.gz
	echo "1) Download ipv4 host for unix:"
elif [ $choice -eq 2  ]
then
	url=https://raw.github.com/aguegu/huhamhire-hosts/Hosts-Modules/downloads/hosts_ipv6.tar.gz
	echo "1) Download ipv6 host for unix:"
else
	echo "exit."
	exit 3
fi

newhost=/tmp/hosts.$$

wget $url -O $newhost.tar.gz

if [ $? -eq 0 ]
then
	echo "2) Extract & Implant hostname:"
	gunzip $newhost.tar.gz
	tar -xvf $newhost.tar > /dev/null
	
	mv hosts $newhost
	sed -i $newhost -e "s/#Replace Your Device Name Here!/$(hostname)/g"
	echo "Done. hostname: " $(hostname)
else
	echo "Download failed."
	rm -r $newhost
	rm -r $newhost.tar.gz
	exit 1
fi

echo "3) Copy new hosts to /etc/hosts: (root required)"
sudo cp $newhost /etc/hosts

if [ $? -eq 0 ]
then
	echo "Host updates successfully."
	result=0
else
	echo "Could not replace /etc/hosts. (root required)"
	result=2
fi

rm -r $newhost.tar.gz
rm -r $newhost.tar
rm -r $newhost

exit $result
