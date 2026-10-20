# Run order — JRA55-do_ctrl_ERA5-forcings

These notebooks came from long linear notebooks, so some use variables computed in
others. Each notebook **loads** shared variables at the top (`load_state`) and **saves**
its own at the bottom (`save_state`), accumulating in `processed_data/state.pkl`.


## Phase 1 — compute / loaders (run first, in this order)

1. `inputs/obs_tas_huss_trends.ipynb` — builds & saves OAFlux tas/huss input trends.
2. `inputs/obs_wind_uas_vas_trends.ipynb` — builds & saves NOAA wind uas/vas input trends.
3. `cold_warm_metric/cw_calculations.ipynb` — **calculates everything** for the cold–warm metric (`cw_mean_omip`, percentiles, `mod_labs`, `control_percent_trend`, warm/cold-50% arrays, basin warming, trends, `noaa_sst_percentiles`) and saves it. (20% ranges removed.)
4. `omip_comparison/omip_percentiles.ipynb` — builds `percentiles_omip_trend` and OMIP percentile data.
5. `omip_comparison/omip_trend_maps_and_quivers.ipynb` — loads OMIP models (`gr_omip`, trends, quivers).

## Phase 2 — plotting / consumers (run after Phase 1)

The cold–warm plotting notebooks (run any of these after `cw_calculations.ipynb`):
- `cold_warm_metric/cw_percentile_difference_plots.ipynb`
- `cold_warm_metric/cw_gradient_fraction_plots.ipynb`
- `cold_warm_metric/cw_mean_basin_plots.ipynb`
- `cold_warm_metric/cw_trend_plots.ipynb`

Then the rest:
- `omip_comparison/omip_global_mean.ipynb`
- `cm2_om2_compare/cm2_om2_trends.ipynb`
- `cm2_om2_compare/cm2_om2_means.ipynb`
- `sst/era5_sst_vs_cobe.ipynb`
- `trends/trend_maps.ipynb`

> Tip: `load_state` prints which variables it loaded. If a plotting notebook still hits
> "name is not defined", a Phase-1 notebook that produces it hasn't been run (to its
> `save_state` cell) since the last kernel restart.
