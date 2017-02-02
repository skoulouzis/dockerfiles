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
#$MONTAGE_BIN/mArchiveList dss ${bands} "56.5 23.75" 3 3 remote.tbl;
#$MONTAGE_BIN/mArchiveExec remote.tbl;
cd .. ;
$MONTAGE_BIN/mImgtbl raw rimages.tbl ;
$MONTAGE_BIN/mProjExec -p raw rimages.tbl ../pleiades.hdr projected stats.tbl ;
$MONTAGE_BIN/mImgtbl projected pimages.tbl ;
$MONTAGE_BIN/mAdd -p projected pimages.tbl ../pleiades.hdr ${bands}.fits ;
cd .. ;
done

$MONTAGE_BIN/mJPEG -blue DSS2B/DSS2B.fits -1s 99.999% gaussian-log \
    -green DSS2R/DSS2R.fits -1s 99.999% gaussian-log \
    -red DSS2IR/DSS2IR.fits -1s 99.999% gaussian-log \
    -out DSS2_BRIR.jpg