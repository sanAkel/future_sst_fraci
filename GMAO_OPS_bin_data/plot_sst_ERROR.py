#!/usr/bin/env python3

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
#----

def apply_mask( input_field, mask, tol=0.1):
  output_field = np.copy( input_field)
  output_field [mask<tol] = np.nan
  return output_field

# Pick a binned 1/8 deg grid file
ds_geos = xr.open_dataset("data/" + "sst_fraci_20230101.nc4").squeeze()
sst_geos=ds_geos.SST.values

# Apply land-sea mask
land_sea_mask = xr.open_dataset("/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/gen_daily_clim/data/geos_fp_bcs_land_sea_mask.nc")
my_mask = land_sea_mask.land_mask.values
#sst_masked=apply_mask(sst_geos, my_mask)
#plt.pcolormesh(ds_geos.lon.values, ds_geos.lat.values, sst_masked), plt.colorbar(shrink=0.5)
#plt.show()

# Difference from persistence
dss = xr.open_mfdataset("data/" + "sst_fraci_*.nc4")

nT = dss.time.shape[0]
dSST_mean = np.zeros((nT,), dtype=np.float64)
dSST_rmse = np.zeros_like( dSST_mean)
# There is no point in working with ice, since coverage varies everyday!
for id in range(0, nT):
  daily_sst = dss.isel(time=id).SST.values
  sst_masked=apply_mask(daily_sst, my_mask)
  if (id==0):
    sst0 = sst_masked
  dsst = (sst_masked - sst0).flatten()
  # unweighted.
  dSST_mean[id], dSST_rmse[id] = [np.nanmean(dsst, dtype=np.float64), np.nanstd(dsst, dtype=np.float64)]

plt.figure( figsize=(8, 6))
plt.subplot(111)
plt.plot(range(0, nT), dSST_mean, 'b.-', label='mean (error)')
plt.plot(range(0, nT), dSST_rmse, 'k.-', label='RMSE (error)')
plt.legend()
plt.show()
