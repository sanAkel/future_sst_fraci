#!/bin/csh

#SBATCH --time=1:00:00
#SBATCH --ntasks=24
#SBATCH --constraint=mil
#SBATCH --partition=scutest
#SBATCH --job-name=cube_BCs
#SBATCH -o cube_bcs_log.o%j
#SBATCH -e cube_bcs_log.e%j

#set echo

if ( $?date_range) then 
 echo ${date_range}
else
 exit 1
endif

set vName = ice
set FVBIN = /discover/nobackup/sakella/geosMom6/develop_20Feb2024/install/bin
set outDir = /discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/to_gen_new_files/fcst_data_${date_range}_${vName}

unset echo
source $FVBIN/g5_modules

if (-e $outDir) then
  cd $outDir
else
  echo "Output dir: " $outDir "does not exist. Exiting!"
  exit 999
endif

mpirun -np 24 $FVBIN/regrid_forcing.x

# sbatch --export=date_range=20230714_20230728,vName=ice ice_cube_bcs.j
# sbatch --export=date_range=20230714_20230728 ice_cube_bcs.j
