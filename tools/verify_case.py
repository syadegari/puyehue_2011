"""Check initial particles, weather time axes and satellite coverage. SPDX-License-Identifier: MIT"""
import csv
import json
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file

ROOT = Path(__file__).resolve().parents[1]


def verify_release(config, initial):
    release = config["release"]
    count, mass = release["particles"], release["total_mass_kg"]
    rows = np.loadtxt(initial, delimiter=",", skiprows=1)
    assert rows.shape == (count, 6) and np.isfinite(rows).all()
    np.testing.assert_array_equal(rows[:, 0], np.arange(count))
    np.testing.assert_array_equal(rows[:, 5], mass / count)
    np.testing.assert_allclose(rows[:, 4], release["surface_reference_hpa"] *
                               np.exp(-rows[:, 3] / release["scale_height_km"]), rtol=1e-9)
    np.testing.assert_allclose(rows[:, 5].sum(), mass)
    grid = config["output_grid"]
    lon_edges = np.linspace(grid["west_deg"], grid["east_deg"], grid["longitude_cells"] + 1)
    lat_edges = np.linspace(grid["south_deg"], grid["north_deg"], grid["latitude_cells"] + 1)
    initial_counts, _, _ = np.histogram2d(rows[:, 2], rows[:, 1], bins=(lat_edges, lon_edges))
    assert initial_counts.sum() == count
    print(f"{count:,} initial parcels inside the reporting grid, {mass:,} kg.")


def verify():
    verify_release(json.loads((ROOT / "case.json").read_text()), ROOT / "initial/particles.csv")
    verify_release(json.loads((ROOT / "small/case.json").read_text()), ROOT / "small/particles.csv")
    with netcdf_file(ROOT / "weather/transport.nc", mmap=False) as data:
        v = data.variables
        np.testing.assert_array_equal(v["time"][:], [0, 24, 48, 72])
        np.testing.assert_array_equal(v["longitude"][:], np.arange(0, 360, 3))
        np.testing.assert_array_equal(v["latitude"][:], np.arange(-90, 91, 3))
        assert len(v["pressure"][:]) == 59 and (np.diff(v["pressure"][:]) < 0).all()
        for name in ("u", "v", "omega", "temperature"):
            assert v[name].shape == (4, 59, 61, 120)
            assert np.isfinite(v[name][:, 32, 16:18, 95:98]).all()
    with netcdf_file(ROOT / "observations/aerosol_index.nc", mmap=False) as data:
        v = data.variables
        np.testing.assert_array_equal(v["day"][:], [0, 1, 2])
        valid = np.isfinite(v["absorbing_aerosol_index"][:])
        np.testing.assert_array_equal(valid, v["number_of_observations"][:] > 0)
        print("GOME-2A valid 1-degree cells per day:", valid.sum(axis=(1, 2)).tolist(), "of 7,500.")
    with netcdf_file(ROOT / "observations/seviri_visible_ash.nc", mmap=False) as data:
        v = data.variables
        np.testing.assert_array_equal(v["time"][:], [15, 39, 63])
        fraction = v["visible_ash_fraction"][:]
        assert fraction.shape == (3, 100, 300)
        assert np.nanmin(fraction) == 0 and np.nanmax(fraction) == 1
        outside = ((v["longitude"][:] < -75) | (v["longitude"][:] > -15))
        assert np.isnan(fraction[:, :, outside]).all()
        np.testing.assert_array_equal((fraction > 0).sum(axis=(1, 2)), [401, 876, 525])
    with (ROOT / "observations/seviri_centres.csv").open() as f:
        assert [int(row["model_hour"]) for row in csv.DictReader(f)] == [15, 39, 63]


if __name__ == "__main__":
    verify()
