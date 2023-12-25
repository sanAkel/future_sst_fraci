# Main purpose is to create SST and ice concentration for future

## Ideas are laid out in: [plan_work.md](https://github.com/sanAkel/future_sst_fraci/blob/main/plan_work.md)

## Relies on functional executables built from [GEOS-ESM/GEOS_Util](https://github.com/GEOS-ESM/GEOS_Util/tree/main/pre/prepare_ocnExtData)

# Layout of contents:

- diff_binned_interpolate/

  Because a choice was made (around 2012, MERRA-2 context) to bin 1/20-deg OSTIA datasets to 1/8-deg instead of (conservative: sea ice!) interpolation,
  plot the difference between the two approaches.
  
  - Remarks:
    1. Which of the two approaches is _better_? (We need comparisons with observations: RT)
    2. Given the overall plan of using coupled model (ocean model) and relax to SST, we should switch to interpolated data- use we ESMF and
       _some_ day this step can be done on-line (on the fly; Ben connection: when we get there). Relaxation can be interpreted as on _operator_...

- gen_daily_clim/

  - Used for generating daily climatology, see script: get_daily_clim.py
  - You need `cal_daily_clim.x` to be built, available from GEOS-ESM/GEOS_Util, 
    source code: `daily_clim_SST_FRACI_eight.F90`

- plot_GMAO_OPS_bin_data/

  To plot GMAO OPS 1/8-deg binned datasets using grads- note the data is binary. There is an option to read/write that binary to netcdf, 
  [see here.](https://github.com/GEOS-ESM/GEOS_Util/tree/main/pre/prepare_ocnExtData)
