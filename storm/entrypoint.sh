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
sleep 1
storm jar topology.jar $TOPOLOGY_MAIN $TOPOLOGY_NAME arg1 arg1

if [ $? -eq 0 ]; then
    echo "topology submitted successfully"
else
    echo  "topology failed"
    exit -1
fi

tail -f screenlog.0

# tail -f /dev/null