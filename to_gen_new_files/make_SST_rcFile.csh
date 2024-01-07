#!/bin/csh

# Inputs
# - user set
set input_bcs = $1 #real_sst_2880x1440_20170601_20170610.bin
set output = $2 #real_sst_C360_20170601_20170610.bin
set workDir = $3 #/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/to_gen_new_files/data_20170601_20170610_sst

# - fixed
set res_out = C360
set tileDir = /discover/nobackup/projects/gmao/bcs_shared/legacy_bcs/Icarus/Shared/
#--

set resX = `echo $res_out | cut -c2-`
@ resY = $resX * 6

set resX3 = $resX
if ($resX3 < 100) set resX3 = 0$resX3
set resX4 = 0$resX3
set tileIN = DE2880xPE1440_CF${resX4}x6C.bin

set out_im = $resX
set out_gridName = PE${resX}x${resY}-CF
set out_tiling_file = DE2880xPE1440_CF${resX4}x6C.bin

# create rc file
set rcfile = REGRID_FORCING.rc

cd $workDir
if (-e $rcfile) /bin/rm -f $rcfile
if (! -e $tileIN) ln -s $tileDir/$tileIN $tileIN

alias rcwrite "echo \!* >> $rcfile"
rcwrite RUN_DT: 1800
rcwrite
rcwrite NX: 4
rcwrite NY: 6
rcwrite 
rcwrite INPUT_GRIDNAME: PE2880x1440-DE
rcwrite INPUT_IM: 2880
rcwrite INPUT_JM: 1440
rcwrite INPUT_LM: 1
rcwrite 
rcwrite OUTPUT_GRIDNAME: $out_gridName
rcwrite OUTPUT_LM: 1
rcwrite OUTPUT_IM: $out_im
rcwrite 
rcwrite OUTPUT_TILING_FILE: $out_tiling_file
rcwrite 
rcwrite INPUT_FILE:  $input_bcs
rcwrite OUTPUT_FILE: $output

unset echo
echo "RC file: "$rcfile "is ready."
