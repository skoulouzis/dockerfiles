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
    
    local time_coverage_start=`jq -r .time_range.time_coverage_start $1`
    local time_coverage_end=`jq -r .time_range.time_coverage_end $1`
    if [ -z "$time_coverage_start" ] || [ -z "$time_coverage_end" ] ; then
        echo "time_coverage was empty" 
        exit
    fi
    
    local time_coverage=`python $WORK_DIR/getDelta.py $time_coverage_start $time_coverage_end`
    
    local geospatial_lat_min=`jq -r .bounding_box.geospatial_lat_min $1`
    local geospatial_lat_max=`jq -r .bounding_box.geospatial_lat_max $1`
    local geospatial_lon_min=`jq -r .bounding_box.geospatial_lon_min $1`
    local geospatial_lon_max=`jq -r .bounding_box.geospatial_lon_max $1`
    
    local area=`python $WORK_DIR/coordinates2Area.py $geospatial_lat_min $geospatial_lat_max $geospatial_lon_min $geospatial_lon_max`
    
     
    local execution_time=$((END_EXECUTION-START_EXECUTION))
    local execution_time=`bc <<< "scale = 3; ($execution_time / 1000)"`

    local num_of_params=`jq -r '.parameters[]' $1 | wc -l`
    local input_folder=`jq -r .input_folder $1`
    local dataset_size=`du -sb $input_folder/ | awk '{print $1}'`
    local output_file=`jq -r .output_file $1`
    local output_file_size=$(wc -c <"$output_file")
     
    local conf=$(jq . $1)
    
#     dbg ${FUNCNAME[0]} "output_file_size: "$output_file_size
#     if [ "$output_file_size" -gt "86" ]; then
        echo "{" \"area\": $area, \"time_coverage\": $time_coverage, \"num_of_params\": $num_of_params, \"dataset_size\": $dataset_size, \"output_file_size\": $output_file_size, \"execution_time\": $execution_time,\"execution_date\": \"$EXECUTION_DATE\" , \"configuration\": $conf, \"num_of_nodes\":$NUMBER_OF_NODES , \"executing_node\":\"$MY_IP\""}"
#     fi
}


function parseResult() {
    sed -i 's/duration (seconds)/duration/g' $2
    local time_coverage_start=`jq -r .time_range.time_coverage_start $1`
    local time_coverage_end=`jq -r .time_range.time_coverage_end $1`
    if [ -z "$time_coverage_start" ] || [ -z "$time_coverage_end" ] ; then
        echo "time_coverage was empty" 
        exit
    fi
    
    local time_coverage=`python $WORK_DIR/getDelta.py $time_coverage_start $time_coverage_end`
    
    local geospatial_lat_min=`jq -r .bounding_box.geospatial_lat_min $1`
    local geospatial_lat_max=`jq -r .bounding_box.geospatial_lat_max $1`
    local geospatial_lon_min=`jq -r .bounding_box.geospatial_lon_min $1`
    local geospatial_lon_max=`jq -r .bounding_box.geospatial_lon_max $1`
    
    local area=`python $WORK_DIR/coordinates2Area.py $geospatial_lat_min $geospatial_lat_max $geospatial_lon_min $geospatial_lon_max`
    
    local date=`jq -r .date $WORK_DIR/$FILTER_RESULT_FILE`
    if [ -z "$date" ]; then
        echo "output file was malformed"
        cat $WORK_DIR/$FILTER_RESULT_FILE
        exit
    fi
    
    local ip=$3
    if [ -z "$ip" ]; then
        local ip=$MY_IP
    fi
    local num_of_nodes=$4
    if [ -z "$num_of_nodes" ]; then
        local num_of_nodes=1
    fi
    
    local execution_time=`jq -r .duration $WORK_DIR/$FILTER_RESULT_FILE`
    local num_of_params=`jq -r '.parameters[]' $1 | wc -l`
    local input_folder=`jq -r .input_folder $1`
    local dataset_size=`du -sb $input_folder/ | awk '{print $1}'`
    local output_file=`jq -r .output_file $1`
    local output_file_size=$(wc -c <"$output_file")
#     if [ "$output_file_size" -gt "86" ]; then
        local conf=$(jq . $1)
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
                local count=0
                local date_count=0
                local NEXT_DATE=$(date +"%Y-%m-%dT%H:%M:%SZ" -d "$DATE + $k year")
                local NEXT_DATE_SECONDS=`date -d "$NEXT_DATE" +%s`
                local parameters=9
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
    local extra_mils=0
    while read line; do
        node_ip=`echo $line | awk -F "@" '{print $2}'`
        while [ -f /tmp/$node_ip.run ]
        do
            local extra_mils=$((extra_mils+100))
            sleep 0.1
            dbg ${FUNCNAME[0]} "extra_mils: "$extra_mils
        done
    done < $SSH_FILE
    END_EXECUTION=$(($(date +%s%N)/1000000))
    END_EXECUTION=$((END_EXECUTION-extra_mils))
}


function run() {
    local FILTER_RESULT_FILE=`date +%s | sha256sum | base64 | head -c 8 ; echo`.out
    python $WORK_DIR/generation_argo_big_data.py $1 &> $WORK_DIR/$FILTER_RESULT_FILE
    parseResult $1 $WORK_DIR/$FILTER_RESULT_FILE
}

function run_ssh() {
    local ssh_count=0
    EXECUTION_DATE=`date +%Y-%m-%dT%H:%M:%SZ`
    START_EXECUTION=$(($(date +%s%N)/1000000))
    while read node; do
        scp -i $KEY_PATH $ssh_count"_"configuration_new.json $node:/mnt/data/source &> /dev/null   
        local node_ip=`echo $node | awk -F "@" '{print $2}'`
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
    local extra_mils=20000
    sleep 20
    sned_index=0
    for (( sned_i=0; sned_i<=$NUMBER_OF_NODES; sned_i++ ))
    do  
        q_name=`curl -s -u guest:guest http://$RMQ_HOST:15672/api/queues/ | jq -r .[$sned_i].name`
        if [ $q_name = "task_queue" ]; then
            sned_index=$sned_i
            break
        fi
    done
    q_size=`curl -s -u guest:guest http://$RMQ_HOST:15672/api/queues/ | jq -r .[$sned_index].messages`
#     q_size=`python task.py $RMQ_HOST $RMQ_PORT 0_configuration_new.json task_queue`
#     echo task_queue $q_size
    while [ $q_size -ge 1 ]
    do
#         echo task_queue $q_size
#         q_size=`python task.py $RMQ_HOST $RMQ_PORT 0_configuration_new.json task_queue`
        q_size=`curl -s -u guest:guest http://$RMQ_HOST:15672/api/queues/ | jq -r .[$sned_index].messages`
#         extra_mils=$((extra_mils+100))
#         sleep 0.1
    done
        
#     for (( sned_i=0; sned_i<=$NUMBER_OF_NODES; sned_i++ ))
#     do  
#         q_name=`curl -s -u guest:guest http://$RMQ_HOST:15672/api/queues/ | jq -r .[$sned_i].name`
#         if [ $q_name = "task_queue_done" ]; then
#             sned_index=$sned_i
#             break
#         fi
#     done
#     extra_mils=$((extra_mils+10000))
#     echo "sleep 10"
#     sleep 10
#     python task.py $RMQ_HOST $RMQ_PORT 0_configuration_new.json consume
#     q_size=`curl -s -u guest:guest http://$RMQ_HOST:15672/api/queues/ | jq -r .[$sned_index].messages`
#     echo task_queue_done $q_size
#     while [ $q_size -ge 1 ]
#     do
#         echo python task.py $RMQ_HOST $RMQ_PORT 0_configuration_new.json consume
#         python task.py $RMQ_HOST $RMQ_PORT 0_configuration_new.json consume   
#         extra_mils=$((extra_mils+6000))
#         sleep 6
#         q_size=`curl -s -u guest:guest http://$RMQ_HOST:15672/api/queues/ | jq -r .[$sned_index].messages`
#         echo task_queue_done $q_size
#         if [ "$q_size" -le "0" ]; then
#             break
#         fi
#     done
    END_EXECUTION=$(($(date +%s%N)/1000000))
    END_EXECUTION=$((END_EXECUTION-extra_mils))
    parse_dist_result "configuration_new.json"
}


function run_parameter_sweep_distributed_ssh() {
    local count_all=0
    #Set latitude
    for (( ssh_i=$LAT_START; ssh_i<=$MAX_LAT; ssh_i=ssh_i+$STEP ))
    do
        # Set longitude
        for (( j=$LON_START; j<=$MAX_LON; j=j+$STEP ))
        do
            for (( k=1; k<=21; k=k+10))
            do
                local count=0
                local date_count=0
                local NEXT_DATE=$(date +"%Y-%m-%dT%H:%M:%SZ" -d "$DATE + $k year")
                local NEXT_DATE_SECONDS=`date -d "$NEXT_DATE" +%s`
                local parameters=9
                while read l; do
                    local count=$((count+1))
                    local parameters=$parameters","$l
                    if [ "$count" -gt "200" ]; then
                        newConf $1 $ssh_i $j $NEXT_DATE $parameters
                        python partitioning.py configuration_new.json $SSH_FILE
                        run_ssh
                        local count_all=$((count_all+1))
                        local count=0
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
    done
    parse_dist_result "configuration_new.json"
}


function run_parameter_sweep_distributed_rabbit() {
    all_parameters="9, 11, 12, 13, 20, 28, 30, 35, 43, 44, 45, 50, 54, 55, 58, 59, 60, 61, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 82, 83, 84, 87, 88, 89, 90, 94, 95, 96, 97, 98, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 114, 124, 132, 133, 135, 139, 145, 146, 147, 148, 150, 151, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 180, 183, 184, 188, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 500, 501, 502, 504, 505, 506, 508, 509,  510, 511, 512, 513, 514, 515, 516, 517, 520, 521, 522, 523, 524, 525, 526, 534, 535, 536, 542, 543, 544, 545, 546, 547, 548, 549, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645"    
    local GLOBAL_COUNT=0
    #Set latitude
#     for (( i_rabbit=$LAT_START; i_rabbit<=$MAX_LAT; i_rabbit=i_rabbit+$STEP ))
#     do
#         # Set longitude
#         for (( j=$LON_START; j<=$MAX_LON; j=j+$STEP ))
#         do
#             for (( k=1; k<=21; k=k+5))
#             do
#                 local count=0
#                 local date_count=0
#                 local NEXT_DATE=$(date +"%Y-%m-%dT%H:%M:%SZ" -d "$DATE + $k year")
#                 local NEXT_DATE_SECONDS=`date -d "$NEXT_DATE" +%s`
#                 local parameters=9
#                 while read l; do
#                     local count=$((count+1))
#                     local parameters=$parameters","$l
#                     if [ "$count" -gt "200" ]; then
#                         newConf $1 $i_rabbit $j $NEXT_DATE $parameters
#                         python partitioning.py configuration_new.json $NUMBER_OF_NODES
#                         send_messages
#                         local GLOBAL_COUNT=$((GLOBAL_COUNT+1))
#                         local count=0
#                     fi
#                 done <physical_parameter_keys.txt
#                 newConf $1 $i_rabbit $j $NEXT_DATE $parameters
#                 python partitioning.py configuration_new.json $NUMBER_OF_NODES
#                 send_messages        
#             done        
#             newConf $1 $i_rabbit $j $MAX_DATE $parameters
#             python partitioning.py configuration_new.json $NUMBER_OF_NODES
#             send_messages
#         done
#         newConf $1 $i_rabbit $MAX_LON $MAX_DATE $parameters
#         python partitioning.py configuration_new.json $NUMBER_OF_NODES
#         send_messages
#     done
    newConf $1 $MAX_LAT $MAX_LON $MAX_DATE "9, 11, 12, 13, 20, 28, 30, 35, 43, 44, 45, 50, 54, 55, 58, 59, 60, 61, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 82, 83, 84, 87, 88, 89, 90, 94, 95, 96, 97, 98, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 114, 124, 132, 133, 135, 139, 145, 146, 147, 148, 150, 151, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 180, 183, 184, 188, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 500, 501, 502, 504, 505, 506, 508, 509,  510, 511, 512, 513, 514, 515, 516, 517, 520, 521, 522, 523, 524, 525, 526, 534, 535, 536, 542, 543, 544, 545, 546, 547, 548, 549, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645"
    python partitioning.py configuration_new.json $NUMBER_OF_NODES
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

NUMBER_OF_NODES=`python getNumberOfConsumers.py $RMQ_HOST 15672 task_queue`


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
