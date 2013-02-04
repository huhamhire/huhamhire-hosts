#!/bin/sh

newhost=/tmp/hosts.$$

echo "1. Download ipv6 host for unix:"
wget https://raw.github.com/aguegu/huhamhire-hosts/master/downloads/raw/ipv6_unix_utf8/hosts -O $newhost

echo "2. Implant hostname:"
if [ $? -eq 0 ]
then
	sed -i $newhost -e "s/#Replace Your Device Name Here!/$(hostname)/g"
	echo "Done. hostname: " $(hostname)
else
	echo "Download failed."
	rm -r $newhost
	exit 1
fi

echo "3. Copy new hosts to /etc/hosts:"
if [ $(whoami) = "root" ]
then
	cp $newhost /etc/hosts
	rm $newhost
else
	echo "Update Failed. script needs to be processed by root"
	exit 2
fi

echo "Host updates successfully."
exit 0
