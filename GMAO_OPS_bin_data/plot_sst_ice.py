#!/usr/bin/env python3

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
#----

def apply_land_sea_mask(ds_in, ls_mask):
  # add mask to dataset
  ds_in = ds_in.assign(mask=ls_mask.mask)
  # apply mask: values are 1 and 9 are from OSTIA's mask variable
  test1 = ds_in.where( ds_in.mask == 1, 0) # values that are not equal to 1 are set to 0.
  test2 = ds_in.where( ds_in.mask == 9, 0) # values that are not equal to 9 are set to 0. mask (=9) is sea ice

  #masked_sst = (test1.SST + test2.SST).where(test1.SST + test2.SST > 0.) # makes ice edge nan. How to fix?? Try again later!
  #work within 60-deg latitude
  sst_masked = (test1.SST + test2.SST).where( (test1.SST + test2.SST > 0.) & (abs(test1.lat)<60.))
  ice_masked = test2.FRACI.where(test2.FRACI > 0.)

  ds_in = ds_in.assign(masked_sst = sst_masked)
  ds_in = ds_in.assign(masked_ice = ice_masked)
  return ds_in
#----

# read land sea mask. Was created using `gen_daily_clim/make_land_sea_mask.py`
ls_mask = xr.open_dataset("/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/diff_binned_interpolate/data/mask_geos_bcs.nc")

# Pick a binned 1/8 deg grid file
ds_geos = xr.open_dataset("data/" + "sst_fraci_20230101.nc4").squeeze()
ds_masked = apply_land_sea_mask(ds_geos, ls_mask)

# lagged difference
dss = xr.open_mfdataset("data/" + "sst_fraci_*.nc4")
dss_masked = apply_land_sea_mask(dss, ls_mask)
#(dss_masked.isel(time=1)-dss_masked.isel(time=0)).masked_sst.mean(('lat', 'lon')).values

nT=11
dSST_mean = np.zeros((nT,), dtype=np.float64)
dICE_mean = np.zeros_like( dSST)
dSST_rmse = np.zeros_like( dSST)
dICE_rmse = np.zeros_like( dSST)
for id in range(0, nT):
  dx = (dss_masked.isel(time=id)-dss_masked.isel(time=0))
  dSST_mean[id] = dx.masked_sst.mean(('lat', 'lon')).values
  dICE_mean[id] = dx.masked_ice.mean(('lat', 'lon')).values
  dSST_rmse[id] = np.sqrt( (dx.masked_sst**2).mean(('lat', 'lon')).values)
  dICE_rmse[id] = np.sqrt( (dx.masked_ice**2).mean(('lat', 'lon')).values)

#plt.subplot(221), plt.plot(range(0, 11), dSST_mean, 'b.-')
