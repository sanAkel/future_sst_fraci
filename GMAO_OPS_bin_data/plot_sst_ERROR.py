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

data_path_clim = "/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/data/ncFiles/"
data_path_real = "/discover/nobackup/projects/gmao/advda/sakella/future_sst_fraci/GMAO_OPS_bin_data/data/"

ds_real = xr.open_mfdataset(data_path_real + "sst_fraci_*.nc4")
ds_clim = xr.open_mfdataset(data_path_clim + "daily_clim_mean_sst_fraci_000101*.nc", concat_dim='time', combine='nested', use_cftime=True)

nT = ds_real.time.shape[0]
mean_pers = np.zeros((nT,), dtype=np.float64)
rmse_pers = np.zeros_like( mean_pers)

mean_clim = np.zeros_like( mean_pers)
rmse_clim = np.zeros_like( mean_pers)
# There is no point in working with ice, since coverage varies everyday!

for id in range(0, nT):
  daily_sst_real = ds_real.isel(time=id).SST.values
  daily_sst_clim = ds_clim.isel(time=id).SST.values

  real_sst_masked=apply_mask(daily_sst_real, my_mask)
  clim_sst_masked=apply_mask(daily_sst_clim, my_mask)

  # Difference from persistence
  if (id==0):
    sst0 = real_sst_masked

  dsst_pers = (real_sst_masked - sst0).flatten()
  dsst_clim = (real_sst_masked - clim_sst_masked).flatten()

  # unweighted.
  mean_pers[id], rmse_pers[id] = [np.nanmean(dsst_pers, dtype=np.float64), np.nanstd(dsst_pers, dtype=np.float64)]
  mean_clim[id], rmse_clim[id] = [np.nanmean(dsst_clim, dtype=np.float64), np.nanstd(dsst_clim, dtype=np.float64)]

plt.figure( figsize=(8, 4))
plt.subplot(121)
plt.plot(range(0, nT), mean_pers, 'b.-', label='Persistence')
plt.plot(range(0, nT), mean_clim, 'g.-', label='Climatology')
plt.legend()
plt.title('Global mean error ($^\circ$K)')

plt.subplot(122)
plt.plot(range(0, nT), rmse_pers, 'b.-', label='Persistence')
plt.plot(range(0, nT), rmse_clim, 'g.-', label='Climatology')
#plt.legend()
plt.title('RMSE ($^\circ$K)')
plt.show()
