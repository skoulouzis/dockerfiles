 #!/bin/bash
        

#Mediterranean
MIN_LAT=-3
MAX_LAT=35
MIN_LON=31
MAX_LON=44
STEP=4
# Set date
DATE=1999-01-01T00:00:19Z
CIRCUMFERENCE=40091147 



function newConf() {
    
    sed "s/\"geospatial_lat_min\": 0,/\"geospatial_lat_min\": $MIN_LAT".00",/" configuration.json > configuration_new.json
    sed -i "s/\"geospatial_lon_min\": 0,/\"geospatial_lon_min\": $MIN_LON".00",/" configuration_new.json
    sed -i "s/\"geospatial_lat_max\": 0,/\"geospatial_lat_max\": $1".00",/" configuration_new.json
    sed -i "s/\"geospatial_lon_max\": 0/\"geospatial_lon_max\": $2".00"/" configuration_new.json
    sed -ie "s/\"time_coverage_end\":.*/\"time_coverage_end\": \"$3\"/" configuration_new.json
    sed -ie "s/\"parameters\":.*/\"parameters\": [\"$4\"],/" configuration_new.json
    
#     echo geospatial_lat_min $MIN_LAT geospatial_lon_min $MIN_LON geospatial_lat_max $1".00" geospatial_lon_max $2".00" time_coverage_end $3 parameter $4
#     cat configuration_new.json
}



function parseResult(){
    if [ ! -f $1 ]; then
        echo "[" > $1
    fi

    sed -ie 's/duration (seconds)/duration/g' out
    time_coverage_start=`jq -r .time_range.time_coverage_start configuration_new.json`
    time_coverage_end=`jq -r .time_range.time_coverage_end configuration_new.json`
    start=`date -d "$time_coverage_start" +%s`
    end=`date -d "$time_coverage_end" +%s`
    time_coverage=`echo "$end + $start" | bc`
    
    
    geospatial_lat_min=`jq -r .bounding_box.geospatial_lat_min configuration_new.json`
    geospatial_lat_max=`jq -r .bounding_box.geospatial_lat_max configuration_new.json`
    geospatial_lon_min=`jq -r .bounding_box.geospatial_lon_min configuration_new.json`
    geospatial_lon_max=`jq -r .bounding_box.geospatial_lon_max configuration_new.json`
    
    area=`python coordinates2Area.py $geospatial_lat_min $geospatial_lon_min $geospatial_lat_max $geospatial_lon_max`
    
    date=`jq -r .date out`
    execution_time=`jq -r .duration out`
    num_of_params=`jq -r '.parameters[] | length' configuration_new.json`
    input_folder=`jq -r .input_folder configuration_new.json`
    dataset_size=`du -sb $input_folder/ | awk '{print $1}'`
    output_file=`jq -r .output_file configuration_new.json`
    output_file_size=$(wc -c <"$output_file")
    
    echo "{" \"area\": $area, \"time_coverage\": \"$time_coverage\", \"num_of_params\": \"$num_of_params\", \"dataset_size\": \"$dataset_size\", \"output_file_size\": \"$output_file_size\", \"execution_time\": \"$execution_time\",\"execution_date\": \"$date\""}," >> $1 
}


#Set latitude
for (( i=$MIN_LAT; i<=$MAX_LAT; i=i+$STEP ))
do
    # Set longitude
    for (( j=$MIN_LON; j<=$MAX_LON; j=j+$STEP ))
    do
        for (( k=1; k<=25; k=k+10))
        do
        count=0
        NEXT_DATE=$(date +"%Y-%m-%dT%H:%M:%SZ" -d "$DATE + $k year")
        parameters=9
        while read l; do
            count=$((count+1))
            parameters=$parameters","$l
            if [ "$count" -gt "200" ]; then
                count=0
                newConf $i $j $NEXT_DATE $parameters
                ./generation_argo_big_data.csh configuration_new.json &> out
                parseResult $4
            fi
            
        done <physical_parameter_keys.txt

        done        
    done
done
            
echo "]" >> $1