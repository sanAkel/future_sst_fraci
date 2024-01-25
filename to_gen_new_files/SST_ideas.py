#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

get_ipython().run_line_magic('matplotlib', 'inline')


land_sea_mask = xr.open_dataset("/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/gen_daily_clim_data/data/geos_fp_bcs_land_sea_mask.nc")
my_mask = land_sea_mask.land_mask.values


# file names: real data and daily climatology
def get_files_names(dates, data_path, file_pref, clim=False, file_suff=".nc"):
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

# We need to mask out land
def apply_mask( input_field, mask, tol=0.1):
  output_field = np.copy( input_field)
  output_field [mask<tol] = np.nan
  return output_field

# mask land
def mask_array(ds, iTime, vName='SST', mask=my_mask):
    arr = ds[vName].isel(time=iTime).values
    masked_arr=apply_mask(arr, mask)
    return masked_arr

# to write forecast stats
def write_stats(vName, var):
    f1 = vName + "_{}_{}.csv".format(exp_dates[0].strftime('%Y%m%d'), exp_dates[-1].strftime('%Y%m%d'))
    print("Writing out: ", f1)
    np.savetxt(f1, (var), delimiter=",", fmt='%1.4f')
    print("Done!")


def forecast_bc(method, id, bc0, clim_bc, anomaly0):
    
    predicted_bc = np.zeros_like(bc0) # init to be safe!
    
    if method == "persist":
        predicted_bc = bc0 # persistence throughout the forecast
    elif method == "persist_init_anom":
        if (id==0):
            predicted_bc = bc0 # forecast start day
        else:
            predicted_bc = clim_bc + anomaly0
    elif method == "test3":
        if (id==0):
            predicted_bc = bc0 # forecast start day
        else:
            predicted_bc = clim_bc - anomaly0
    elif method == "test4":
        if (id==0):
            predicted_bc = bc0 # forecast start day
        else:
            predicted_bc = bc0 + anomaly0       
    else:
        print("Uknown method: {} for creating future BCs.".format(method))
        
    return predicted_bc    


fcst_nDays, nfcst = [10, 90]

start_date, end_date = ['2023-06-01', '2023-09-01'] # end_date must fit above.

data_path_real = "/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/GMAO_OPS_bin_data/data/"
data_path_clim = "/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/data/ncFiles/"

file_pref_real, file_suff = ["sst_ice_", ".nc"]
file_pref_clim, file_suff = ["daily_clim_mean_sst_fraci_", ".nc"]

# Select _forecast_ method
#method = "persist" 
method = "persist_init_anom"
#method = "test3"
#method = "test4"

vName = 'FRACI'


# One forecast per day, since this is daily BCs.
exp_dates  = pd.date_range(start_date, end_date, freq='D')


mean_spatial_error = np.full((fcst_nDays, my_mask.shape[0], my_mask.shape[1]), 0.0)

# With respect to real data -- remember, we _test_ in **hindcast** mode, so we know the _truth_.
mean_error = np.zeros((fcst_nDays, nfcst), dtype=np.float64)
sdev_error = np.zeros_like( mean_error)

# With respect to daily climatology
mean_error_clim = np.zeros((fcst_nDays, nfcst), dtype=np.float64)
sdev_error_clim = np.zeros_like( mean_error_clim)


for ifcst in range(1, nfcst+1): # each forecast

  fcst_start_date = exp_dates[0] + pd.DateOffset(days=ifcst-1)
  fcst_dates = pd.date_range(start=fcst_start_date, periods=fcst_nDays)
  print("Forecast [{}] Dates: {}".format(ifcst,fcst_dates))

  files_names_real_data = get_files_names(fcst_dates, data_path_real, file_pref_real)
  clim_files_names      = get_files_names(fcst_dates, data_path_clim, file_pref_clim, clim=True)

  ds_real = xr.open_mfdataset(files_names_real_data)
  ds_clim = xr.open_mfdataset(clim_files_names, concat_dim='time', combine='nested', use_cftime=True)

  for id in range(0, fcst_nDays): # over each day of forecast
    if (vName == 'SST'):
        real_bc = mask_array(ds_real, id); clim_bc = mask_array(ds_clim, id)
    else:
        real_bc = mask_array(ds_real, id, vName); clim_bc = mask_array(ds_clim, id, vName)

    # save initial BC (SST/ICE)
    if (id==0):
      bc0 = real_bc; anom0 = bc0 - clim_bc
   
    predicted_bc = forecast_bc(method, id, bc0, clim_bc, anom0)
    
    error_real = predicted_bc - real_bc
    error_clim = clim_bc - real_bc # difference from climatology- if clim was used
    
    # unweighted global mean and std. dev. <-- add weighting
    mean_error[id,ifcst-1], sdev_error[id, ifcst-1] =\
    [np.nanmean(error_real.flatten(), dtype=np.float64), np.nanstd(error_real.flatten(), dtype=np.float64)]

    mean_error_clim[id,ifcst-1], sdev_error_clim[id, ifcst-1] =\
    [np.nanmean(error_clim.flatten(), dtype=np.float64), np.nanstd(error_clim.flatten(), dtype=np.float64)]
    
    if (ifcst ==1): # first forecast
        mean_spatial_error[id,:,:] = error_real
    else:
        mean_spatial_error[id,:,:] = mean_spatial_error[id,:,:] + error_real
#    
for id in range(0, fcst_nDays):
    mean_spatial_error[id,:,:] = mean_spatial_error[id,:,:]/nfcst    


plt.figure( figsize=(12, 4))
plt.subplot(121)
for id in range(0, nfcst):
  plt.plot(range(0, fcst_nDays), mean_error[:,id],      ls='-', c='b', alpha=0.05)
  plt.plot(range(0, fcst_nDays), mean_error_clim[:,id], ls='-', c='k', alpha=0.05)

x1 = np.zeros( (fcst_nDays), dtype=np.float64)
x2 = np.zeros_like(x1)
for id in range(0, fcst_nDays):
    x1[id] = np.mean(mean_error[id,:],  dtype=np.float64)
    x2[id] = np.mean(mean_error_clim[id,:],  dtype=np.float64)
plt.plot(range(0, fcst_nDays), x1, ls='-', c='b', lw=2)
plt.plot(range(0, fcst_nDays), x2, ls='-', c='k', lw=2)

plt.title('Global mean error')
plt.xlabel('Forecast days')
plt.grid(True)
plt.ylim(-0.5, 0.5)
#
plt.subplot(122)
for id in range(0, nfcst):
  plt.plot(range(0, fcst_nDays), sdev_error[:,id],      ls='-', c='b', alpha=0.5)
  plt.plot(range(0, fcst_nDays), sdev_error_clim[:,id], ls='-', c='k', alpha=0.5)
plt.title('SDEV of global mean error')
plt.xlabel('Forecast days')
plt.grid(True)
plt.ylim(0., 1.0)


print("Forecast Day\tGlobal Mean Error (time-series)\tFrom spatial maps\t Difference between the two methods\n")

for id in range(0, fcst_nDays):
    x1 = np.nanmean( mean_spatial_error[id,:,:], dtype=np.float64)
    x2 = np.mean(mean_error[id,:], dtype=np.float64)
    print(id+1,"\t\t",x1,"\t\t",x2,"\t",x2-x1)
    
print("\n--> If both methods give same answer, (last column == 0), all good!")    


if vName == 'SST':
    cMin, cMax = [-1., 1.]
else:
    cMin, cMax = [-.2, .2]

plt.figure( figsize=(16, 10))

for id in range(0, fcst_nDays):
    plt.subplot(4, 3, id+1)
    plt.pcolormesh(land_sea_mask.lon.values, land_sea_mask.lat.values,\
                   mean_spatial_error[id,:,:], vmin=cMin, vmax=cMax, cmap=plt.cm.bwr)
    plt.colorbar()
    plt.title('day: {}'.format(id))


write_stats('mean_{}_error_'.format(vName) + method, mean_error)
write_stats('sdev_{}_error_'.format(vName) + method, sdev_error)

write_stats('mean_{}_error_clim_'.format(vName) + method, mean_error_clim)
write_stats('sdev_{}_error_clim_'.format(vName) + method, sdev_error_clim)


da = xr.DataArray(data=mean_spatial_error, 
coords={'time': np.arange(0, fcst_nDays), 'lat': land_sea_mask.lat,'lon': land_sea_mask.lon}, 
dims=["time", "lat", "lon"],
attrs=dict(description="Mean of forecast error in BCs, see https://github.com/sanAkel/future_sst_fraci/blob/main/to_gen_new_files/SST_ideas.ipynb"))

ds_bc_err = da.to_dataset(name='{}_fcst_error'.format(vName))

# vName = SST, FRACI
#ds_bc_err.SST_fcst_error.plot(x="lon", y="lat", col="time", col_wrap=3, vmin=cMin, vmax=cMax, cmap=plt.cm.bwr)
#ds_bc_err.FRACI_fcst_error.plot(x="lon", y="lat", col="time", col_wrap=3, vmin=cMin, vmax=cMax, cmap=plt.cm.bwr)

ds_bc_err.to_netcdf("{}_mean_err_{}_{}_{}.nc".format(vName, method, exp_dates[0].strftime('%Y%m%d'), exp_dates[-1].strftime('%Y%m%d')))


# Initialize
sdev_spatial_error = np.zeros_like(mean_spatial_error)
sum_sq_spatial_error = np.zeros_like(mean_spatial_error)


for ifcst in range(1, nfcst+1): # each forecast

  fcst_start_date = exp_dates[0] + pd.DateOffset(days=ifcst-1)
  fcst_dates = pd.date_range(start=fcst_start_date, periods=fcst_nDays)
  print("Forecast [{}] Dates: {}".format(ifcst,fcst_dates))

  files_names_real_data = get_files_names(fcst_dates, data_path_real, file_pref_real)
  clim_files_names      = get_files_names(fcst_dates, data_path_clim, file_pref_clim, clim=True)

  ds_real = xr.open_mfdataset(files_names_real_data)
  ds_clim = xr.open_mfdataset(clim_files_names, concat_dim='time', combine='nested', use_cftime=True)

  for id in range(0, fcst_nDays): # over each day of forecast
    if (vName == 'SST'):
        real_bc = mask_array(ds_real, id); clim_bc = mask_array(ds_clim, id)
    else:
        real_bc = mask_array(ds_real, id, vName); clim_bc = mask_array(ds_clim, id, vName)

    # save initial BC (SST/ICE)
    if (id==0):
      bc0 = real_bc; anom0 = bc0 - clim_bc
   
    predicted_bc = forecast_bc(method, id, bc0, clim_bc, anom0) 
    error_real = predicted_bc - real_bc
    
    if (ifcst ==1): # first forecast
        sum_sq_spatial_error[id,:,:] = (error_real-mean_spatial_error[id,:,:])**2.
    else:
        sum_sq_spatial_error[id,:,:] = sum_sq_spatial_error[id,:,:] + (error_real-mean_spatial_error[id,:,:])**2.
#    
for id in range(0, fcst_nDays):
    sdev_spatial_error[id,:,:] = np.sqrt(sum_sq_spatial_error[id,:,:]/(nfcst-1)) # sample (n-1), not population (n).  


if vName == 'SST':
    cMin, cMax = [0.05, 2.]
else:
    cMin, cMax = [0.01, .5]

plt.figure( figsize=(16, 10))

for id in range(0, fcst_nDays):
    plt.subplot(4, 3, id+1)
    plt.pcolormesh(land_sea_mask.lon.values, land_sea_mask.lat.values,\
                   sdev_spatial_error[id,:,:], vmin=cMin, vmax=cMax, cmap=plt.cm.Spectral_r)
    plt.colorbar()
    plt.title('day: {}'.format(id))


da = xr.DataArray(data=sdev_spatial_error, 
coords={'time': np.arange(0, fcst_nDays), 'lat': land_sea_mask.lat,'lon': land_sea_mask.lon}, 
dims=["time", "lat", "lon"],
attrs=dict(description="Standard deviation of forecast error in BCs, see https://github.com/sanAkel/future_sst_fraci/blob/main/to_gen_new_files/SST_ideas.ipynb"))

ds_bc_err = da.to_dataset(name='{}_fcst_error'.format(vName))

# vName = SST, FRACI
#ds_bc_err.SST_fcst_error.plot(x="lon", y="lat", col="time", col_wrap=3, vmin=cMin, vmax=cMax, cmap=plt.cm.Spectral_r)
#ds_bc_err.FRACI_fcst_error.plot(x="lon", y="lat", col="time", col_wrap=3, vmin=cMin, vmax=cMax, cmap=plt.cm.Spectral_r)

ds_bc_err.to_netcdf("{}_sdev_err_{}_{}_{}.nc".format(vName, method, exp_dates[0].strftime('%Y%m%d'), exp_dates[-1].strftime('%Y%m%d')))

