#!/usr/bin/env python3

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

# To apply land-sea mask
land_sea_mask = xr.open_dataset("/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/gen_daily_clim_data/data/geos_fp_bcs_land_sea_mask.nc")
my_mask = land_sea_mask.land_mask.values
# --

def get_files_names(dates, data_path, file_pref, file_suff, clim=False):
   files_to_read = []
   for idate in dates:

     if (clim==False): # real data
       ff = data_path + str(idate.year) + "/" +\
            file_pref + str(idate.year) + str(idate.month).zfill(2) + str(idate.day).zfill(2) +\
            file_suff
     else:
       ff = data_path + "/"+\
            file_pref + "0001" + str(idate.month).zfill(2) + str(idate.day).zfill(2) +\
            file_suff

     #print(ff)
     files_to_read.append(ff)
   return files_to_read

def apply_mask( input_field, mask, tol=0.1):
  output_field = np.copy( input_field)
  output_field [mask<tol] = np.nan
  return output_field
# --

fcst_nDays, nfcst = [10, 30]
start_date, end_date = ['2017-06-01', '2017-07-01'] # end_date must fit above.
data_path_real = "/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/GMAO_OPS_bin_data/data/"
data_path_clim = "/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/data/ncFiles/"

file_pref_real, file_suff = ["sst_ice_", ".nc"]
file_pref_clim, file_suff = ["daily_clim_mean_sst_fraci_", ".nc"]
# --

exp_dates  = pd.date_range(start_date, end_date, freq='D')

mean_error = np.zeros((fcst_nDays, nfcst), dtype=np.float64)
sdev_error = np.zeros_like( mean_error)
spatial_error = -999*np.ones((fcst_nDays, my_mask.shape[0], my_mask.shape[1]), dtype=np.float32)

# with respect to daily climatology
mean_error_clim = np.zeros((fcst_nDays, nfcst), dtype=np.float64)
sdev_error_clim = np.zeros_like( mean_error_clim)

for ifcst in range(1, nfcst+1):
  #print("Forecast: ", ifcst)
  fcst_start_date = exp_dates[0] + pd.DateOffset(days=ifcst-1)
  fcst_dates = pd.date_range(start=fcst_start_date, periods=fcst_nDays)
  print("Forecast Dates: ", fcst_dates)
  #print(" ")
  files_real_data = get_files_names(fcst_dates, data_path_real, file_pref_real, file_suff)
  clim_files      = get_files_names(fcst_dates, data_path_clim, file_pref_clim, file_suff, True)
  #print(files_real_data)
  #print(clim_files)
  #print(" ")
  ds_real = xr.open_mfdataset(files_real_data)
  ds_clim = xr.open_mfdataset(clim_files, concat_dim='time', combine='nested', use_cftime=True)

  for id in range(0, fcst_nDays):

    real_sst = ds_real.isel(time=id).SST.values
    clim_sst = ds_clim.isel(time=id).SST.values

    real_sst_masked=apply_mask(real_sst, my_mask)
    clim_sst_masked=apply_mask(clim_sst, my_mask)

    # save initial SST
    if (id==0):
      sst0 = real_sst_masked

    predicted_sst = sst0 # persistence throughout the forecast
    dsst_error = (real_sst_masked - predicted_sst).flatten()
    dsst_clim  = (real_sst_masked - clim_sst_masked).flatten() # use climatology as _best_ guess

    if (ifcst ==1):
      spatial_error[id,:,:] = (real_sst_masked - predicted_sst)
    else:
      spatial_error[id,:,:] = spatial_error[id,:,:] + (real_sst_masked - predicted_sst)

    # unweighted global mean and std. dev.
    mean_error[id,ifcst-1], sdev_error[id, ifcst-1] =\
    [np.nanmean(dsst_error, dtype=np.float64), np.nanstd(dsst_error, dtype=np.float64)]

    mean_error_clim[id,ifcst-1], sdev_error_clim[id, ifcst-1] =\
    [np.nanmean(dsst_clim, dtype=np.float64), np.nanstd(dsst_clim, dtype=np.float64)]
# --
spatial_error = spatial_error/nfcst
spatial_error[spatial_error < -900.] = np.nan

plt.figure( figsize=(8, 4))
plt.subplot(121)
for id in range(0, fcst_nDays):
  plt.plot(range(0, fcst_nDays), mean_error[:,id],      ls='-', c='b')
  plt.plot(range(0, fcst_nDays), mean_error_clim[:,id], ls='-', c='k')
plt.title('Global mean error ($^\circ$K)')
plt.xlabel('Forecast days')
#
plt.subplot(122)
for id in range(0, fcst_nDays):
  plt.plot(range(0, fcst_nDays), sdev_error[:,id],      ls='-', c='b')
  plt.plot(range(0, fcst_nDays), sdev_error_clim[:,id], ls='-', c='k')
plt.title('SDEV of global mean error ($^\circ$K)')
plt.xlabel('Forecast days')

plt.show()
