 #!/bin/bash


function newConf() {
    sed "s/\"geospatial_lat_min\": 0,/\"geospatial_lat_min\": $MIN_LAT".00",/" $1 > configuration_new.json
    sed -i "s/\"geospatial_lon_min\": 0,/\"geospatial_lon_min\": $MIN_LON".00",/" configuration_new.json
    sed -i "s/\"geospatial_lat_max\": 0,/\"geospatial_lat_max\": $2".00",/" configuration_new.json
    sed -i "s/\"geospatial_lon_max\": 0/\"geospatial_lon_max\": $3".00"/" configuration_new.json
    sed -i "s/\"time_coverage_end\":.*/\"time_coverage_end\": \"$4\"/" configuration_new.json
    sed -i "s/\"parameters\":.*/\"parameters\": [\"$5\"],/" configuration_new.json
    
#     echo geospatial_lat_min $MIN_LAT geospatial_lon_min $MIN_LON geospatial_lat_max $1".00" geospatial_lon_max $2".00" time_coverage_end $3 parameter $4
#     cat configuration_new.json
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

    num_of_params=`jq -r '.parameters[] | length' $1`
    input_folder=`jq -r .input_folder $1`
    dataset_size=`du -sb $input_folder/ | awk '{print $1}'`
    output_file=`jq -r .output_file $1`
    output_file_size=$(wc -c <"$output_file")
    
    conf=`jq . $1`
    num_of_nodes=`wc -l $SSH_FILE | awk '{print $1}'`
    last_ssh_line=`tail -1  $SSH_FILE`
    if [ -z "$last_ssh_line" ] ; then
        num_of_nodes=$((num_of_nodes - 1))
    fi
    echo "{" \"area\": $area, \"time_coverage\": $time_coverage, \"num_of_params\": $num_of_params, \"dataset_size\": $dataset_size, \"output_file_size\": $output_file_size, \"execution_time\": $execution_time,\"execution_date\": \"$EXECUTION_DATE\" , \"configuration\": $conf, \"num_of_nodes\":$num_of_nodes , \"executing_node\":\"$MY_IP\""}"
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
    num_of_params=`jq -r '.parameters[] | length' $1`
    input_folder=`jq -r .input_folder $1`
    dataset_size=`du -sb $input_folder/ | awk '{print $1}'`
    output_file=`jq -r .output_file $1`
    output_file_size=$(wc -c <"$output_file")
    
    conf=`jq . $1`
    echo "{" \"area\": $area, \"time_coverage\": $time_coverage, \"num_of_params\": $num_of_params, \"dataset_size\": $dataset_size, \"output_file_size\": $output_file_size, \"execution_time\": $execution_time,\"execution_date\": \"$date\" , \"configuration\": $conf, \"num_of_nodes\":$num_of_nodes, \"executing_node\":\"$ip\""}"
#     rm $WORK_DIR/$FILTER_RESULT_FILE
}


function run_parameter_sweep() {
    #Set latitude
    for (( i=$LAT_START; i<=$MAX_LAT; i=i+$STEP ))
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
            if [ "$NEXT_DATE_SECONDS" -gt "$MAX_DATE_SECONDS" ]; then
                NEXT_DATE=$MAX_DATE        
            fi

            parameters=9
            while read l; do
                count=$((count+1))
                parameters=$parameters","$l
                if [ "$count" -gt "200" ]; then
                    newConf $1 $i $j $NEXT_DATE $parameters
                    run configuration_new.json
                    count=0
                fi
                
            done <physical_parameter_keys.txt
            done        
        done
    done
}


function run_new_conf() {
    #Set latitude
    count_all=0
    for (( i=$LAT_START; i<=$MAX_LAT; i=i+$STEP ))
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
            if [ "$NEXT_DATE_SECONDS" -gt "$MAX_DATE_SECONDS" ]; then
                NEXT_DATE=$MAX_DATE        
            fi

            parameters=9
            while read l; do
                count=$((count+1))
                parameters=$parameters","$l
                if [ "$count" -gt "200" ]; then
                    newConf $1 $i $j $NEXT_DATE $parameters
                    mv configuration_new.json $count_all"_"configuration_new.json
                    count_all=$((count_all+1))
                    count=0
                fi
            done <physical_parameter_keys.txt
            done        
        done
    done
}

function block() {
    extra_mils=0
    while read line; do
        node_ip=`echo $line | awk -F "@" '{print $2}'`
        while [ -f /tmp/$node_ip.run ]
        do
            extra_mils=$((extra_mils+100))
            sleep 0.1
        done
    done < $SSH_FILE
    END_EXECUTION=$(($(date +%s%N)/1000000))
    END_EXECUTION=$((END_EXECUTION-extra_mils))
}


function run() {
    FILTER_RESULT_FILE=`date +%s | sha256sum | base64 | head -c 8 ; echo`.out
    python $WORK_DIR/generation_argo_big_data.py $1 &> $WORK_DIR/$FILTER_RESULT_FILE
    ssh $MASTER_IP "rm /tmp/$MY_IP.run" < /dev/null
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
        ssh $node -i $KEY_PATH "screen -L -dmS argoBenchmark bash ~/workspace/dockerfiles/ArgoDiffusion/scripts/runParameterSweep.sh -op=run -json_conf_file=/mnt/data/source/$ssh_count"_"configuration_new.json -maser_ip=$MY_IP" < /dev/null
        ssh_count=$((ssh_count+1))
    done < $SSH_FILE
    block
    parse_dist_result configuration_new.json
}

function send_messages() {
    ssh_count=0
    EXECUTION_DATE=`date +%Y-%m-%dT%H:%M:%SZ`
    START_EXECUTION=$(($(date +%s%N)/1000000))
    while read node; do
#         node_ip=`echo $node | awk -F "@" '{print $2}'`
#         FILTER_RESULT_FILE=`date +%s | sha256sum | base64 | head -c 8 ; echo`.out
        python task.py $RMQ_HOST $RMQ_PORT $ssh_count"_"configuration_new.json task &> $WORK_DIR/$ssh_count"_".out
        ssh_count=$((ssh_count+1))
    done < $SSH_FILE
    q_size=`python task.py $RMQ_HOST $RMQ_PORT $ssh_count"_"configuration_new.json no_task`
    echo $q_size
    while [ $q_size -gt 1 ]
    do
        q_size=`python task.py $RMQ_HOST $RMQ_PORT $ssh_count"_"configuration_new.json no_task`
        echo $q_size
    done
#     echo waiting 
#     wait
#     parseResult $ssh_count"_"configuration_new.json $node_ip $WORK_DIR/$ssh_count"_".out
    END_EXECUTION=$(($(date +%s%N)/1000000))
#     parse_dist_result configuration_new.json 
}


function run_parameter_sweep_distributed_ssh() {
    count_all=0
    #Set latitude
    for (( i=$LAT_START; i<=$MAX_LAT; i=i+$STEP ))
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
                if [ "$NEXT_DATE_SECONDS" -gt "$MAX_DATE_SECONDS" ]; then
                    NEXT_DATE=$MAX_DATE        
                fi
                parameters=9
                while read l; do
                    count=$((count+1))
                    parameters=$parameters","$l
                    if [ "$count" -gt "200" ]; then
                        newConf $1 $i $j $NEXT_DATE $parameters
                        python partitioning.py configuration_new.json $SSH_FILE
                        run_ssh
                        sleep 0.5
                        count_all=$((count_all+1))
                        count=0
                    fi
                done <physical_parameter_keys.txt
            done        
        done
    done
}


function run_parameter_sweep_distributed_rabbit() {
    count_all=0
    #Set latitude
    for (( i=$LAT_START; i<=$MAX_LAT; i=i+$STEP ))
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
                if [ "$NEXT_DATE_SECONDS" -gt "$MAX_DATE_SECONDS" ]; then
                    NEXT_DATE=$MAX_DATE        
                fi

                parameters=9
                while read l; do
                    count=$((count+1))
                    parameters=$parameters","$l
                    if [ "$count" -gt "200" ]; then
                        newConf $1 $i $j $NEXT_DATE $parameters
                        python partitioning.py configuration_new.json $SSH_FILE
                        send_messages
                        count_all=$((count_all+1))
                        count=0
                    fi
                done <physical_parameter_keys.txt
            done        
        done
    done
}




for i in "$@"
do
case $i in
    -op=*|--operation=*)
    OPERATION="${i#*=}"
    ;;
    -json_conf_file=*)
    JSON_CONF_FILE="${i#*=}"
    ;;
    -conf_file=*)
    CONF_FILE="${i#*=}"
    ;;
    -maser_ip=*)
    MASTER_IP="${i#*=}"
    ;;    
esac
done

# echo OPERATION = ${OPERATION}
# echo JSON_CONF_FILE = ${JSON_CONF_FILE}
# echo CONF_FILE = ${CONF_FILE}

WORK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MY_IP=`ifconfig eth0 | awk '/inet addr/ {gsub("addr:", "", $2); print $2}'`
if [ -z "$MY_IP" ]; then
    MY_IP=$HOSTNAME
fi
    
RMQ_HOST=localhost 
RMQ_PORT=5672

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
