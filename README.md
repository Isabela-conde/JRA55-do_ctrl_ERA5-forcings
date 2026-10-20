# JRA55-do_ctrl_ERA5-forcings

Analysis of **ACCESS-OM2 forcing-perturbation experiments** — JRA55-do control vs.
ERA5-derived forcings — focused on SST responses, percentile / cold-warm metrics, and the
observational input trends that drive the perturbations.

Carved out of the original `ACCESS-OM2-Atmosphere-Perturb` folder and reorganised into
focused notebooks. The original folder is left untouched as the source of truth.

## Structure

- **`omip_comparison/`**
  - `omip_trend_maps_and_quivers.ipynb` — OMIP SST trend maps with JRA55/MERRA2 wind quivers.
  - `omip_percentiles.ipynb` — SST percentile method & perturbation-SST percentiles.
  - `omip_global_mean.ipynb` — global-mean SST & wind-stress perturbation.
- **`cold_warm_metric/`**
  - `cw_load_and_percentile_plots.ipynb` — load data, percentiles & difference plots.
  - `cw_warm_cold_fractions_and_gradient.ipynb` — SST gradient & warm/cold fractions (50% / 20%).
  - `cw_mean_and_basin_warming.ipynb` — CW mean & basin warming.
  - `cw_trend_load_and_compute.ipynb` — cold–warm trend: load & compute.
  - `cw_trend_plots.ipynb` — cold–warm trend: plots.
- **`cm2_om2_compare/`**
  - `cm2_om2_trends.ipynb` — CM2 vs OM2 trend comparison (winds & radiation).
  - `cm2_om2_means.ipynb` — CM2 vs OM2 mean-state comparison.
- **`sst/era5_sst_vs_cobe.ipynb`** — ERA5 SST vs COBE SST.
- **`trends/trend_maps.ipynb`** — trend maps of forcing fields.
- **`inputs/`**
  - `obs_tas_huss_trends.ipynb` — OAFlux tas/huss input trends (saved as OM2 forcing inputs).
  - `obs_wind_uas_vas_trends.ipynb` — NOAA blended-wind uas/vas input trends (saved as OM2 forcing inputs).
- **`functions.py`** — shared helpers (`find_trend_values`, `pacific_mask`, `quantiles_xhist`, `find_trend_percentile`, `calculate_confidence_intervals_all`, …). Each notebook starts with a path-aware `from functions import *`.

