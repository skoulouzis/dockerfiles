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



function parseResult() {
    sed -i 's/duration (seconds)/duration/g' out
    time_coverage_start=`jq -r .time_range.time_coverage_start $1`
    time_coverage_end=`jq -r .time_range.time_coverage_end $1`
    if [ -z "$time_coverage_start" ] || [ -z "$time_coverage_end" ] ; then
        echo "time_coverage was empty" 
        exit
    fi
    
    time_coverage=`python getDelta.py $time_coverage_start $time_coverage_end`
    
    geospatial_lat_min=`jq -r .bounding_box.geospatial_lat_min $1`
    geospatial_lat_max=`jq -r .bounding_box.geospatial_lat_max $1`
    geospatial_lon_min=`jq -r .bounding_box.geospatial_lon_min $1`
    geospatial_lon_max=`jq -r .bounding_box.geospatial_lon_max $1`
    
    area=`python coordinates2Area.py $geospatial_lat_min $geospatial_lat_max $geospatial_lon_min $geospatial_lon_max`
    
    date=`jq -r .date out`
    if [ -z "$date" ]; then
        echo "output file was malformed" 
        exit
    fi
     
    execution_time=`jq -r .duration out`
    num_of_params=`jq -r '.parameters[] | length' $1`
    input_folder=`jq -r .input_folder $1`
    dataset_size=`du -sb $input_folder/ | awk '{print $1}'`
    output_file=`jq -r .output_file $1`
    output_file_size=$(wc -c <"$output_file")
    
    conf=`jq . $1`
    echo "{" \"area\": $area, \"time_coverage\": $time_coverage, \"num_of_params\": $num_of_params, \"dataset_size\": $dataset_size, \"output_file_size\": $output_file_size, \"execution_time\": $execution_time,\"execution_date\": \"$date\" , \"configuration\": $conf "}"
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



function run() {
    ./generation_argo_big_data.csh $1 &> out
    parseResult $1
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
esac
done

# echo OPERATION = ${OPERATION}
# echo JSON_CONF_FILE = ${JSON_CONF_FILE}
# echo CONF_FILE = ${CONF_FILE}

source ${CONF_FILE}


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
esac


# this="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
# grep "function" $this | awk '{print $2}' 
