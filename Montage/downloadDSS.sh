#!/bin/bash

# Pleiades Image creation BASH script.
# Inseok Song, 2007

MONTAGE_HOME=/root/Montage
MONTAGE_BIN=$MONTAGE_HOME/bin

for bands in DSS2B DSS2R DSS2IR; do echo Processing ${bands};
mkdir $bands;
cd $bands;
mkdir raw projected;
cd raw;
$MONTAGE_BIN/mArchiveList dss ${bands} "56.5 23.75" 3 3 remote.tbl;
$MONTAGE_BIN/mArchiveExec remote.tbl;
done