#!/bin/bash


screen -dm -L sh -c 'storm nimbus && rm screenlog.0'
sleep 1
if [ -f "screenlog.0" ]
then
	echo "screenlog.0 found."
else
	echo "screenlog.0 not found."
	exit -1
fi

wget -O topology.jar $TOPOLOGY_URL

storm jar topology.jar $TOPOLOGY_MAIN $TOPOLOGY_NAME arg1 arg1

tail -f screenlog.0

# tail -f /dev/null