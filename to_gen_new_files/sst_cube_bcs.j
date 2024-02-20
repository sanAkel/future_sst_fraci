#!/bin/csh

#SBATCH --time=1:00:00
#SBATCH --ntasks=24
#SBATCH --constraint=mil
#SBATCH --partition=scutest
#SBATCH --job-name=cube_BCs
#SBATCH -o cube_bcs_log.o%j
#SBATCH -e cube_bcs_log.e%j

set echo

#set FVBIN  = $1
#set outDir = $2
#-- why above fails??
set FVBIN = /discover/nobackup/sakella/geosMom6/develop_20Feb2024/install/bin
set outDir = /discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/to_gen_new_files/fcst_data_20230714_20230728_sst

unset echo
source $FVBIN/g5_modules

if (-e $outDir) then
  cd $outDir
else
  echo "Output dir: " $outDir "does not exist. Exiting!"
  exit 999
endif

mpirun -np 24 $FVBIN/regrid_forcing.x
