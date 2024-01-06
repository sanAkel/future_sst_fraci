#!/bin/csh -f

#-- to build
# source /gpfsm/dnb33/sakella/geosMom6/v11.1.1/GEOSgcm/@env/g5_modules
# cd /gpfsm/dnb33/sakella/geosMom6/v11.1.1/GEOSgcm/build
# make cal_daily_clim.x
#-- 
umask 022
      
limit stacksize unlimited

setenv ARCH `uname`

setenv GEOSDIR /discover/nobackup/sakella/geosMom6/v11.1.1/GEOSgcm

source ${GEOSDIR}/@env/g5_modules
setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:${BASEDIR}/${ARCH}/lib:${GEOSDIR}/install/lib

#${GEOSDIR}/install/bin/cal_daily_clim.x
#${GEOSDIR}/build/bin/cal_daily_clim.x
${GEOSDIR}/build/bin/extract_daily_sst_ice.x 2023 1 5

# to plot bcs
#${GEOSDIR}/install/bin/plot_sst_ice.py -data_path /gpfsm/dnb33/sakella/projects/bcs_pert/tests/ -year 2023 -month 1 -day 1

# to plot diff: conservative (xesmf) - binned bcs
# first generate regridding weights: gen_wts_regrid_ostia_geos.py
plot_diff_ostia_native_regridded_binned.py 20230105


# to generate daily climatology
source $NOBACKUP/geosMom6/v11.1.1/GEOSgcm/@env/g5_modules
$NOBACKUP/geosMom6/v11.1.1/GEOSgcm/build/bin/cal_daily_clim.x 2007 2023 2 29
