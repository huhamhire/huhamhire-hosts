#!/bin/sh

newhost=/tmp/hosts.$$

echo "1. Download ipv6 host for unix:"
wget https://raw.github.com/aguegu/huhamhire-hosts/master/downloads/zip/ipv6_unix_utf8.zip -O $newhost.zip

echo "2. Extract & Implant hostname:"
if [ $? -eq 0 ]
then
	unzip $newhost.zip
	mv hosts $newhost
	sed -i $newhost -e "s/#Replace Your Device Name Here!/$(hostname)/g"
	echo "Done. hostname: " $(hostname)
else
	echo "Download failed."
	rm -r $newhost
	rm -r $newhost.zip
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
