#!/bin/sh

echo "  1. Install ipv4 hosts"
echo "  2. Install ipv6 hosts"
echo "> 3. Exit"
read -p "choice[1-3]: " choice

choice=${choice:=3}

if [ $choice -eq 1 ]
then
	url=https://raw.github.com/aguegu/huhamhire-hosts/master/downloads/zip/ipv4_unix_utf8.zip
	echo "1) Download ipv4 host for unix:"
elif [ $choice -eq 2  ]
then
	url=https://raw.github.com/aguegu/huhamhire-hosts/master/downloads/zip/ipv6_unix_utf8.zip
	echo "1) Download ipv6 host for unix:"
else
	echo "exit."
	exit 3
fi

newhost=/tmp/hosts.$$

wget $url -O $newhost.zip

if [ $? -eq 0 ]
then
	echo "2) Extract & Implant hostname:"
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

rm -r $newhost
exit $result
