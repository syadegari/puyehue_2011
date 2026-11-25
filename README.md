# Puyehue–Cordón Caulle ash transport starter

This offline case follows a single idealized puff from Chile across the South Atlantic from **5 June 2011 at 00:00 UTC to 8 June at 00:00 UTC**. It packages the weather, generated initial particles and satellite observations for building a transport solver. Start with the small case to check file parsing and integration, then use the full case for scaling and comparison.

| Case | Particles | Mass per parcel | Step length | Steps over 72 h |
|---|---:|---:|---:|---:|
| Small, in `small/` | 10,000 | 100,000 kg | 180 s | 1,440 |
| Full, in `initial/` | 100,000 | 10,000 kg | 10 s | 25,920 |

Each case starts with **1 billion kg** of tracer mass. All four daily weather snapshots, the solver-ready weather file and the satellite observations are included for offline use.

## License

The original software and documentation use the [MIT License](LICENSE). The case configurations and generated initial particles are available under CC0 1.0. The weather, SEVIRI figure and its adaptations use CC BY 4.0. The GOME-2A aerosol data and their regional subset use the ESA CCI Data Policy. When redistributing data, include the applicable attribution, change history and provider notices. [File-by-file terms and credits](SOURCES.md)

## Open the package

From this directory, run the following offline. The first command needs only coreutils. The numerical checks use Python, NumPy and SciPy, which are available on the described coding desktop. No C compiler, MPTRAC executable, native netCDF development package or OpenMP runtime is needed to read the prepared case.

```sh
sha256sum -c SHA256SUMS
python3 tools/verify_case.py
```

Open the [published satellite maps](observations/seviri_figure1.png). The left column shows the observed plume at hours 15, 39 and 63 in the first three rows. The fourth row in the published figure falls after the run ends.

| File | Contents and intended use |
|---|---|
| `case.json`, `small/case.json` | UTC bounds, physical release parameters, integrator step and output grid. |
| `initial/particles.csv`, `small/particles.csv` | Zero-based ID, longitude and latitude in degrees, pressure altitude in km, pressure in hPa and parcel mass in kg. All rows start at hour zero. |
| `weather/transport.nc` | Solver-ready winds, temperature and surface pressure. Four daily UTC snapshots cover both endpoints. |
| `weather/ei_*.nc` | Complete packed ERA-Interim source fields, including humidity and ancillary meteorological fields. |
| `observations/aerosol_index.nc` | Three daily observed UV aerosol-index fields, number of observations and solar zenith angle. A native 1° cell spans 2 × 2 of the output cells. |
| `observations/seviri_visible_ash.nc` | Three satellite footprint estimates digitized onto the model’s 0.5° grid. NaN identifies areas with no usable map pixels. |
| `observations/seviri_centres.csv` | Three approximate observed fine-ash mass centres, with UTC timestamps and corresponding hourly grid indices. |

The prepared numerical `.nc` files use classic NetCDF and can be read offline with SciPy. Source `.nc` files use NetCDF-4/HDF5. This example reads the eastward wind at the first time and the observed footprint at hour 39.

```python
from scipy.io import netcdf_file

with netcdf_file("weather/transport.nc", mmap=False) as f:
    u = f.variables["u"][0].copy()  # [pressure, latitude, longitude], m/s
with netcdf_file("observations/seviri_visible_ash.nc", mmap=False) as f:
    footprint = f.variables["visible_ash_fraction"][1].copy()  # second observation, hour 39
```

A C++ solver can use its own reader or the NetCDF C API. On a desktop with SciPy alone, `u.astype("<f4").tofile("u0.f32")` writes a contiguous little-endian float32 array that C++ can read directly. Its dimensions are 59 × 61 × 120 with longitude varying fastest.

## Release and weather methodology

The release is centred at **72.117°W, 40.59°S**, at a nominal 10 km pressure altitude. This is a simplified atmospheric transport experiment. The actual eruption had repeated emissions, and the single puff and assigned mass are experimental assumptions. Particle grain size, settling velocity, continuing emissions and deposition are outside this case.

The generator uses Python’s seeded `random.Random(20110605)` and three independent Gaussian draws per ID, in east, north, vertical order. Each horizontal full width at half maximum is 30 km. The vertical full width is 1 km in the linearized pressure perturbation. Divide each width by √(8 ln 2) to obtain its standard deviation. East and north distances are converted to degrees on a sphere of radius 6,367.421 km, using the cosine of the vent latitude for longitude. With scale height H = 7 km and reference pressure 1013.25 hPa, the generator computes the central pressure p₀ = 1013.25 exp(−10/H), applies p = p₀(1 − δz/H), then reports z = −H ln(p/1013.25). Each row has mass equal to total mass divided by particle count. Both sizes share the same sequence of positions for their first 10,000 IDs and use different parcel weights.

Recreate the canonical CSVs, or choose a different output filename to compare bytes. The code needs only the Python standard library.

```sh
python3 tools/generate_particles.py
python3 tools/generate_particles.py --case small/case.json --output small/particles.csv
```

The weather grid is global, 3° × 3°, with longitudes 0…357° east, latitudes −90…90°, and 59 descending pressure levels from 104,613 to 10 Pa. The compact file has `u` eastward and `v` northward in m/s, `omega` in Pa/s (positive toward higher pressure), temperature in K, and surface pressure in Pa. Its time axis is **hours** since release. The pressure coordinate uses **Pa**. Multiply the initial CSV’s hPa by 100. Unpacking masks source fill values before applying scale and offset. Missing values are NaN, particularly below terrain. Interpolate winds in space and between the two bracketing daily times, wrapping longitude at 360°. The 0.5° output grid is a reporting grid over 90°W–60°E and 65°S–15°S, with a single column from −5 to 85 km.

## How to compare a solver

1. Bin the supplied initial particles onto the 0.5° output grid and check that the counts and mass agree with your solver at time zero. Track total mass across all particles throughout the run and account for particles outside the reporting grid when integrating its column mass.
2. Check reproducibility by running the same release and random seed with one and four threads. Compare the solver's particle positions in ID order and its gridded outputs at matching times.
3. Compare observed ash position at **15:00 UTC on June 5, 6 and 7** against model hours **15, 39 and 63**. For a centre-of-mass diagnostic, restrict the model to the satellite panel (75°W–15°W, 55°S–20°S) and weight cells by column mass times area. The published map marks a 0.2 g/m² contour. The reported centres were read from the plotted X, linearly calibrated in longitude and interpolated between neighbouring labelled latitude ticks. Their one-decimal precision is approximate. The footprint file gives the fraction of usable plotted pixels coloured as ash in each model cell. White background counts as no visible signal. Blue annotations, dark neutral outlines and a small region around the vent marker are masked. NaN denotes no usable pixels. The three rasters support approximate shape comparisons. Colour quantization and plotting overlays limit their accuracy. For a thresholded overlap score, document your chosen visible-fraction threshold and model mass threshold and restrict the score to finite satellite cells.
4. Use the GOME-2A index to examine regional absorbing aerosol patterns. It is dimensionless and can also respond to dust and smoke. Compare on the native daily 1° grid, aggregate model output with area weights, and keep cells with zero observation count missing. Only 3,046, 3,049 and 3,006 of 7,500 regional cells have valid values on the three dates. A daily composite has no unique overpass time. The final model timestamp is midnight starting June 8, so a June 8 daily composite would be outside the run. No observed hourly quantitative ash-mass raster or individual observed parcel tracks are supplied.

## Reproducing the preparation

`python3 tools/prepare_fields.py` rebuilds the solver weather and regional aerosol subset from the packaged source files using h5py, NumPy and SciPy. `python3 tools/digitize_seviri.py` rebuilds the mapped footprint and centre CSV using Pillow, NumPy and SciPy. The full data lineage and redistribution notices are in [SOURCES.md](SOURCES.md).
