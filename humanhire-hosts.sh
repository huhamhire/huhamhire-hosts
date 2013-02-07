#!/bin/sh
# humanhire-host.sh
# host on https://github.com/aguegu/huhamhire-hosts/tree/Client-Linux

backup_hosts()
{
	mkdir -p $HOME/.humanhire-hosts
	ts=$(date +%s)
	echo "copy /etc/hosts to ~/.humanhire-hosts/$ts.host"
	cp /etc/hosts $HOME/.humanhire-hosts/$ts.hosts
	return 0;
}

echo "  1. Install ipv4 hosts"
echo "  2. Install ipv6 hosts"
echo "  3. backup system hosts to ~/.humanhire-hosts/"
echo "  4. retore system hosts from ~/.humanhire-hosts/"
echo "> 5. Exit"
read -p "choice[1-5]: " choice

choice=${choice:=5}

if [ $choice -eq 1 ]
then
	url=https://raw.github.com/aguegu/huhamhire-hosts/Hosts-Modules/downloads/hosts_ipv4.gz
	echo "1) Download ipv4 host for unix:"
elif [ $choice -eq 2  ]
then
	url=https://raw.github.com/aguegu/huhamhire-hosts/Hosts-Modules/downloads/hosts_ipv6.gz
	echo "1) Download ipv6 host for unix:"
elif [ $choice -eq 3 ] 
then
	backup_hosts;
	echo "done."
	exit 0
elif [ $choice -eq 4 ]
then
	backups=$(ls $HOME/.humanhire-hosts -r)
	i=1
	for host in $backups
	do
		dt=$(echo $host | grep -E -o  "^[^.]*" | xargs -I {} date -d "@{}" +"%D-%T")
		printf "%4d. %s: %s\n" $i $dt $host
		i=$((i+1))
	done
	read -p "hosts to restore: [1-$((i-1))]:" id

	if [ $id -ge 1 -a $id -lt $i ]
	then
		path=$HOME/.humanhire-hosts/$(ls $HOME/.humanhire-hosts -r | head -n $id | tail -n 1)
		echo "restore $path to /etc/hosts"
		sudo cp $path /etc/hosts
		echo "done."
		exit 0
	else
	exit 4	
	fi

	echo $id
else
	echo "exit."
	exit 5
fi

newhost=/tmp/hosts.$$

wget $url -O $newhost.gz

if [ $? -eq 0 ]
then
	echo "2) Extract & Implant hostname:"
	tar -zxvf $newhost.gz > /dev/null

	mv hosts $newhost
	sed -i $newhost -e "s/#Replace Your Device Name Here!/$(hostname)/g"
	echo "Done. hostname: " $(hostname)
else
	echo "Download failed."
	rm -r $newhost
	rm -r $newhost.gz
	exit 1
fi

echo "3) Copy new hosts to /etc/hosts: (root required)"
backup_hosts;
sudo cp $newhost /etc/hosts

if [ $? -eq 0 ]
then
	echo "Host updates successfully."
	result=0
else
	echo "Could not replace /etc/hosts. (root required)"
	result=2
fi

rm -r $newhost.gz
rm -r $newhost

exit $result
