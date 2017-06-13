 #!/bin/bash


function newConf() {
    sed "s/\"geospatial_lat_min\": 0,/\"geospatial_lat_min\": $MIN_LAT".00",/" $1 > configuration_new.json
    sed -i "s/\"geospatial_lon_min\": 0,/\"geospatial_lon_min\": $MIN_LON".00",/" configuration_new.json
    sed -i "s/\"geospatial_lat_max\": 0,/\"geospatial_lat_max\": $2".00",/" configuration_new.json
    sed -i "s/\"geospatial_lon_max\": 0/\"geospatial_lon_max\": $3".00"/" configuration_new.json
    sed -i "s/\"time_coverage_end\":.*/\"time_coverage_end\": \"$4\"/" configuration_new.json
    sed -i "s/\"parameters\":.*/\"parameters\": [$5],/" configuration_new.json
    
#     echo geospatial_lat_min $MIN_LAT geospatial_lon_min $MIN_LON geospatial_lat_max $1".00" geospatial_lon_max $2".00" time_coverage_end $3 parameter $4
#     cat configuration_new.json
}

function dbg(){
    if [ "$DBG" = true ] ; then
        echo $1 $2
    fi
}

function parse_dist_result() {
    
    time_coverage_start=`jq -r .time_range.time_coverage_start $1`
    time_coverage_end=`jq -r .time_range.time_coverage_end $1`
    if [ -z "$time_coverage_start" ] || [ -z "$time_coverage_end" ] ; then
        echo "time_coverage was empty" 
        exit
    fi
    
    time_coverage=`python $WORK_DIR/getDelta.py $time_coverage_start $time_coverage_end`
    
    geospatial_lat_min=`jq -r .bounding_box.geospatial_lat_min $1`
    geospatial_lat_max=`jq -r .bounding_box.geospatial_lat_max $1`
    geospatial_lon_min=`jq -r .bounding_box.geospatial_lon_min $1`
    geospatial_lon_max=`jq -r .bounding_box.geospatial_lon_max $1`
    
    area=`python $WORK_DIR/coordinates2Area.py $geospatial_lat_min $geospatial_lat_max $geospatial_lon_min $geospatial_lon_max`
    
     
    execution_time=$((END_EXECUTION-START_EXECUTION))
    execution_time=`bc <<< "scale = 3; ($execution_time / 1000)"`

    num_of_params=`jq -r '.parameters[]' $1 | wc -l`
    input_folder=`jq -r .input_folder $1`
    dataset_size=`du -sb $input_folder/ | awk '{print $1}'`
    output_file=`jq -r .output_file $1`
    output_file_size=$(wc -c <"$output_file")
     
    conf=$(jq . $1)
        
    num_of_nodes=`python getNumberOfConsumers.py $RMQ_HOST 15672 task_queue`
    
#     dbg ${FUNCNAME[0]} "execution_time: "$execution_time
    if (( $(echo "$execution_time > 2" |bc -l) )); then
        echo "{" \"area\": $area, \"time_coverage\": $time_coverage, \"num_of_params\": $num_of_params, \"dataset_size\": $dataset_size, \"output_file_size\": $output_file_size, \"execution_time\": $execution_time,\"execution_date\": \"$EXECUTION_DATE\" , \"configuration\": $conf, \"num_of_nodes\":$num_of_nodes , \"executing_node\":\"$MY_IP\""}"
    fi
    
#     dbg ${FUNCNAME[0]} "output_file_size: "$output_file_size
#     if [ "$output_file_size" -gt "86" ]; then
        echo "{" \"area\": $area, \"time_coverage\": $time_coverage, \"num_of_params\": $num_of_params, \"dataset_size\": $dataset_size, \"output_file_size\": $output_file_size, \"execution_time\": $execution_time,\"execution_date\": \"$EXECUTION_DATE\" , \"configuration\": $conf, \"num_of_nodes\":$num_of_nodes , \"executing_node\":\"$MY_IP\""}"
#     fi
}


function parseResult() {
    sed -i 's/duration (seconds)/duration/g' $2
    time_coverage_start=`jq -r .time_range.time_coverage_start $1`
    time_coverage_end=`jq -r .time_range.time_coverage_end $1`
    if [ -z "$time_coverage_start" ] || [ -z "$time_coverage_end" ] ; then
        echo "time_coverage was empty" 
        exit
    fi
    
    time_coverage=`python $WORK_DIR/getDelta.py $time_coverage_start $time_coverage_end`
    
    geospatial_lat_min=`jq -r .bounding_box.geospatial_lat_min $1`
    geospatial_lat_max=`jq -r .bounding_box.geospatial_lat_max $1`
    geospatial_lon_min=`jq -r .bounding_box.geospatial_lon_min $1`
    geospatial_lon_max=`jq -r .bounding_box.geospatial_lon_max $1`
    
    area=`python $WORK_DIR/coordinates2Area.py $geospatial_lat_min $geospatial_lat_max $geospatial_lon_min $geospatial_lon_max`
    
    date=`jq -r .date $WORK_DIR/$FILTER_RESULT_FILE`
    if [ -z "$date" ]; then
        echo "output file was malformed"
        cat $WORK_DIR/$FILTER_RESULT_FILE
        exit
    fi
    
    ip=$3
    if [ -z "$ip" ]; then
        ip=$MY_IP
    fi
    num_of_nodes=$4
    if [ -z "$num_of_nodes" ]; then
        num_of_nodes=1
    fi
    
    execution_time=`jq -r .duration $WORK_DIR/$FILTER_RESULT_FILE`
    num_of_params=`jq -r '.parameters[]' $1 | wc -l`
    input_folder=`jq -r .input_folder $1`
    dataset_size=`du -sb $input_folder/ | awk '{print $1}'`
    output_file=`jq -r .output_file $1`
    output_file_size=$(wc -c <"$output_file")
#     if [ "$output_file_size" -gt "86" ]; then
        conf=$(jq . $1)
        echo "{" \"area\": $area, \"time_coverage\": $time_coverage, \"num_of_params\": $num_of_params, \"dataset_size\": $dataset_size, \"output_file_size\": $output_file_size, \"execution_time\": $execution_time,\"execution_date\": \"$date\" , \"configuration\": $conf, \"num_of_nodes\":$num_of_nodes, \"executing_node\":\"$ip\""}"
#     fi
}


function run_parameter_sweep() {
    #Set latitude
    for (( sweep_i=$LAT_START; sweep_i<=$MAX_LAT; sweep_i=sweep_i+$STEP ))
    do
        # Set longitude
        for (( j=$LON_START; j<=$MAX_LON; j=j+$STEP ))
        do
            for (( k=1; k<=21; k=k+10))
            do
                count=0
                date_count=0
                NEXT_DATE=$(date +"%Y-%m-%dT%H:%M:%SZ" -d "$DATE + $k year")
                NEXT_DATE_SECONDS=`date -d "$NEXT_DATE" +%s`
                parameters=9
                while read l; do
                    count=$((count+1))
                    parameters=$parameters","$l
                    if [ "$count" -ge "400" ]; then                        
                        newConf $1 $sweep_i $j $NEXT_DATE $parameters
                        run configuration_new.json
                        count=0
                    fi
                done <physical_parameter_keys.txt
                newConf $1 $sweep_i $j $NEXT_DATE $parameters
                run configuration_new.json
            done
            newConf $1 $sweep_i $j $MAX_DATE $parameters
            run configuration_new.json
        done
        newConf $1 $sweep_i $MAX_LON $MAX_DATE $parameters
        run configuration_new.json        
    done
    newConf $1 $MAX_LAT $MAX_LON $MAX_DATE $parameters
    run configuration_new.json            
}


function run_new_conf() {
    #Set latitude
    count_all=0
    for (( conf_i=$LAT_START; conf_i<=$MAX_LAT; conf_i=conf_i+$STEP ))
    do
        # Set longitude
        for (( j=$LON_START; j<=$MAX_LON; j=j+$STEP ))
        do
            for (( k=1; k<=21; k=k+20))
            do
                count=0
                date_count=0
                NEXT_DATE=$(date +"%Y-%m-%dT%H:%M:%SZ" -d "$DATE + $k year")
                NEXT_DATE_SECONDS=`date -d "$NEXT_DATE" +%s`
                parameters=9
                while read l; do
                    count=$((count+1))
                    parameters=$parameters","$l
                    if [ "$count" -gt "400" ]; then
                        newConf $1 $conf_i $j $NEXT_DATE $parameters
                        mv configuration_new.json $count_all"_"configuration_new.json
                        count_all=$((count_all+1))
                        count=0
                    fi
                done <physical_parameter_keys.txt
                newConf $1 $conf_i $j $NEXT_DATE $parameters
            done
            newConf $1 $conf_i $j $MAX_DATE $parameters
        done
        newConf $1 $conf_i $MAX_LON $MAX_DATE $parameters
    done
    newConf $1 $MAX_LAT $MAX_LON $MAX_DATE $parameters
}

function block() {
    extra_mils=0
    while read line; do
        node_ip=`echo $line | awk -F "@" '{print $2}'`
        while [ -f /tmp/$node_ip.run ]
        do
            extra_mils=$((extra_mils+100))
            sleep 0.1
            dbg ${FUNCNAME[0]} "extra_mils: "$extra_mils
        done
    done < $SSH_FILE
    END_EXECUTION=$(($(date +%s%N)/1000000))
    END_EXECUTION=$((END_EXECUTION-extra_mils))
}


function run() {
    FILTER_RESULT_FILE=`date +%s | sha256sum | base64 | head -c 8 ; echo`.out
    python $WORK_DIR/generation_argo_big_data.py $1 &> $WORK_DIR/$FILTER_RESULT_FILE
    parseResult $1 $WORK_DIR/$FILTER_RESULT_FILE
}

function run_ssh() {
    ssh_count=0
    EXECUTION_DATE=`date +%Y-%m-%dT%H:%M:%SZ`
    START_EXECUTION=$(($(date +%s%N)/1000000))
    while read node; do
        scp -i $KEY_PATH $ssh_count"_"configuration_new.json $node:/mnt/data/source &> /dev/null   
        node_ip=`echo $node | awk -F "@" '{print $2}'`
        touch /tmp/$node_ip.run
        ssh $node -i $KEY_PATH "screen -L -dmS worker bash ~/workspace/dockerfiles/ArgoDiffusion/scripts/runParameterSweep.sh -op=run -json_conf_file=/mnt/data/source/$ssh_count"_"configuration_new.json -maser_ip=$MY_IP" < /dev/null
        ssh_count=$((ssh_count+1))
    done < $SSH_FILE
    block
    parse_dist_result "configuration_new.json"
}

function send_messages() {
    EXECUTION_DATE=`date +%Y-%m-%dT%H:%M:%SZ`
    START_EXECUTION=$(($(date +%s%N)/1000000))
    
    
    for new_file in $( ls *_configuration_new.json); do python task.py $RMQ_HOST $RMQ_PORT $new_file task &> $WORK_DIR/$new_file"_".out; done
        
    sleep 1
    q_size=`python task.py $RMQ_HOST $RMQ_PORT 0_configuration_new.json task_queue`
    while [ $q_size -ge 1 ]
    do
        q_size=`python task.py $RMQ_HOST $RMQ_PORT 0_configuration_new.json task_queue`
        count=$((count+1))
    done
    
    q_size=`python task.py $RMQ_HOST $RMQ_PORT 0_configuration_new.json task_queue`
    while [ $q_size -ge 1 ]
    do
        python task.py $RMQ_HOST $RMQ_PORT $ssh_count"_"configuration_new.json consume
        q_size=`python task.py $RMQ_HOST $RMQ_PORT 0_configuration_new.json task_queue`
    done
    END_EXECUTION=$(($(date +%s%N)/1000000))
    END_EXECUTION=$((END_EXECUTION-1000))
    parse_dist_result "configuration_new.json"
}


function run_parameter_sweep_distributed_ssh() {
    count_all=0
    #Set latitude
    for (( ssh_i=$LAT_START; ssh_i<=$MAX_LAT; ssh_i=ssh_i+$STEP ))
    do
        # Set longitude
        for (( j=$LON_START; j<=$MAX_LON; j=j+$STEP ))
        do
            for (( k=1; k<=21; k=k+10))
            do
                count=0
                date_count=0
                NEXT_DATE=$(date +"%Y-%m-%dT%H:%M:%SZ" -d "$DATE + $k year")
                NEXT_DATE_SECONDS=`date -d "$NEXT_DATE" +%s`
                parameters=9
                while read l; do
                    count=$((count+1))
                    parameters=$parameters","$l
                    if [ "$count" -gt "200" ]; then
                        newConf $1 $ssh_i $j $NEXT_DATE $parameters
                        python partitioning.py configuration_new.json $SSH_FILE
                        run_ssh
                        count_all=$((count_all+1))
                        count=0
                    fi
                done <physical_parameter_keys.txt
                newConf $1 $ssh_i $j $NEXT_DATE $parameters
                python partitioning.py configuration_new.json $SSH_FILE
                run_ssh
            done        
            newConf $1 $ssh_i $j $MAX_DATE $parameters
            python partitioning.py configuration_new.json $SSH_FILE
            run_ssh
        done
        newConf $1 $ssh_i $MAX_LON $MAX_DATE $parameters
        python partitioning.py configuration_new.json $SSH_FILE
        run_ssh
    done
    newConf $1 $MAX_LAT $MAX_LON $MAX_DATE $parameters
    python partitioning.py configuration_new.json $SSH_FILE
    run_ssh
}


function run_parameter_sweep_distributed_rabbit() {
    GLOBAL_COUNT=0
    nodes=`python getNumberOfConsumers.py $RMQ_HOST 15672 task_queue`
    #Set latitude
    for (( i_rabbit=$LAT_START; i_rabbit<=$MAX_LAT; i_rabbit=i_rabbit+$STEP ))
    do
        # Set longitude
        for (( j=$LON_START; j<=$MAX_LON; j=j+$STEP ))
        do
            for (( k=1; k<=21; k=k+5))
            do
                count=0
                date_count=0
                NEXT_DATE=$(date +"%Y-%m-%dT%H:%M:%SZ" -d "$DATE + $k year")
                NEXT_DATE_SECONDS=`date -d "$NEXT_DATE" +%s`
                parameters=9
                while read l; do
                    count=$((count+1))
                    parameters=$parameters","$l
                    if [ "$count" -gt "200" ]; then
                        newConf $1 $i_rabbit $j $NEXT_DATE $parameters
                        python partitioning.py configuration_new.json $nodes
                        send_messages
                        GLOBAL_COUNT=$((GLOBAL_COUNT+1))
                        count=0
                    fi
                done <physical_parameter_keys.txt
                newConf $1 $i_rabbit $j $NEXT_DATE $parameters
                python partitioning.py configuration_new.json $nodes
                send_messages        
            done        
            newConf $1 $i_rabbit $j $MAX_DATE $parameters
            python partitioning.py configuration_new.json $nodes
            send_messages
        done
        newConf $1 $i_rabbit $MAX_LON $MAX_DATE $parameters
        python partitioning.py configuration_new.json $nodes
        send_messages
    done
    newConf $1 $MAX_LAT $MAX_LON $MAX_DATE $parameters    
    python partitioning.py configuration_new.json $nodes
    send_messages
}




for input_i in "$@"
do
case $input_i in
    -op=*|--operation=*)
    OPERATION="${input_i#*=}"
    ;;
    -json_conf_file=*)
    JSON_CONF_FILE="${input_i#*=}"
    ;;
    -conf_file=*)
    CONF_FILE="${input_i#*=}"
    ;;
    -maser_ip=*)
    MASTER_IP="${input_i#*=}"
    ;;    
esac
done

# echo OPERATION = ${OPERATION}
# echo JSON_CONF_FILE = ${JSON_CONF_FILE}
# echo CONF_FILE = ${CONF_FILE}

WORK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# MY_IP=`ifconfig eth0 | awk '/inet addr/ {gsub("addr:", "", $2); print $2}'  &> /dev/null`

if [ -z "$MY_IP" ]; then
    MY_IP=$HOSTNAME
fi
    
RMQ_HOST=localhost 
RMQ_PORT=5672
DBG=true



if [ -n "$CONF_FILE" ]; then
    source ${CONF_FILE}
fi

case ${OPERATION} in
    run)
    run $JSON_CONF_FILE
    ;;
    run_new_conf)
    run_new_conf $JSON_CONF_FILE
    ;;    
    run_parameter_sweep)
    run_parameter_sweep $JSON_CONF_FILE
    ;;
    run_parameter_sweep_distributed_ssh)
    run_parameter_sweep_distributed_ssh $JSON_CONF_FILE
    ;;    
    run_parameter_sweep_distributed_rabbit)
    run_parameter_sweep_distributed_rabbit $JSON_CONF_FILE
    ;;      
esac

#  ./runParameterSweep.sh -op=run_parameter_sweep_distributed_ssh -json_conf_file=configuration1.json  -conf_file=med.conf

# this="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
# grep "function" $this | awk '{print $2}' 
