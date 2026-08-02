#!/usr/bin/env python
"""Absolute blended GMST from CMIP6 (SST over ocean + tas over land).

For each model, `historical` (1850-2014) is spliced with `ssp585` (2015-)
so the 1991-2020 window is fully covered. The surface field is blended as

    GMST = f_land * tas + (1 - f_land) * tos ,   f_land = sftlf / 100

then reduced with a cos-latitude area weight to a monthly global-mean series.

Outputs (written under OUT):
  - gmst_monthly_<model>.nc   monthly blended GMST timeseries (degC)
  - gmst_blended_cmip6.nc      (model x period) dataset: absolute GMST +
                               anomalies vs 1850-1900, with metadata

UKESM1-0-LL uses member r4i1p1f2; its sftlf (fixed field) is borrowed from
piControl since it is not published under historical.

Run on Gadi via gmst_blended_historical.sh.
"""
import os
import glob
from pathlib import Path

import numpy as np
import xarray as xr
import xesmf as xe

import warnings
warnings.filterwarnings('ignore')

OI10_CMIP = "/g/data/oi10/replicas/CMIP6/CMIP"
OI10_SCEN = "/g/data/oi10/replicas/CMIP6/ScenarioMIP"
OUT = "/g/data/e14/ic0706/CMIP/GMST_hist"

MODELS = {
    "CanESM5":      "r1i1p1f1",
    "IPSL-CM6A-LR": "r1i1p1f1",
    "MRI-ESM2-0":   "r1i1p1f1",
    "CESM2-WACCM":  "r1i1p1f1",
    "UKESM1-0-LL":  "r4i1p1f2",   # f2 member; sftlf borrowed from piControl
}

PERIODS = {
    "1850-1900": ("1850", "1900"),
    "1986-2005": ("1986", "2005"),
    "1991-2020": ("1991", "2020"),   # needs the ssp585 tail
}

TIME_CODER = xr.coders.CFDatetimeCoder(use_cftime=True)


def find(root, model, exp, member, table, var):
    """Return (grid, files) trying native then regular grids.

    Deduplicates by filename: the oi10 replica tree can expose the same
    file under several institution paths, which breaks combine='by_coords'.
    """
    for grid in ("gn", "gr", "gr1"):
        pattern = str(Path(root) / "*" / model / exp / member /
                      table / var / grid / "*" / "*.nc")
        uniq = {}
        for p in glob.iglob(pattern):
            if os.path.isfile(p):
                uniq.setdefault(os.path.basename(p), os.path.realpath(p))
        if uniq:
            return grid, [uniq[b] for b in sorted(uniq)]
    return None, []


def load_hist_ssp(model, member, var, table):
    """historical + ssp585 concatenated along time; preserves units attr."""
    _, hf = find(OI10_CMIP, model, "historical", member, table, var)
    _, sf = find(OI10_SCEN, model, "ssp585", member, table, var)
    if not hf:
        raise FileNotFoundError(f"no historical {var} for {model}")
    if not sf:
        raise FileNotFoundError(f"no ssp585 {var} for {model}")
    dh = xr.open_mfdataset(hf, combine='by_coords', decode_times=TIME_CODER)
    ds = xr.open_mfdataset(sf, combine='by_coords', decode_times=TIME_CODER)
    da = xr.concat([dh[var], ds[var].sel(time=slice('2015', None))],
                   dim='time', combine_attrs='override')
    da.attrs['units'] = dh[var].attrs.get('units', '')
    return da


def find_sftlf(model, member):
    """Locate sftlf: historical first, else the fixed field anywhere.

    sftlf is time-invariant and identical across experiments/members, so
    models that only publish it under piControl (e.g. UKESM) still resolve.
    """
    _, files = find(OI10_CMIP, model, "historical", member, "fx", "sftlf")
    if files:
        return files
    for grid in ("gn", "gr", "gr1"):
        pat = f"{OI10_CMIP}/*/{model}/*/*/fx/sftlf/{grid}/*/*.nc"
        uniq = {os.path.basename(p): os.path.realpath(p)
                for p in glob.iglob(pat) if os.path.isfile(p)}
        if uniq:
            return [uniq[b] for b in sorted(uniq)]
    return []


def make_regridder(ds_native):
    """Bilinear regridder from a native grid to a global 1x1 grid."""
    ds_out = xr.Dataset({
        'lat': (['lat'], np.arange(-89.5, 90.5, 1.0)),
        'lon': (['lon'], np.arange(0.5, 360.5, 1.0)),
    })
    return xe.Regridder(ds_native, ds_out, method='bilinear', periodic=True,
                        ignore_degenerate=True)


def to_degC(da):
    """Convert K -> degC if the units attribute says so."""
    u = str(da.attrs.get('units', '')).lower()
    return da - 273.15 if u in ('k', 'kelvin') else da


def blended_gmst(model, member):
    """Return the monthly blended GMST DataArray (degC) for one model."""
    tas = load_hist_ssp(model, member, "tas", "Amon").squeeze(drop=True)
    tos = load_hist_ssp(model, member, "tos", "Omon").squeeze(drop=True)

    lf = find_sftlf(model, member)
    if not lf:
        raise FileNotFoundError(f"no sftlf anywhere for {model}")
    sftlf = xr.open_dataset(lf[0])["sftlf"]

    # convert to degC BEFORE regridding: xesmf drops the units attribute,
    # so to_degC must see the native arrays or tas stays in Kelvin.
    tas = to_degC(tas)
    tos = to_degC(tos)

    # regrid to a common 1x1 grid (tas & sftlf share the atmosphere grid)
    rg_atmos = make_regridder(tas)
    rg_ocean = make_regridder(tos)
    tas_r = rg_atmos(tas)
    lf_r  = rg_atmos(sftlf).clip(0, 100) / 100.0
    tos_r = rg_ocean(tos)

    # Amon vs Omon timestamps can differ within a month -> force one time axis
    tos_r = tos_r.assign_coords(time=tas_r.time)

    # blend; land cells fall back to tas where SST is missing
    tos_filled = tos_r.where(np.isfinite(tos_r), tas_r)
    blend = lf_r * tas_r + (1.0 - lf_r) * tos_filled

    w = np.cos(np.deg2rad(blend.lat))
    gmst = blend.weighted(w).mean(("lat", "lon"))
    gmst.name = "gmst"
    gmst.attrs.update(units="degC",
                      long_name="blended global mean surface temperature",
                      description="f_land*tas + (1-f_land)*tos, cos-lat weighted",
                      source="historical + ssp585", model=model, member=member)
    return gmst.compute()


def build_dataset(period_means, members):
    """Assemble a (model x period) Dataset of absolute GMST + anomalies."""
    models  = list(period_means)
    periods = list(PERIODS)
    data = np.array([[period_means[m][p] for p in periods] for m in models])

    return xr.Dataset(
        data_vars={
            "gmst": (["model", "period"], data, {
                "units": "degC",
                "long_name": "absolute blended global mean surface temperature",
                "description": ("cos-latitude area-weighted global mean of "
                                "f_land*tas + (1-f_land)*tos, averaged over the period"),
                "cell_methods": "area: mean (cos-lat weighted) time: mean",
            }),
        },
        coords={
            "model":  ("model", models, {"long_name": "CMIP6 source model"}),
            "member": ("model", [members[m] for m in models],
                       {"long_name": "variant label (ripf)"}),
            "period": ("period", periods,
                       {"long_name": "averaging period (year range)"}),
            "period_start": ("period", [int(PERIODS[p][0]) for p in periods],
                             {"long_name": "period start year", "units": "year"}),
            "period_end":   ("period", [int(PERIODS[p][1]) for p in periods],
                             {"long_name": "period end year", "units": "year"}),
        },
        attrs={
            "title": "Absolute blended GMST from CMIP6 (historical + ssp585)",
            "summary": ("Blend of sea-surface temperature (tos) over ocean and "
                        "near-surface air temperature (tas) over land, weighted by "
                        "land-area fraction (sftlf), regridded bilinearly to a regular "
                        "1x1 grid and cos-latitude area-averaged to a global mean. "
                        "historical (1850-2014) is spliced with ssp585 (2015-) so the "
                        "1991-2020 window is covered."),
            "experiments": "historical + ssp585",
            "variables_used": "tas (Amon), tos (Omon), sftlf (fx)",
            "grid": "regular 1x1 degree; bilinear regrid via xesmf (ignore_degenerate)",
            "source": "CMIP6 replicas, NCI /g/data/oi10",
            "references": ("IPCC AR6 WG1; Copernicus C3S Global Climate Highlights 2023 "
                           "(https://climate.copernicus.eu/GCH2023-Paris-Agreement)"),
            "note": ("Absolute GMST retains each model's absolute bias (inter-model "
                     "spread ~1-2 degC); intended to be anchored to an observational "
                     "estimate for paleo / Paris Agreement comparison."),
        },
    )


def main():
    os.makedirs(OUT, exist_ok=True)
    period_means, members = {}, {}
    for model, member in MODELS.items():
        print(f"[{model}] computing ...", flush=True)
        try:
            gmst = blended_gmst(model, member)
        except Exception as e:
            print(f"[{model}] FAILED: {e}", flush=True)
            continue

        ncpath = os.path.join(OUT, f"gmst_monthly_{model}.nc")
        gmst.to_netcdf(ncpath)
        print(f"[{model}] wrote {ncpath}", flush=True)

        means = {name: float(gmst.sel(time=slice(y0, y1)).mean("time"))
                 for name, (y0, y1) in PERIODS.items()}
        period_means[model] = means
        members[model] = member
        line = "  ".join(f"{n}={means[n]:.3f}" for n in PERIODS)
        print(f"[{model}] {line}  degC", flush=True)

    if not period_means:
        print("no models succeeded; nothing to write")
        return

    ds = build_dataset(period_means, members)
    dspath = os.path.join(OUT, "gmst_blended_cmip6.nc")
    ds.to_netcdf(dspath)
    print(f"\nwrote {dspath}")
    print(ds)


if __name__ == "__main__":
    main()
